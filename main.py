#!/usr/bin/env python3
import argparse
import logging
import sys
import time
from pathlib import Path
from typing import Any

from src.chunker import ChunkingError, chunk_document
from src.config import config
from src.embedder import EmbeddingError, generate_embeddings
from src.pdf_processor import PDFConversionError, convert_pdf
from src.qdrant_manager import QdrantError, QdrantManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)


def print_stage(stage_num: int, total_stages: int, description: str) -> None:
    print(f"[{stage_num}/{total_stages}] {description}...")


def print_success(message: str, elapsed_time: float) -> None:
    print(f"{message} ({elapsed_time:.1f}s)")


def print_summary(stats: dict[str, Any]) -> None:
    print("Processing Summary:")
    print(f"  Source:        {stats['source']}")
    print(f"  Chunks:        {stats['chunks']}")
    print(f"  Vectors:       {stats['vectors']}")
    print(f"  Stored:        {stats['stored']}")
    print(f"  Collection:    {stats['collection']}")
    print(f"  Total Points:  {stats['total_points']}")
    print(f"  Total Time:    {stats['total_time']:.1f}s")
    print(f"  Status:        {stats['status']}")


def process_pdf_file(pdf_path: Path) -> dict[str, Any]:
    start_time = time.time()
    stats: dict[str, Any] = {
        "source": pdf_path.name,
        "status": "FAILED",
    }

    # Stage 1: PDF Conversion
    print_stage(1, 4, "Converting PDF to structured document")
    stage_start = time.time()
    document = convert_pdf(pdf_path)
    stage_time = time.time() - stage_start
    print_success("Conversion complete", stage_time)

    # Stage 2: Chunking
    print_stage(2, 4, "Chunking document into semantic segments")
    stage_start = time.time()
    chunks = chunk_document(document, pdf_path.name)
    stage_time = time.time() - stage_start
    print_success(f"Created {len(chunks)} chunks", stage_time)

    if not chunks:
        raise ValueError("No chunks were generated from document")

    # Stage 3: Embedding
    print_stage(3, 4, f"Generating embeddings for {len(chunks)} chunks")
    stage_start = time.time()
    texts = [chunk["text"] for chunk in chunks]
    embeddings = generate_embeddings(texts, show_progress=config.embedding.show_progress)
    stage_time = time.time() - stage_start
    print_success(f"Generated {len(embeddings)} embeddings", stage_time)

    # Stage 4: Storage
    print_stage(4, 4, "Storing vectors in Qdrant")
    stage_start = time.time()
    manager = QdrantManager()
    manager.initialize_collection()
    stored_count = manager.upsert_points(chunks, embeddings)
    collection_info = manager.get_collection_info()
    stage_time = time.time() - stage_start
    print_success(f"Stored {stored_count} points", stage_time)

    total_time = time.time() - start_time

    stats.update(
        {
            "chunks": len(chunks),
            "vectors": len(embeddings),
            "stored": stored_count,
            "collection": collection_info["name"],
            "total_points": collection_info["points_count"],
            "total_time": total_time,
            "status": "SUCCESS",
        }
    )

    return stats


def main() -> None:
    parser = argparse.ArgumentParser(
        description="PDF to Vector Database Pipeline - Convert PDFs to searchable vector embeddings",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s document.pdf
  %(prog)s data/input/research_paper.pdf --verbose
  %(prog)s /path/to/file.pdf -v
        """,
    )

    parser.add_argument("pdf_path", type=Path, help="Path to PDF file to process")
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output with detailed logging",
    )

    args = parser.parse_args()

    config.ensure_directories()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        config.processing.verbose = True

    if not args.pdf_path.exists():
        logging.error(f"File not found: {args.pdf_path}")
        sys.exit(1)

    if not args.pdf_path.is_file():
        logging.error(f"Path is not a file: {args.pdf_path}")
        sys.exit(1)

    if args.pdf_path.suffix.lower() != ".pdf":
        logging.error(f"File is not a PDF: {args.pdf_path} (extension: {args.pdf_path.suffix})")
        sys.exit(1)

    print(f"Processing PDF: {args.pdf_path}")

    try:
        stats = process_pdf_file(args.pdf_path)
        print_summary(stats)
        sys.exit(0)

    except PDFConversionError as e:
        logging.error(f"PDF conversion failed: {e}")
        logging.debug("Full traceback:", exc_info=True)
        sys.exit(2)

    except ChunkingError as e:
        logging.error(f"Document chunking failed: {e}")
        logging.debug("Full traceback:", exc_info=True)
        sys.exit(3)

    except EmbeddingError as e:
        logging.error(f"Embedding generation failed: {e}")
        logging.debug("Full traceback:", exc_info=True)
        sys.exit(4)

    except QdrantError as e:
        logging.error(f"Qdrant database operation failed: {e}")
        logging.info("Ensure Qdrant is running: ./setup.sh")
        logging.debug("Full traceback:", exc_info=True)
        sys.exit(5)

    except ValueError as e:
        logging.error(f"Validation error: {e}")
        logging.debug("Full traceback:", exc_info=True)
        sys.exit(6)

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(130)

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        logging.debug("Full traceback:", exc_info=True)
        sys.exit(99)


if __name__ == "__main__":
    main()

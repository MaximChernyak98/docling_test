"""Document chunking module for semantic segmentation.

This module handles document chunking using Docling Core's HybridChunker.
It creates semantically meaningful chunks with configurable size and overlap,
preserving document structure and extracting metadata for each chunk.
"""

from typing import Any

from docling_core.transforms.chunker import HybridChunker
from docling_core.transforms.chunker.tokenizer import HuggingFaceTokenizer
from docling_core.types.doc import DoclingDocument

from src.config import config


class ChunkingError(Exception):
    """Raised when document chunking fails."""

    pass


def create_chunker() -> HybridChunker:
    """Create a configured HybridChunker instance.

    Returns:
        Configured HybridChunker with tokenizer settings from config.

    Raises:
        ChunkingError: If chunker initialization fails.
    """
    try:
        tokenizer = HuggingFaceTokenizer.from_pretrained(
            model_name=config.embedding.model_name, max_tokens=config.chunking.target_chunk_size
        )

        chunker = HybridChunker(tokenizer=tokenizer, merge_peers=True)

        return chunker

    except Exception as e:
        raise ChunkingError(f"Failed to initialize chunker: {e}") from e


def chunk_document(document: DoclingDocument, source_file: str) -> list[dict[str, Any]]:
    """Chunk a DoclingDocument into semantic segments with metadata.

    Args:
        document: The DoclingDocument to chunk.
        source_file: Name of the source file (for metadata).

    Returns:
        List of chunk dictionaries, each containing:
            - text: Chunk text content
            - source_file: Source filename
            - chunk_index: Sequential chunk number
            - heading_context: Hierarchical heading path
            - content_type: Type of content (text/table/list)
            - page_number: Page number (if available from provenance)

    Raises:
        ChunkingError: If chunking fails.
    """
    if not isinstance(document, DoclingDocument):
        raise ValueError("document must be a DoclingDocument instance")

    try:
        chunker = create_chunker()
        chunks = list(chunker.chunk(dl_doc=document))

        chunk_dicts = []
        for idx, chunk in enumerate(chunks):
            # Extract page number from provenance if available
            page_number = None
            if chunk.meta.doc_items:
                # Get the first doc item and check for provenance
                first_item = chunk.meta.doc_items[0]
                if hasattr(first_item, "prov") and first_item.prov:
                    page_number = first_item.prov[0].page

            # Build heading context as a path
            heading_context = " > ".join(chunk.meta.headings) if chunk.meta.headings else ""

            # Determine content type based on doc items
            content_type = _infer_content_type(chunk)

            chunk_dict = {
                "text": chunk.text,
                "source_file": source_file,
                "chunk_index": idx,
                "heading_context": heading_context,
                "content_type": content_type,
                "page_number": page_number,
            }

            chunk_dicts.append(chunk_dict)

        return chunk_dicts

    except Exception as e:
        if isinstance(e, (ValueError, ChunkingError)):
            raise
        raise ChunkingError(f"Failed to chunk document: {e}") from e


def _infer_content_type(chunk: Any) -> str:
    """Infer content type from chunk metadata.

    Args:
        chunk: The chunk object with metadata.

    Returns:
        Content type string: 'table', 'list', or 'text'.
    """
    if not chunk.meta.doc_items:
        return "text"

    # Check labels of doc items to infer type
    labels = []
    for item in chunk.meta.doc_items:
        if hasattr(item, "label"):
            labels.append(str(item.label).lower())

    # Determine primary content type
    if any("table" in label for label in labels):
        return "table"
    if any("list" in label for label in labels):
        return "list"

    return "text"

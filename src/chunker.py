from typing import Any

from docling_core.transforms.chunker import HybridChunker
from docling_core.transforms.chunker.tokenizer import HuggingFaceTokenizer
from docling_core.types.doc import DoclingDocument

from src.config import config


class ChunkingError(Exception):
    pass


def create_chunker() -> HybridChunker:
    try:
        tokenizer = HuggingFaceTokenizer.from_pretrained(
            model_name=config.embedding.model_name, max_tokens=config.chunking.target_chunk_size
        )
        chunker = HybridChunker(tokenizer=tokenizer, merge_peers=True)
        return chunker
    except Exception as e:
        raise ChunkingError(f"Failed to initialize chunker: {e}") from e


def chunk_document(document: DoclingDocument, source_file: str) -> list[dict[str, Any]]:
    if not isinstance(document, DoclingDocument):
        raise ValueError("document must be a DoclingDocument instance")

    try:
        chunker = create_chunker()
        chunks = list(chunker.chunk(dl_doc=document))

        chunk_dicts = []
        for idx, chunk in enumerate(chunks):
            page_number = None
            if chunk.meta.doc_items:
                first_item = chunk.meta.doc_items[0]
                if hasattr(first_item, "prov") and first_item.prov:
                    page_number = first_item.prov[0].page

            heading_context = " > ".join(chunk.meta.headings) if chunk.meta.headings else ""
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
    if not chunk.meta.doc_items:
        return "text"

    labels = []
    for item in chunk.meta.doc_items:
        if hasattr(item, "label"):
            labels.append(str(item.label).lower())

    if any("table" in label for label in labels):
        return "table"
    if any("list" in label for label in labels):
        return "list"

    return "text"

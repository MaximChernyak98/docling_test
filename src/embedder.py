from typing import Any

import numpy as np
from sentence_transformers import SentenceTransformer

from .config import config


class EmbeddingError(Exception):
    pass


# Model cache to avoid reloading
_model_cache: SentenceTransformer | None = None


def load_model(model_name: str | None = None, device: str | None = None) -> SentenceTransformer:
    global _model_cache

    if _model_cache is not None:
        return _model_cache

    model_name = model_name or config.embedding.model_name
    device = device or config.embedding.device

    try:
        _model_cache = SentenceTransformer(model_name, device=device)
        return _model_cache
    except Exception as e:
        raise EmbeddingError(f"Failed to load embedding model '{model_name}': {e}") from e


def generate_embeddings(texts: list[str], show_progress: bool | None = None) -> np.ndarray:
    if not texts:
        raise ValueError("Cannot generate embeddings for empty text list")

    if show_progress is None:
        show_progress = config.embedding.show_progress

    try:
        model = load_model()

        embeddings = model.encode(
            texts,
            batch_size=config.embedding.batch_size,
            show_progress_bar=show_progress,
            normalize_embeddings=config.embedding.normalize_embeddings,
        )

        return np.array(embeddings)

    except Exception as e:
        raise EmbeddingError(f"Failed to generate embeddings: {e}") from e


def generate_single_embedding(text: str) -> np.ndarray:
    if not text:
        raise ValueError("Cannot generate embedding for empty text")

    embeddings = generate_embeddings([text], show_progress=False)
    return embeddings[0]

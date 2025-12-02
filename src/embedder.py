"""Embedding generation module for creating vector representations.

This module handles embedding generation using Sentence Transformers.
Uses the all-MiniLM-L6-v2 model for efficient semantic embeddings.
"""

from typing import Any

import numpy as np
from sentence_transformers import SentenceTransformer

from .config import config


class EmbeddingError(Exception):
    """Custom exception for embedding generation errors."""


# Model cache to avoid reloading
_model_cache: SentenceTransformer | None = None


def load_model(model_name: str | None = None, device: str | None = None) -> SentenceTransformer:
    """Load the sentence transformer model with caching.

    Args:
        model_name: Model identifier (default from config)
        device: Device to use ('cpu', 'cuda', 'mps') (default from config)

    Returns:
        Loaded SentenceTransformer model

    Raises:
        EmbeddingError: If model loading fails
    """
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
    """Generate embeddings for a list of texts with batch processing.

    Args:
        texts: List of text strings to embed
        show_progress: Show progress bar (default from config)

    Returns:
        Numpy array of shape (len(texts), 384) with L2-normalized embeddings

    Raises:
        EmbeddingError: If embedding generation fails
        ValueError: If texts list is empty
    """
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
    """Generate embedding for a single text string.

    Args:
        text: Text string to embed

    Returns:
        Numpy array of shape (384,) with L2-normalized embedding

    Raises:
        EmbeddingError: If embedding generation fails
    """
    if not text:
        raise ValueError("Cannot generate embedding for empty text")

    embeddings = generate_embeddings([text], show_progress=False)
    return embeddings[0]

"""Qdrant database manager for vector storage and retrieval.

This module handles all Qdrant vector database operations including
collection management, point insertion, and similarity search.
"""

from typing import Any
from uuid import uuid4

import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from .config import Config, config as default_config


class QdrantError(Exception):
    """Custom exception for Qdrant operations errors."""


class QdrantManager:
    """Manager for Qdrant vector database operations."""

    def __init__(self, config: Config | None = None) -> None:
        """Initialize Qdrant manager with configuration.

        Args:
            config: Configuration object (uses default if None)

        Raises:
            QdrantError: If connection to Qdrant fails
        """
        self.config = config or default_config

        try:
            self.client = QdrantClient(
                host=self.config.qdrant.host,
                port=self.config.qdrant.http_port,
                timeout=self.config.qdrant.timeout,
            )
        except Exception as e:
            raise QdrantError(f"Failed to connect to Qdrant at {self.config.qdrant_url}: {e}") from e

        self.collection_name = self.config.qdrant.collection_name
        self.vector_size = self.config.embedding.vector_dimensions

    def collection_exists(self) -> bool:
        """Check if the collection exists.

        Returns:
            True if collection exists, False otherwise
        """
        try:
            collections = self.client.get_collections().collections
            return any(c.name == self.collection_name for c in collections)
        except Exception:
            return False

    def initialize_collection(self) -> None:
        """Create the collection if it doesn't exist.

        Creates a collection with vector parameters matching the embedding configuration.

        Raises:
            QdrantError: If collection creation fails
        """
        if self.collection_exists():
            return

        try:
            distance_metric = Distance[self.config.qdrant.distance_metric.upper()]

            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=self.vector_size, distance=distance_metric),
                on_disk_payload=self.config.qdrant.on_disk_payload,
            )
        except Exception as e:
            raise QdrantError(f"Failed to create collection '{self.collection_name}': {e}") from e

    def upsert_points(self, chunks: list[dict[str, Any]], embeddings: np.ndarray) -> int:
        """Insert or update points in the collection.

        Args:
            chunks: List of chunk dictionaries with metadata
            embeddings: Numpy array of embeddings, shape (len(chunks), vector_size)

        Returns:
            Number of points upserted

        Raises:
            QdrantError: If upsert operation fails
            ValueError: If chunks and embeddings length mismatch or empty
        """
        if not chunks or len(embeddings) == 0:
            raise ValueError("Cannot upsert empty chunks or embeddings")

        if len(chunks) != len(embeddings):
            raise ValueError(f"Chunks count ({len(chunks)}) must match embeddings count ({len(embeddings)})")

        if embeddings.shape[1] != self.vector_size:
            raise ValueError(f"Embedding dimension ({embeddings.shape[1]}) must match config ({self.vector_size})")

        try:
            points = []
            for chunk, embedding in zip(chunks, embeddings):
                point = PointStruct(
                    id=str(uuid4()),
                    vector=embedding.tolist(),
                    payload={
                        "text": chunk.get("text", ""),
                        "source_file": chunk.get("source_file", ""),
                        "chunk_index": chunk.get("chunk_index", 0),
                        "heading_context": chunk.get("heading_context", ""),
                        "content_type": chunk.get("content_type", "text"),
                        "page_number": chunk.get("page_number"),
                    },
                )
                points.append(point)

            self.client.upsert(collection_name=self.collection_name, points=points)

            return len(points)

        except Exception as e:
            raise QdrantError(f"Failed to upsert points: {e}") from e

    def search(self, query_vector: np.ndarray, limit: int = 10) -> list[dict[str, Any]]:
        """Search for similar vectors in the collection.

        Args:
            query_vector: Query embedding vector, shape (vector_size,)
            limit: Maximum number of results to return

        Returns:
            List of search results with scores and payloads

        Raises:
            QdrantError: If search operation fails
            ValueError: If query vector has wrong dimensions
        """
        if query_vector.shape[0] != self.vector_size:
            raise ValueError(f"Query vector dimension ({query_vector.shape[0]}) must match config ({self.vector_size})")

        try:
            response = self.client.query_points(
                collection_name=self.collection_name, query=query_vector.tolist(), limit=limit
            )

            return [
                {
                    "id": result.id,
                    "score": result.score,
                    "payload": result.payload,
                }
                for result in response.points
            ]

        except Exception as e:
            raise QdrantError(f"Search failed: {e}") from e

    def get_collection_info(self) -> dict[str, Any]:
        """Get information about the collection.

        Returns:
            Dictionary with collection statistics

        Raises:
            QdrantError: If collection info retrieval fails
        """
        try:
            info = self.client.get_collection(collection_name=self.collection_name)

            return {
                "name": self.collection_name,
                "indexed_vectors_count": info.indexed_vectors_count,
                "points_count": info.points_count,
                "status": info.status.value,
                "vector_size": self.vector_size,
            }

        except Exception as e:
            raise QdrantError(f"Failed to get collection info: {e}") from e

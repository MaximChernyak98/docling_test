from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field


class PDFProcessingConfig(BaseModel):
    ocr_enabled: bool = Field(default=False, description="Enable OCR for scanned PDFs (not supported in v1)")
    extract_images: bool = Field(default=False, description="Extract images from PDFs")
    page_limit: int | None = Field(default=None, description="Maximum pages to process (None = all)")


class ChunkingConfig(BaseModel):
    target_chunk_size: int = Field(default=512, description="Target chunk size in tokens")
    chunk_overlap: int = Field(default=50, description="Overlap between chunks in tokens")
    table_format: Literal["markdown", "html"] = Field(default="markdown", description="Table serialization format")
    keep_tables_intact: bool = Field(default=True, description="Try to keep tables in single chunks")
    include_heading_context: bool = Field(default=True, description="Include heading hierarchy in chunks")


class EmbeddingConfig(BaseModel):
    model_name: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2", description="Sentence transformer model name"
    )
    vector_dimensions: int = Field(default=384, description="Embedding vector dimensions")
    batch_size: int = Field(default=32, description="Batch size for embedding generation")
    device: Literal["cpu", "cuda", "mps"] = Field(default="cpu", description="Device for model inference")
    normalize_embeddings: bool = Field(default=True, description="L2 normalize embeddings")
    show_progress: bool = Field(default=True, description="Show progress bar during embedding")


class QdrantConfig(BaseModel):
    host: str = Field(default="localhost", description="Qdrant host")
    http_port: int = Field(default=6333, description="Qdrant HTTP API port")
    grpc_port: int = Field(default=6334, description="Qdrant gRPC API port")
    storage_path: Path = Field(default=Path("./qdrant_storage"), description="Local storage path for Qdrant")
    collection_name: str = Field(default="pdf_documents", description="Name of the vector collection")
    distance_metric: Literal["Cosine", "Euclid", "Dot"] = Field(
        default="Cosine", description="Vector distance metric"
    )
    on_disk_payload: bool = Field(default=True, description="Store payload on disk")
    timeout: int = Field(default=60, description="Request timeout in seconds")


class PathsConfig(BaseModel):
    input_dir: Path = Field(default=Path("./data/input"), description="Directory for input PDF files")
    logs_dir: Path = Field(default=Path("./logs"), description="Directory for log files")
    cache_dir: Path | None = Field(default=None, description="Cache directory (None = use default)")


class ProcessingConfig(BaseModel):
    verbose: bool = Field(default=True, description="Enable verbose output")
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(default="INFO", description="Logging level")
    max_retries: int = Field(default=3, description="Maximum retries for failed operations")
    retry_delay: int = Field(default=2, description="Delay between retries in seconds")


class Config(BaseModel):
    pdf_processing: PDFProcessingConfig = Field(default_factory=PDFProcessingConfig)
    chunking: ChunkingConfig = Field(default_factory=ChunkingConfig)
    embedding: EmbeddingConfig = Field(default_factory=EmbeddingConfig)
    qdrant: QdrantConfig = Field(default_factory=QdrantConfig)
    paths: PathsConfig = Field(default_factory=PathsConfig)
    processing: ProcessingConfig = Field(default_factory=ProcessingConfig)

    def ensure_directories(self) -> None:
        self.paths.input_dir.mkdir(parents=True, exist_ok=True)
        self.paths.logs_dir.mkdir(parents=True, exist_ok=True)
        self.qdrant.storage_path.mkdir(parents=True, exist_ok=True)

    @property
    def qdrant_url(self) -> str:
        return f"http://{self.qdrant.host}:{self.qdrant.http_port}"


# Default configuration instance
config = Config()

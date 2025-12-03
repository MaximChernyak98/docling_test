# Project Description

## Overview

This is a **PDF to Markdown Converter with Semantic Search** system - a pipeline that transforms PDF documents into searchable knowledge bases using vector embeddings. The system preserves document structure while enabling semantic search capabilities through Retrieval Augmented Generation (RAG).

**Primary Purpose**: Convert PDFs to structured markdown, chunk them intelligently, generate vector embeddings, and store in a vector database for semantic search.

**Main Use Case**: Enable semantic search and RAG over PDF document collections by understanding meaning rather than just keyword matching.

---

## System Architecture

The system follows a **4-stage pipeline architecture**:

```
┌────────────┐      ┌────────────┐      ┌────────────┐      ┌────────────┐
│    PDF     │──────│  Markdown  │──────│   Chunks   │──────│  Vectors   │
│ Document   │      │  Document  │      │ + Metadata │      │ + Storage  │
└────────────┘      └────────────┘      └────────────┘      └────────────┘
     │                    │                    │                    │
[Conversion]         [Chunking]          [Embedding]          [Storage]
  Service              Service             Service             Service
```

**Data Flow**:
1. **PDF → Markdown**: Structure-preserving conversion (tables, headings, lists)
2. **Markdown → Chunks**: Semantic segmentation with context preservation
3. **Chunks → Vectors**: Generate 384-dimensional embeddings
4. **Vectors → Database**: Store with metadata for similarity search

---

## Core Components

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Conversion Service** | Docling | Converts PDF to structured markdown, preserves tables and hierarchy |
| **Chunking Service** | Docling Core | Splits documents at semantic boundaries, maintains context |
| **Embedding Service** | Sentence Transformers | Generates vector representations (all-MiniLM-L6-v2, 384-dim) |
| **Storage Service** | Qdrant | Vector database for similarity search with metadata |

---

## Technology Stack

**Core Libraries**:
- **docling** (1.0.0+): PDF processing with structure preservation
- **docling-core** (1.0.0+): Semantic document chunking
- **sentence-transformers** (2.2.0+): Text embedding generation
- **qdrant-client** (1.7.0+): Vector database client
- **pydantic** (2.0.0+): Configuration validation

**Infrastructure**:
- **Docker Compose**: Containerized Qdrant vector database
- **Python**: 3.9-3.12
- **Embedding Model**: all-MiniLM-L6-v2 (80MB, 384 dimensions)

**Runtime**:
- Local development environment
- Persistent vector storage on disk
- CPU-based processing (GPU optional for speed)

---

## Data Pipeline Details

**Stage 1: PDF Ingestion**
- Input: PDF file path
- Process: Document parsing, layout analysis, structure extraction
- Output: Structured document object + Markdown string

**Stage 2: Semantic Chunking**
- Input: Document object + Markdown
- Process: Hierarchical chunking at semantic boundaries
- Parameters: 512 token target, 50 token overlap
- Output: List of chunks with metadata (page, heading context, content type)

**Stage 3: Vector Generation**
- Input: Text chunks
- Process: Batch embedding generation, L2 normalization
- Parameters: 384-dimensional vectors, cosine similarity metric
- Output: Normalized vector embeddings

**Stage 4: Storage**
- Input: Vectors + metadata
- Process: Upsert to Qdrant collection
- Parameters: Collection name, distance metric (cosine)
- Output: Searchable vector database

---

## Project Structure

```
docling_test/
├── src/
│   ├── config.py              # Configuration management
│   ├── pdf_processor.py       # Conversion service
│   ├── chunking.py            # Chunking service
│   ├── embedding.py           # Embedding service
│   ├── qdrant_manager.py      # Storage service
│   └── main.py                # Pipeline orchestration
├── docker-compose.yml          # Qdrant vector database
├── setup.sh                   # Start infrastructure
├── teardown.sh                # Stop infrastructure
├── requirements.txt           # Python dependencies
├── data/
│   └── pdfs/                  # Input PDF files
├── qdrant_storage/            # Vector DB persistence
└── documentation/             # Detailed specs and architecture
```

**Key Modules**:
- **config.py**: Centralized configuration (chunk size, model name, paths)
- **pdf_processor.py**: PDF to markdown conversion logic
- **chunking.py**: Semantic segmentation with metadata enrichment
- **embedding.py**: Batch embedding generation
- **qdrant_manager.py**: Vector DB operations (create, upsert, search)
- **main.py**: End-to-end pipeline orchestration

---

## Key Configuration

**Chunking Configuration**:
- Chunk size: 512 tokens (configurable)
- Overlap: 50 tokens (configurable)
- Table serialization: Markdown format
- Strategy: Hierarchical/hybrid chunking

**Embedding Configuration**:
- Model: sentence-transformers/all-MiniLM-L6-v2
- Dimensions: 384
- Batch size: 32 chunks
- Device: CPU (default) or CUDA
- Distance metric: Cosine similarity

**Storage Configuration**:
- Database: Qdrant (local)
- Storage path: ./qdrant_storage
- Collection name: pdf_documents (configurable)
- Persistence: On-disk with payload storage

**Docker Services**:
- Qdrant container ports: 6333 (HTTP), 6334 (gRPC)
- Persistent volume for data retention
- Health checks for service readiness

---

## Important Notes

**Processing Characteristics**:
- Single PDF processing (v1 scope)
- Text-based PDFs only (no OCR)
- Local processing (no external API calls except model downloads)
- Sequential pipeline execution
- Progress tracking per stage

**Data Handling**:
- Each chunk carries: source file, page number, heading context, content type, markdown text
- Chunks are self-contained with preserved context
- Tables kept intact when size permits
- Images excluded from processing

**Performance Expectations**:
- PDF conversion: 1-5 seconds per page (complexity dependent)
- Chunking: <1 second for typical documents
- Embedding: ~500-1000 chunks/minute (CPU)
- Search: Sub-second for typical collections

---

## References

For detailed information, see:
- **documentation/PRD.md**: Product requirements and vision
- **documentation/architecture.md**: Detailed architecture and design rationale
- **documentation/technical-specifications.md**: Complete technical specs, versions, benchmarks
- **documentation/implementation-plan.md**: Development roadmap

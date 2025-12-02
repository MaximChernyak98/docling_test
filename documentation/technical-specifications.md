# Technical Specifications

**Project**: PDF to Markdown Converter with Semantic Search
**Version**: 2.0
**Date**: 2025-12-02

---

## 1. System Requirements

### 1.1 Hardware Requirements

**Minimum Specifications**:
- **CPU**: Modern multi-core processor (2+ cores)
- **RAM**: 4GB minimum
- **Storage**: 2GB free space
  - 500MB for models
  - 500MB for vector database
  - 1GB for working space

**Recommended Specifications**:
- **CPU**: 4+ cores for faster processing
- **RAM**: 8GB for large documents
- **Storage**: 5GB+ for multiple documents
- **GPU**: Optional, speeds up embedding generation

### 1.2 Software Requirements

**Operating System**:
- Linux (Ubuntu 20.04+, Debian, CentOS)
- macOS (11.0+)
- Windows (10/11 with WSL2 for Docker)

**Runtime Environment**:
- Python 3.9, 3.10, 3.11, or 3.12
- Docker Engine 20.10+
- Docker Compose 2.0+

---

## 2. Python Dependencies

### 2.1 Core Libraries

**PDF Processing**:
- **Package**: docling
- **Minimum Version**: 1.0.0
- **Purpose**: PDF to markdown conversion with structure preservation
- **Size**: ~50MB with dependencies

**Chunking Framework**:
- **Package**: docling-core
- **Minimum Version**: 1.0.0
- **Purpose**: Semantic document segmentation
- **Size**: ~5MB

**Vector Database Client**:
- **Package**: qdrant-client
- **Minimum Version**: 1.7.0
- **Purpose**: Interface to Qdrant vector database
- **Size**: ~10MB

**Embedding Generation**:
- **Package**: sentence-transformers
- **Minimum Version**: 2.2.0
- **Purpose**: Generate text embeddings
- **Size**: ~100MB
- **Note**: Downloads model on first use (~80MB additional)

### 2.2 Supporting Libraries

**Numerical Operations**:
- **Package**: numpy
- **Minimum Version**: 1.24.0
- **Purpose**: Array operations and vector manipulation
- **Size**: ~15MB

**Data Validation**:
- **Package**: pydantic
- **Minimum Version**: 2.0.0
- **Purpose**: Configuration and data validation
- **Size**: ~5MB

**Optional Dependencies**:
- **Package**: torch (automatically installed with sentence-transformers)
- **Note**: CPU-only version sufficient for prototype

---

## 3. Docker Infrastructure

### 3.1 Qdrant Vector Database

**Container Specifications**:
- **Image**: qdrant/qdrant
- **Recommended Version**: latest stable
- **Ports**: 6333 (HTTP), 6334 (gRPC)
- **Storage**: Persistent volume mount required
- **Memory**: 512MB minimum, 1GB recommended

**Volume Configuration**:
- **Purpose**: Persist vector data across restarts
- **Mount Point**: Container data directory
- **Host Path**: Configurable local directory

**Network Configuration**:
- **Mode**: Bridge network for service isolation
- **Access**: Localhost access from Python application

### 3.2 Docker Compose Configuration

**Service Definitions**:
- Qdrant vector database service
- Persistent volume definitions
- Network definitions
- Health check configurations

**Startup Dependencies**:
- Database must be ready before application runs
- Health checks ensure service availability

---

## 4. Embedding Model Specifications

### 4.1 Recommended Model

**Model Identifier**: sentence-transformers/all-MiniLM-L6-v2

**Model Characteristics**:
- **Type**: Sentence transformer (BERT-based)
- **Vector Dimensions**: 384
- **Model Size**: ~80MB
- **Performance**: ~3000 sentences/second (CPU)
- **Quality**: Good balance for semantic search

**Technical Details**:
- **Max Sequence Length**: 256 tokens
- **Tokenizer**: BERT WordPiece
- **Normalization**: L2 normalized embeddings
- **Training**: Trained on sentence similarity tasks

### 4.2 Alternative Models

**For Higher Quality** (slower, larger):
- all-mpnet-base-v2 (768 dimensions)
- all-distilroberta-v1 (768 dimensions)

**For Faster Processing** (lower quality):
- all-MiniLM-L12-v2 (384 dimensions, faster)
- paraphrase-MiniLM-L3-v2 (384 dimensions, fastest)

**Multilingual Options**:
- paraphrase-multilingual-MiniLM-L12-v2
- distiluse-base-multilingual-cased-v2

---

## 5. Qdrant Database Configuration

### 5.1 Collection Settings

**Vector Configuration**:
- **Size**: 384 dimensions (matches embedding model)
- **Distance Metric**: Cosine
  - Range: -1 to 1 (higher = more similar)
  - Normalized vectors recommended

**Storage Options**:
- **In-Memory**: Fast, volatile (development)
- **On-Disk**: Slower, persistent (production)
- **Hybrid**: Hot data in memory, cold on disk

**Performance Settings**:
- **Index Type**: HNSW (Hierarchical Navigable Small World)
- **M Parameter**: 16 (connectivity, default)
- **EF Construction**: 100 (build quality, default)

### 5.2 Point Structure

**Vector Point Components**:
- **ID**: Unique identifier (UUID or sequential integer)
- **Vector**: 384-dimensional float array
- **Payload**: JSON object with metadata

**Payload Schema**:
- source_file: string (filename)
- page_number: integer
- chunk_index: integer (sequential)
- heading_context: string (parent headings)
- content_type: string (text/table/list)
- text: string (markdown content)

---

## 6. Chunking Configuration

### 6.1 Chunking Strategy

**Approach**: Hierarchical/Hybrid chunking

**Strategy Details**:
- **Hierarchy-Aware**: Respects document structure
- **Semantic Boundaries**: Splits at logical points
- **Context Preservation**: Includes heading context
- **Table Handling**: Serializes as markdown

### 6.2 Chunking Parameters

**Size Parameters**:
- **Target Chunk Size**: 512 tokens (configurable)
  - Approximately 380-400 words
  - Good balance for search quality

- **Chunk Overlap**: 50 tokens (configurable)
  - Approximately 35-40 words
  - Prevents context loss at boundaries

**Table Handling**:
- **Serialization Format**: Markdown tables
- **Size Strategy**: Keep intact if under size limit
- **Splitting**: Split large tables by rows if necessary

**Image Handling**:
- **Strategy**: Exclude images from chunks
- **Placeholder**: Empty string
- **Future**: Could add image descriptions

---

## 7. Processing Pipeline Parameters

### 7.1 PDF Conversion Settings

**Document Converter Options**:
- **Format**: Standard PDF processing
- **OCR**: Disabled (v1 limitation)
- **Page Limit**: None (process all pages)
- **Image Extraction**: Disabled

**Output Format**:
- **Primary**: Markdown string
- **Structure**: Preserve headings, lists, tables
- **Metadata**: Page numbers, element types

### 7.2 Embedding Generation Settings

**Processing Parameters**:
- **Batch Size**: 32 chunks per batch
  - Balance between memory and speed
  - Adjust based on available RAM

- **Device**: CPU (default) or CUDA
  - GPU significantly faster if available
  - CPU sufficient for prototypes

- **Normalization**: L2 normalization
  - Required for cosine similarity
  - Built into model output

### 7.3 Storage Settings

**Database Connection**:
- **Mode**: Local file-based storage
- **Path**: ./qdrant_storage (configurable)
- **Timeout**: 60 seconds for operations

**Collection Parameters**:
- **Name**: pdf_documents (configurable)
- **On-Disk Payload**: True (for large collections)
- **Replication**: Single instance (local)

---

## 8. File and Directory Structure

### 8.1 Project Organization

**Python Modules**:
- Configuration module
- PDF processor module
- Chunking module
- Embedding module
- Qdrant manager module
- Main orchestration script

**Configuration Files**:
- Python dependencies list
- Docker compose definition
- Application configuration
- Environment variables (optional)

**Data Directories**:
- Input PDFs location (configurable)
- Vector database storage
- Logs directory (future)
- Cache directory for models

### 8.2 Storage Paths

**Qdrant Storage**:
- Default: ./qdrant_storage
- Purpose: Persistent vector database
- Size: Scales with document count

**Model Cache**:
- Default: ~/.cache/torch/sentence_transformers
- Purpose: Downloaded embedding models
- Size: ~80MB per model

**Temporary Files**:
- Processing intermediates (if any)
- Cleared after successful run

---

## 9. Network and Connectivity

### 9.1 Network Requirements

**Docker Networking**:
- Bridge network for container isolation
- Port mapping for database access
- No external network required for operation

**External Connections**:
- Model download (first run only)
- HuggingFace Hub for models
- PyPI for package installation

### 9.2 Port Configuration

**Qdrant Ports**:
- **6333**: HTTP API (REST interface)
- **6334**: gRPC API (high-performance)
- **Access**: Localhost only by default

---

## 10. Performance Benchmarks

### 10.1 Expected Performance

**PDF Conversion**:
- Simple PDF: 1-2 seconds per page
- Complex PDF with tables: 3-5 seconds per page
- Very large documents: Variable

**Chunking**:
- Fast operation: <1 second for typical document
- Scales linearly with document size

**Embedding Generation**:
- **CPU**: ~500-1000 chunks per minute
- **GPU**: ~5000-10000 chunks per minute
- First run slower (model loading)

**Database Storage**:
- Fast: <1 second for typical batch
- Scales well to thousands of chunks

### 10.2 Scalability Estimates

**Small Collection** (<1000 chunks):
- Storage: <100MB
- Search: <100ms
- Processing: <5 minutes

**Medium Collection** (1000-10000 chunks):
- Storage: 100MB-1GB
- Search: 100-500ms
- Processing: 5-50 minutes

**Large Collection** (>10000 chunks):
- Storage: >1GB
- Search: 500ms-2s
- Processing: >50 minutes

---

## 11. Environment Configuration

### 11.1 Configuration Methods

**Options**:
- Python configuration module (default)
- Environment variables (override)
- Command-line arguments (future)
- Configuration file (future)

### 11.2 Key Configuration Parameters

**Application Settings**:
- PDF input path
- Qdrant storage path
- Collection name
- Processing verbosity

**Model Settings**:
- Embedding model name
- Device selection (cpu/cuda)
- Batch size
- Cache directory

**Chunking Settings**:
- Chunk size target
- Overlap amount
- Table serialization format
- Image handling

**Database Settings**:
- Connection string/path
- Collection parameters
- Distance metric
- Storage mode

---

## 12. Error Codes and Handling

### 12.1 Error Categories

**Input Errors**:
- PDF not found
- Invalid PDF format
- Corrupted PDF file

**Processing Errors**:
- Conversion failures
- Chunking errors
- Embedding generation failures

**Storage Errors**:
- Database connection failures
- Collection creation errors
- Upsert failures

**System Errors**:
- Out of memory
- Disk space issues
- Permission errors

### 12.2 Error Recovery

**Graceful Degradation**:
- Skip problematic chunks if possible
- Continue processing after recoverable errors
- Clear error messages for user action

**Logging**:
- Error context capture
- Stack traces for debugging
- Operation state at failure

---

## 13. Testing Specifications

### 13.1 Test Data Requirements

**PDF Test Suite**:
- Simple single-page text PDF
- Multi-page structured document
- Document with tables
- Document with complex formatting
- Large document (>100 pages)

**Expected Outputs**:
- Reference markdown outputs
- Expected chunk counts
- Validation checksums

### 13.2 Test Coverage Goals

**Unit Test Coverage**:
- All service modules
- Configuration validation
- Utility functions
- Error handling paths

**Integration Test Coverage**:
- Pipeline connections
- Database operations
- End-to-end processing

---

## 14. Deployment Specifications

### 14.1 Setup Scripts

**Startup Script Requirements**:
- Check prerequisites (Docker, Python)
- Start Docker Compose services
- Wait for service health
- Initialize database collections
- Verify system ready

**Teardown Script Requirements**:
- Stop all containers gracefully
- Optional: Preserve data volumes
- Clean up networks
- Report cleanup status

### 14.2 Verification Steps

**Health Checks**:
- Qdrant database accessible
- Collection creation successful
- Python dependencies available
- Model download successful

---

## 15. Resource Limits

### 15.1 Operational Limits

**Document Limits**:
- Maximum pages: No hard limit (memory dependent)
- Maximum file size: 500MB recommended
- Concurrent documents: 1 (v1)

**Processing Limits**:
- Maximum chunks: Limited by memory and storage
- Maximum batch size: 64 (configurable)
- Timeout per document: Configurable

### 15.2 Storage Limits

**Vector Database**:
- Maximum points: Millions (Qdrant capability)
- Practical limit: Depends on disk space
- Metadata size: Configurable per point

---

## 16. Version Compatibility

### 16.1 Python Versions

**Supported**:
- Python 3.9.x
- Python 3.10.x
- Python 3.11.x
- Python 3.12.x

**Not Supported**:
- Python 3.8 and below
- Python 3.13+ (untested)

### 16.2 Library Compatibility

**Stable Combinations**:
- Documented in dependencies list
- Tested together
- Version pins recommended

**Upgrade Path**:
- Minor version updates generally safe
- Major version updates require testing
- Pin versions for reproducibility

---

## 17. Reference Links

### 17.1 Official Documentation

**Docling**:
- GitHub: https://github.com/docling-project/docling
- Examples: https://github.com/docling-project/docling/tree/main/docs/examples

**Docling Core**:
- GitHub: https://github.com/docling-project/docling-core

**Qdrant**:
- Documentation: https://qdrant.tech/documentation/
- Python Client: https://python-client.qdrant.tech/
- Docker Hub: https://hub.docker.com/r/qdrant/qdrant

**Sentence Transformers**:
- Documentation: https://www.sbert.net/
- Models: https://www.sbert.net/docs/pretrained_models.html
- GitHub: https://github.com/UKPLab/sentence-transformers

### 17.2 Model Resources

**all-MiniLM-L6-v2**:
- HuggingFace: https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
- Performance benchmarks available
- Training details documented

---

**End of Technical Specifications**

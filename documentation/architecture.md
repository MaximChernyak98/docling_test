# Technical Architecture Documentation

**Project**: PDF to Markdown Converter with Semantic Search
**Version**: 2.0
**Date**: 2025-12-02

---

## Overview

This document describes the technical architecture, component interactions, and technology choices for the PDF semantic search system. It provides conceptual guidance without implementation details.

---

## 1. System Architecture

### 1.1 Architectural Pattern

The system follows a **pipeline architecture** with four distinct stages:

```
Input Stage → Processing Stage → Transformation Stage → Storage Stage
```

Each stage is independent, with clearly defined inputs and outputs, enabling:
- Easy testing of individual components
- Flexible replacement of technologies
- Clear error boundaries
- Progressive data transformation

### 1.2 Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Application Layer                       │
│                  (Orchestration & Control)                  │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌──────────────┐      ┌──────────────┐     ┌──────────────┐
│  Conversion  │      │   Chunking   │     │  Embedding   │
│   Service    │──────│   Service    │─────│   Service    │
└──────────────┘      └──────────────┘     └──────────────┘
                                                    │
                                                    ▼
                                          ┌──────────────────┐
                                          │  Storage Service │
                                          │  (Vector DB)     │
                                          └──────────────────┘
```

---

## 2. Component Specifications

### 2.1 Conversion Service

**Responsibility**: Transform PDF binary into structured markdown

**Technology Approach**:
- Uses document understanding library
- Analyzes PDF layout and structure
- Extracts text, tables, and formatting
- Generates markdown representation

**Inputs**:
- PDF file path
- Configuration parameters (optional)

**Outputs**:
- Structured document object
- Markdown string representation
- Document metadata

**Key Capabilities**:
- Table recognition and conversion
- Heading hierarchy detection
- List structure preservation
- Paragraph boundary identification

---

### 2.2 Chunking Service

**Responsibility**: Segment documents into semantically coherent pieces

**Chunking Strategy**:
- **Hierarchical Chunking**: Respects document structure (sections, subsections)
- **Semantic Boundaries**: Splits at natural breakpoints (paragraph ends, section changes)
- **Context Preservation**: Maintains heading context within chunks
- **Table Handling**: Keeps tables intact when size permits

**Chunk Sizing Considerations**:
- **Target Size**: 256-512 tokens
  - Rationale: Balance between context and specificity
  - Small enough for focused retrieval
  - Large enough to maintain coherence

- **Overlap Strategy**: 30-50 tokens
  - Rationale: Prevents information loss at boundaries
  - Ensures smooth transitions between chunks
  - Improves retrieval recall

**Metadata Enrichment**:
Each chunk carries context information:
- Source document reference
- Position within document (page, sequence)
- Structural context (heading hierarchy)
- Content classification (text, table, list)
- Original markdown content

**Design Considerations**:
- Configurable chunk parameters
- Preserves semantic coherence
- Avoids splitting mid-sentence
- Maintains table integrity

---

### 2.3 Embedding Service

**Responsibility**: Convert text chunks into vector representations

**Embedding Approach**:
- Uses transformer-based sentence encoding
- Generates fixed-dimension dense vectors
- Captures semantic meaning in vector space
- Enables similarity comparison

**Model Characteristics**:
- **Recommended**: Lightweight sentence transformer
- **Vector Size**: 384 dimensions
  - Balance between quality and efficiency
  - Standard for many sentence transformers
  - Compatible with most vector databases

- **Distance Metric**: Cosine similarity
  - Measures angle between vectors
  - Normalized for fair comparison
  - Industry standard for semantic similarity

**Processing Strategy**:
- Batch processing for efficiency
- Normalization for consistent comparison
- Device flexibility (CPU/GPU)
- Progress tracking for large sets

**Technical Considerations**:
- Model downloads automatically on first run
- Caching for repeated use
- Memory management for large batches
- Error handling for edge cases

---

### 2.4 Storage Service

**Responsibility**: Persist vectors and enable similarity search

**Vector Database Approach**:
- Local instance for development/prototype
- Persistent storage on disk
- Collection-based organization
- Metadata payload support

**Collection Structure**:
- **Vectors**: 384-dimensional embeddings
- **IDs**: Unique identifier per chunk
- **Payloads**: Full metadata for each chunk
- **Distance**: Cosine similarity metric

**Search Capabilities**:
- Vector similarity search
- Top-K retrieval
- Payload filtering (future enhancement)
- Score-based ranking

**Storage Management**:
- Persistent local storage
- Collection lifecycle management
- Data integrity verification
- Cleanup capabilities

**Performance Characteristics**:
- Sub-second search for typical collections
- Scales to thousands of chunks
- Memory-efficient indexing
- Disk persistence for durability

---

## 3. Data Flow and Transformations

### 3.1 End-to-End Pipeline

**Stage 1: PDF Ingestion**
```
PDF File (Binary)
    ↓
[Document Parser]
    ↓
Structured Document Object
    ↓
Markdown String + Metadata
```

**Stage 2: Semantic Segmentation**
```
Document Object + Markdown
    ↓
[Hierarchical Chunker]
    ↓
List of Text Chunks
    ↓
Each Chunk: {text, metadata}
```

**Stage 3: Vector Generation**
```
Text Chunks
    ↓
[Sentence Transformer]
    ↓
Vector Embeddings (384-dim)
    ↓
Normalized Vectors
```

**Stage 4: Persistent Storage**
```
Vectors + Metadata
    ↓
[Vector Database Client]
    ↓
Database Points
    ↓
Searchable Collection
```

### 3.2 Data Transformations

**PDF → Document Object**
- Binary → Parsed structure
- Layout analysis → Semantic structure
- Visual elements → Markdown syntax

**Document → Chunks**
- Single document → Multiple segments
- Continuous text → Discrete pieces
- Flat content → Hierarchical context

**Chunks → Vectors**
- Text strings → Numerical representations
- Variable length → Fixed dimensions
- Semantic meaning → Geometric space

**Vectors → Database**
- In-memory objects → Persistent storage
- Isolated data → Searchable collection
- Individual vectors → Similarity graph

---

## 4. Technology Stack

### 4.1 Core Libraries

**PDF Processing**
- **Library**: Docling
- **Purpose**: Advanced PDF understanding and conversion
- **Why**: Preserves document structure, handles tables well
- **Alternatives Considered**: PyMuPDF, pdfplumber (less structure-aware)

**Semantic Chunking**
- **Library**: Docling Core
- **Purpose**: Intelligent document segmentation
- **Why**: Designed for semantic boundaries, hierarchical awareness
- **Alternatives Considered**: LangChain splitters (less document-aware)

**Embedding Generation**
- **Library**: Sentence Transformers
- **Model**: all-MiniLM-L6-v2
- **Why**: Fast, efficient, good quality for semantic search
- **Alternatives Considered**: OpenAI embeddings (requires API), larger models (slower)

**Vector Storage**
- **Database**: Qdrant
- **Why**: Local deployment, excellent performance, Python client
- **Alternatives Considered**: Chroma (less mature), Milvus (heavier), FAISS (no metadata)

### 4.2 Infrastructure Components

**Containerization**
- **Technology**: Docker + Docker Compose
- **Purpose**: Isolated, reproducible environment
- **Services**: Vector database, supporting services

**Development Environment**
- **Language**: Python 3.9+
- **Package Manager**: pip
- **Dependencies**: Listed in requirements specification

---

## 5. Configuration Architecture

### 5.1 Configuration Categories

**Document Processing Configuration**
- Conversion pipeline options
- Table handling preferences
- Image exclusion rules

**Chunking Configuration**
- Chunk size targets
- Overlap amounts
- Boundary detection rules
- Table serialization format

**Embedding Configuration**
- Model selection
- Batch sizes
- Device selection (CPU/GPU)
- Normalization options

**Storage Configuration**
- Database paths
- Collection names
- Vector dimensions
- Distance metrics

### 5.2 Configuration Strategy

- Centralized configuration module
- Environment-based overrides
- Sensible defaults for common use cases
- Type validation for safety

---

## 6. Project Structure Concept

### 6.1 Module Organization

**Separation of Concerns**:
- Each service in dedicated module
- Configuration isolated from logic
- Orchestration separate from processing
- Utilities shared across modules

**Module Hierarchy**:
```
Application Entry Point
    ├── Configuration Management
    ├── Service Modules
    │   ├── Conversion Service
    │   ├── Chunking Service
    │   ├── Embedding Service
    │   └── Storage Service
    ├── Orchestration Logic
    └── Utility Functions
```

### 6.2 Data Directory Structure

**Input/Output Organization**:
- Source PDFs in defined location
- Vector database persistence directory
- Logs and metrics (future)
- Configuration files

---

## 7. Error Handling Strategy

### 7.1 Error Boundaries

**Per-Stage Error Handling**:
- **Conversion**: Invalid PDF handling
- **Chunking**: Malformed document handling
- **Embedding**: Model loading failures
- **Storage**: Database connection issues

### 7.2 Error Recovery

- Graceful degradation where possible
- Clear error messages for users
- Logging for debugging
- Validation at stage boundaries

---

## 8. Performance Considerations

### 8.1 Bottleneck Analysis

**Likely Bottlenecks**:
1. PDF conversion for large documents
2. Embedding generation for many chunks
3. Initial model loading

**Mitigation Strategies**:
- Batch processing for embeddings
- Progress indicators for long operations
- Model caching after first load
- Memory-efficient processing

### 8.2 Scalability Path

**Current Scale**: Single document, local processing
**Future Scale Considerations**:
- Batch processing multiple documents
- Distributed embedding generation
- Remote vector database
- Parallel processing

---

## 9. Security and Privacy

### 9.1 Data Handling

- All processing local by default
- No external API calls (except model downloads)
- No data transmission to third parties
- Local storage only

### 9.2 Future Considerations

- Input validation for PDF uploads
- Sanitization of metadata
- Access control for database
- Encryption for sensitive documents

---

## 10. Testing Strategy

### 10.1 Test Categories

**Unit Tests**:
- Individual service functionality
- Configuration validation
- Utility functions

**Integration Tests**:
- Pipeline stage connections
- Database operations
- Model loading and inference

**End-to-End Tests**:
- Complete pipeline execution
- Search functionality
- Error scenarios

### 10.2 Test Data

- Sample PDFs of varying complexity
- Expected outputs for validation
- Edge cases (empty pages, large tables)

---

## 11. Deployment Architecture

### 11.1 Local Deployment

**Docker Compose Setup**:
- Vector database container
- Persistent volume mounts
- Network configuration
- Service dependencies

**Setup Scripts**:
- **Startup**: Initialize all services
- **Teardown**: Clean shutdown
- **Verification**: Health checks

### 11.2 Environment Setup

**Prerequisites**:
- Docker and Docker Compose installed
- Python environment configured
- Sufficient disk space
- Adequate memory

**Initialization Steps**:
1. Container orchestration startup
2. Database initialization
3. Python dependencies installation
4. Model download verification

---

## 12. Monitoring and Observability

### 12.1 Processing Metrics

**Pipeline Metrics**:
- Documents processed
- Chunks generated
- Embeddings created
- Storage operations

**Performance Metrics**:
- Processing time per stage
- Memory usage
- Database size
- Search latency (future)

### 12.2 Logging Strategy

- Structured logging approach
- Per-stage log levels
- Error context capture
- Progress indicators

---

## 13. Future Architecture Enhancements

### 13.1 Potential Improvements

**Batch Processing**:
- Queue-based document processing
- Parallel pipeline execution
- Progress tracking across documents

**Advanced Search**:
- Hybrid search (vector + keyword)
- Faceted filtering
- Result re-ranking

**API Layer**:
- REST API for document upload
- Search endpoint
- Management endpoints

**Distributed Architecture**:
- Remote vector database
- Distributed embedding generation
- Cloud deployment

### 13.2 Extensibility Points

- Pluggable embedding models
- Custom chunking strategies
- Alternative vector databases
- Multiple output formats

---

## 14. References and Resources

### 14.1 Technology Documentation

**Docling**:
- Project: https://github.com/docling-project/docling
- Documentation: Official GitHub docs
- Examples: RAG and chunking examples

**Docling Core**:
- Project: https://github.com/docling-project/docling-core
- Chunking strategies documentation

**Sentence Transformers**:
- Documentation: https://www.sbert.net/
- Model hub: HuggingFace

**Qdrant**:
- Documentation: https://qdrant.tech/documentation/
- Python client: https://python-client.qdrant.tech/

### 14.2 Architectural Patterns

- Pipeline architecture patterns
- Vector database design patterns
- Semantic search best practices
- RAG system architecture

---

**End of Architecture Documentation**

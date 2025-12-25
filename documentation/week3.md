---
# 📘 Week 3 Documentation

## Embedding Generation & Vector Database Indexing

**Project:** Company Internal Chatbot with Role-Based Access Control (RBAC) and Retrieval-Augmented Generation (RAG)

---

## 1. Overview

Week 3 focuses on converting the **processed, role-aware document chunks** (produced in Milestone 1) into a **searchable semantic knowledge base**.

The core objective is to:

* Generate dense vector embeddings for each document chunk
* Store these embeddings in a vector database
* Preserve metadata for downstream RBAC enforcement
* Enable efficient semantic similarity search

This week introduces **machine learning components**, but does **not yet involve user authentication, RAG generation, or frontend UI**.

---

## 2. Objectives

The primary objectives of Week 3 are:

* Select a lightweight, high-quality embedding model
* Generate embeddings for all processed chunks
* Initialize and populate a vector database
* Store embeddings together with metadata
* Validate semantic search quality and performance

---

## 3. Inputs

### 3.1 Processed Dataset

Input data comes from Milestone 1:

```
data/processed/document_chunks.jsonl
```

Each entry contains:

* Chunk text
* Department
* Source file
* Allowed roles
* Unique chunk ID

This ensures the vector store is **RBAC-ready by design**.

---

## 4. Embedding Model Selection

### 4.1 Selected Model

**Model:** `sentence-transformers/all-MiniLM-L6-v2`

### 4.2 Rationale

This model was chosen because it:

* Is open-source and free
* Has low latency and small memory footprint
* Produces high-quality sentence embeddings
* Is widely adopted for semantic search and RAG systems

Key properties:

* Embedding dimension: 384
* Optimized for cosine similarity
* Suitable for real-time applications

---

## 5. Embedding Generation Pipeline

### 5.1 Processing Flow

```
Document Chunk Text
 → Sentence Transformer Encoder
 → Dense Vector Embedding
 → Metadata Attachment
 → Vector Store Insertion
```

Each chunk is embedded independently to preserve granularity.

---

### 5.2 Embedding Strategy

* Each chunk’s full text is embedded
* No summarization or truncation applied
* Embeddings generated in batches to optimize performance

This approach maximizes semantic recall during retrieval.

---

## 6. Vector Database Selection

### 6.1 Chroma DB

**Vector Database:** Chroma (local, file-based)

### 6.2 Reasons for Selection

* Open-source and free
* Easy local deployment
* Native Python support
* Metadata-aware querying
* Suitable for small-to-medium scale internal systems

---

## 7. Vector Store Initialization

### 7.1 Collection Configuration

A dedicated collection is created:

```
Collection name: company_docs
```

Each record contains:

* `id`: unique chunk ID
* `embedding`: vector representation
* `document`: chunk text
* `metadata`:

  * department
  * source_file
  * allowed_roles

---

### 7.2 Metadata Design

Metadata is preserved exactly as defined in Milestone 1.

This ensures:

* RBAC can be enforced post-retrieval
* Source attribution is traceable
* No sensitive information is lost or mixed

---

## 8. Indexing Process

### 8.1 Indexing Strategy

* Existing collection is cleared before indexing (idempotent runs)
* Chunks are indexed in batches
* Each batch insertion is logged

This allows:

* Safe re-runs during development
* Easy debugging and verification

---

### 8.2 Indexing Output

At the end of indexing:

* All chunks are stored in Chroma
* Each chunk is retrievable by semantic similarity
* Metadata remains attached to each vector

---

## 9. Semantic Search Capability

### 9.1 Query Flow (Without RBAC Yet)

```
User Query
 → Query Embedding
 → Vector Similarity Search
 → Top-K Candidate Chunks
```

At this stage:

* Retrieval is purely semantic
* RBAC filtering is implemented in Week 4

---

### 9.2 Over-Fetching Strategy

To support later RBAC filtering:

* More results than needed (e.g., top 20) are retrieved
* Unauthorized chunks can be filtered downstream
* Authorized results are selected from remaining candidates

---

## 10. Validation & Quality Checks

### 10.1 Index Integrity Checks

* All chunks successfully indexed
* No missing or duplicate IDs
* Metadata correctly attached

---

### 10.2 Search Quality Checks

Test queries such as:

* “employee benefits”
* “marketing results Q4”
* “engineering architecture”

Observed behavior:

* Relevant documents ranked higher
* Semantic similarity working as expected

---

### 10.3 Performance Checks

* Indexing time acceptable for dataset size
* Query latency well under 500ms for local setup
* Embedding generation stable without errors

---

## 11. Deliverables (Week 3)

* Embedding generation module
* Chroma vector database initialized
* Indexed document collection
* Semantic search capability
* Validation test outputs
* Week 3 documentation

---

## 12. Key Design Decisions (Week 3)

1. **Use of lightweight embedding model**

   * Faster iteration
   * Lower resource usage

2. **Local vector database**

   * Simplifies development
   * Avoids cloud dependency

3. **Metadata-first indexing**

   * Enables secure retrieval later
   * Avoids post-hoc security fixes

4. **Over-fetching strategy**

   * Enables robust RBAC enforcement

---

## 13. Outcome of Week 3

At the end of Week 3:

* All document chunks are embedded
* Vector database is fully populated
* Semantic similarity search is operational
* The system is ready for **RBAC-aware query filtering**

This completes the **data intelligence layer** of the project.

---

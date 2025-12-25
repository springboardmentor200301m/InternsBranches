---

# 📘 Milestone 1 Documentation

## Data Preparation, Preprocessing & Vector Database Readiness

**Project:** Company Internal Chatbot with Role-Based Access Control (RBAC) and Retrieval-Augmented Generation (RAG)

---

## 1. Milestone Overview

**Milestone 1** establishes the **data foundation** of the system.
Its purpose is to ensure that all company documents are:

* Properly understood
* Securely structured
* Cleaned and chunked
* Tagged with role-based access metadata
* Ready for semantic indexing and retrieval

This milestone deliberately excludes authentication, LLM integration, and frontend development to maintain a strong **separation of concerns**.

---

## 2. Milestone Scope

This milestone covers:

* Environment setup
* Data exploration and analysis
* Role-to-document access mapping
* Document preprocessing
* Chunking strategy design
* Metadata tagging for RBAC
* Validation and quality checks

It corresponds to:

* **Week 1:** Environment Setup & Data Exploration
* **Week 2:** Document Preprocessing, Chunking & Metadata Tagging

---

## 3. Objectives

The primary objectives of Milestone 1 are:

1. Understand the structure and sensitivity of company data
2. Define strict role-based access boundaries at the data level
3. Convert raw documents into retrieval-ready chunks
4. Ensure security, traceability, and auditability before vector indexing

---

## 4. Input Data Description

The system processes department-specific company documents:

| Department  | Format   | Description                               |
| ----------- | -------- | ----------------------------------------- |
| Finance     | Markdown | Financial summaries and quarterly reports |
| Marketing   | Markdown | Campaign and market analysis              |
| Engineering | Markdown | Technical architecture documentation      |
| HR          | CSV      | Employee records (highly sensitive)       |
| General     | Markdown | Employee handbook and policies            |

---

## 5. Role Taxonomy & Access Model

### 5.1 Defined Roles

* Employee
* Finance
* Marketing
* Engineering
* HR
* C-Level

---

### 5.2 Role Hierarchy

```
C-Level
  └── Department Roles (Finance / HR / Marketing / Engineering)
        └── Employee
```

---

### 5.3 Role-to-Document Mapping

| Role        | Accessible Documents  |
| ----------- | --------------------- |
| Employee    | General handbook      |
| Finance     | Finance + General     |
| Marketing   | Marketing + General   |
| Engineering | Engineering + General |
| HR          | HR + General          |
| C-Level     | All documents         |

**Design principle:**

> Access rules are **strict by default** and can be expanded later if required.

---

## 6. Data Exploration & Analysis (Week 1)

### Key Activities

* Inspected directory structure
* Identified file formats and volume
* Previewed document contents safely
* Identified sensitive fields (HR salary, performance data)

### Outcomes

* Confirmed dataset completeness
* Classified documents by sensitivity
* Identified special handling requirements for HR CSV

---

## 7. Document Preprocessing Pipeline (Week 2)

### 7.1 Processing Flow

```
Raw Document
 → Parsing
 → Text Cleaning
 → Chunking
 → Metadata Tagging
 → Validation
 → Processed Dataset
```

Each step is deterministic and reproducible.

---

### 7.2 Parsing Strategy

* **Markdown:** Section-aware text extraction
* **CSV (HR):** Row-level parsing to avoid bulk exposure

---

### 7.3 Chunking Strategy

* Chunk size: ~300 tokens
* No overlapping chunks
* Each chunk represents a self-contained semantic unit

Chunk ID format:

```
<department>/<source_file>::chunk_<index>
```

---

## 8. Metadata & RBAC Enforcement

### 8.1 Metadata Fields

Each chunk contains:

| Field           | Purpose                   |
| --------------- | ------------------------- |
| `id`            | Unique chunk identifier   |
| `text`          | Chunk content             |
| `department`    | Source department         |
| `source_file`   | Origin document           |
| `allowed_roles` | Roles permitted to access |

---

### 8.2 RBAC at Data Level

RBAC is enforced **before retrieval**, not after generation.

Examples:

* HR chunk:

```json
"allowed_roles": ["hr", "c_level"]
```

* Finance chunk:

```json
"allowed_roles": ["finance", "c_level"]
```

* General chunk:

```json
"allowed_roles": ["employee", "finance", "marketing", "engineering", "hr", "c_level"]
```

This ensures:

* No unauthorized chunk can ever be retrieved
* LLM never receives restricted context

---

## 9. Processed Dataset Output

All chunks are stored in:

```
data/processed/document_chunks.jsonl
```

Format:

```json
{
  "id": "...",
  "text": "...",
  "department": "...",
  "source_file": "...",
  "allowed_roles": [...]
}
```

This format is:

* Stream-friendly
* Easy to audit
* Ready for embedding and indexing

---

## 10. Validation & Quality Assurance

### 10.1 Structural Checks

* All chunks have required metadata
* No duplicate IDs
* No empty text fields

### 10.2 Security Checks

* HR salary data restricted correctly
* No cross-department leakage
* Employee role limited to general documents

### 10.3 Distribution Checks

* Chunk counts reviewed per department
* No abnormal skew detected

---

## 11. Deliverables (Milestone 1)

* Python virtual environment
* Data exploration scripts
* Preprocessing & chunking pipeline
* Role-aware processed dataset
* RBAC metadata definitions
* Validation reports
* Week 1 & Week 2 documentation
* Milestone 1 documentation

---

## 12. Key Design Decisions

1. **RBAC at chunk level**

   * Fine-grained control
   * Strong security guarantees

2. **HR data row-level chunking**

   * Prevents bulk data exposure
   * Enables precise retrieval

3. **Strict default permissions**

   * Security-first design

4. **No LLM dependency**

   * Focus on correctness before intelligence

---

## 13. Milestone Completion Statement

**Milestone 1 is successfully completed.**

At the end of this milestone:

* The data layer is fully prepared
* Security boundaries are clearly enforced
* The system is ready for embedding generation, vector indexing, and semantic search

---

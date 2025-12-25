---

# 📘 Week 2 Documentation

## Document Preprocessing, Chunking & Metadata Tagging

**Project:** Company Internal Chatbot with Role-Based Access Control (RBAC) and Retrieval-Augmented Generation (RAG)

---

## 1. Overview

Week 2 focuses on transforming raw company documents into a **machine-readable, role-aware knowledge base** suitable for semantic search and RAG.

The primary goal of this week is to:

* Convert heterogeneous documents into a uniform structure
* Break content into semantically meaningful chunks
* Attach role-based access metadata at the **lowest possible granularity**
* Prepare clean inputs for embedding and vector indexing

This stage is **critical for security, retrieval quality, and system correctness**.

---

## 2. Objectives

The key objectives of Week 2 are:

* Parse markdown and CSV documents reliably
* Clean and normalize textual content
* Chunk documents into retrieval-friendly segments
* Assign strict role-based metadata to each chunk
* Validate chunk quality and access correctness
* Produce a processed dataset ready for embedding

---

## 3. Input Data

### 3.1 Raw Data Sources

All inputs originate from the `data/raw/` directory:

| Department  | Format   | Notes                               |
| ----------- | -------- | ----------------------------------- |
| Finance     | Markdown | Narrative financial reports         |
| Marketing   | Markdown | Quarterly and annual reports        |
| Engineering | Markdown | Technical documentation             |
| HR          | CSV      | Row-level employee data (sensitive) |
| General     | Markdown | Company handbook and policies       |

---

## 4. Preprocessing Architecture

The preprocessing pipeline follows a **deterministic, reproducible flow**:

```
Raw Document
 → Parse
 → Clean
 → Chunk
 → Assign Metadata
 → Validate
 → Save to Processed Dataset
```

Each step is intentionally separated to simplify debugging and auditing.

---

## 5. Document Parsing Strategy

### 5.1 Markdown Parsing

Markdown files are parsed by:

* Reading raw text
* Preserving section boundaries where possible
* Flattening tables and bullet points into plain text
* Retaining semantic cues (headings, section titles)

Design rationale:

> Markdown documents already encode structure; preserving this improves semantic coherence during retrieval.

---

### 5.2 CSV Parsing (HR Data)

HR data requires special handling due to sensitivity.

Approach:

* Each row is treated as an independent logical unit
* Rows are converted into structured text summaries
* Sensitive attributes remain but are **protected via metadata**

Example (conceptual):

```
Employee ID: FINEMP1001
Role: Credit Officer
Department: Finance
Salary: [value]
Performance Rating: [value]
```

This allows:

* Fine-grained access control
* Precise retrieval
* Prevention of bulk data exposure

---

## 6. Text Cleaning & Normalization

Before chunking, text undergoes normalization:

* Removal of excessive whitespace
* Normalization of line breaks
* Unicode normalization
* Safe handling of encoding issues

No aggressive stop-word removal is performed to avoid semantic loss.

---

## 7. Chunking Strategy

### 7.1 Chunk Size

* **Target size:** ~300 tokens per chunk
* Small overlap avoided for simplicity and clarity

Rationale:

* Large enough to preserve context
* Small enough to improve retrieval precision
* Efficient for vector search and LLM context limits

---

### 7.2 Chunk Identification

Each chunk is assigned a deterministic identifier:

```
<department>/<source_file>::chunk_<index>
```

Example:

```
hr/hr_data.csv::chunk_62
marketing/marketing_report_q2_2024.md::chunk_3
```

This enables:

* Precise source attribution
* Auditability
* Debugging and traceability

---

## 8. Role-Based Metadata Tagging

### 8.1 Metadata Fields

Each chunk is enriched with metadata:

| Field           | Description               |
| --------------- | ------------------------- |
| `id`            | Unique chunk identifier   |
| `text`          | Chunk content             |
| `department`    | Owning department         |
| `source_file`   | Original document         |
| `allowed_roles` | Roles permitted to access |

---

### 8.2 Role Assignment Logic

Role assignment strictly follows the mapping defined in Week 1.

Examples:

* Finance document chunk:

```json
"allowed_roles": ["finance", "c_level"]
```

* HR CSV chunk:

```json
"allowed_roles": ["hr", "c_level"]
```

* General handbook chunk:

```json
"allowed_roles": ["employee", "finance", "marketing", "engineering", "hr", "c_level"]
```

Design principle:

> **RBAC enforcement begins at data level, not application level.**

---

## 9. Processed Dataset Format

All processed chunks are stored in:

```
data/processed/document_chunks.jsonl
```

Each line represents one chunk.

Example structure:

```json
{
  "id": "general/employee_handbook.md::chunk_4",
  "text": "### Workplace Safety Guidelines ...",
  "department": "general",
  "source_file": "employee_handbook.md",
  "allowed_roles": ["employee", "finance", "marketing", "engineering", "hr", "c_level"]
}
```

This format:

* Is streaming-friendly
* Supports large datasets
* Is easy to debug and inspect

---

## 10. Validation & Quality Assurance

Several validation checks are performed:

### 10.1 Structural Validation

* All chunks contain required metadata fields
* No empty or malformed chunks
* IDs are unique

### 10.2 Security Validation

* HR salary chunks restricted to HR and C-Level
* No cross-department role leakage
* General documents accessible to all roles

### 10.3 Distribution Validation

Chunk counts per department are reviewed to detect anomalies.

---

## 11. Deliverables (Week 2)

* Preprocessing script (`scripts/preprocess_docs.py`)
* Cleaned and chunked dataset
* Role-aware metadata mapping
* Validation summary
* Week 2 documentation

---

## 12. Key Design Decisions (Week 2)

1. **Chunk-level RBAC instead of document-level**

   * Enables fine-grained access control
   * Prevents partial data leaks

2. **Row-level HR chunking**

   * Protects sensitive employee data
   * Enables controlled retrieval

3. **JSONL storage format**

   * Scalable and inspectable
   * Easy to integrate with vector databases

4. **Strict defaults**

   * Security prioritized over convenience

---

## 13. Outcome of Week 2

At the end of Week 2:

* All company documents are transformed into clean, structured chunks
* Each chunk carries explicit role-based access rules
* The dataset is ready for embedding and vector indexing
* The system is prepared for semantic search with RBAC enforcement

---

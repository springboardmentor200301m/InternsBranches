---

# 📘 Milestone 2 Documentation

## Vector Database, Semantic Search & Role-Based Access Control (RBAC)

**Project:** Company Internal Chatbot with Role-Based Access Control (RBAC) and Retrieval-Augmented Generation (RAG)

---

## 1. Milestone Overview

**Milestone 2** establishes the **core retrieval intelligence and security layer** of the system.

While Milestone 1 focused on preparing data safely, Milestone 2 ensures that:

* Company knowledge is **searchable using semantic similarity**
* All retrieval operations are **strictly governed by RBAC**
* Unauthorized users are **technically incapable** of accessing restricted information

This milestone transforms static data into a **secure, queryable enterprise knowledge base**.

---

## 2. Milestone Scope

Milestone 2 covers:

* Embedding model selection and integration
* Vector database initialization and indexing
* Semantic similarity search implementation
* Role-based filtering at query time
* Query normalization and validation
* Security and access enforcement testing

This milestone corresponds to:

* **Week 3:** Embedding Generation & Vector Database Indexing
* **Week 4:** Role-Based Semantic Search & RBAC Enforcement

---

## 3. Objectives

The primary objectives of Milestone 2 are:

1. Enable semantic retrieval across company documents
2. Preserve metadata integrity during vector indexing
3. Enforce RBAC before any LLM interaction
4. Prevent unauthorized data exposure through similarity search
5. Prepare a safe retrieval layer for RAG integration

---

## 4. System Architecture (Milestone 2)

### 4.1 Retrieval Flow

```
User Query
 → Query Embedding
 → Vector Similarity Search (Over-Fetch)
 → Role-Based Filtering
 → Authorized Document Chunks
```

The output of this flow is a **trusted, RBAC-safe context set**.

---

## 5. Embedding Generation

### 5.1 Model Selection

**Model Used:**
`sentence-transformers/all-MiniLM-L6-v2`

### 5.2 Justification

* Open-source and free
* Low latency and memory footprint
* High semantic accuracy for short-to-medium text
* Widely used in production RAG systems

### 5.3 Embedding Strategy

* Each chunk embedded independently
* No truncation of chunk content
* Batch embedding for efficiency

---

## 6. Vector Database Implementation

### 6.1 Database Selection

**Vector Store:** Chroma DB (local)

### 6.2 Reasons for Selection

* Open-source and free
* Native Python API
* Metadata-aware querying
* Easy local deployment
* Suitable for internal systems and POCs

---

### 6.3 Collection Design

```
Collection Name: company_docs
```

Each record includes:

* Chunk ID
* Dense embedding vector
* Original text
* Metadata:

  * department
  * source_file
  * allowed_roles

Metadata is treated as **authoritative** for access decisions.

---

## 7. Semantic Search Design

### 7.1 Over-Fetching Strategy

To ensure RBAC filtering does not starve results:

```
n_results = max(top_k × 5, 20)
```

This ensures:

* High recall
* Robust access filtering
* Stable retrieval under strict permissions

---

### 7.2 Similarity Metrics

* Cosine similarity
* Ranked by semantic relevance
* Scores used for ordering, not authorization

---

## 8. Role-Based Access Control (RBAC)

### 8.1 Enforcement Point

RBAC is enforced:

* **After retrieval**
* **Before RAG or LLM usage**

This guarantees:

* LLM never sees unauthorized content
* No downstream leakage

---

### 8.2 Filtering Rule

```
chunk is allowed ⇔ user_role ∈ chunk.allowed_roles
```

Chunks failing this condition are discarded.

---

### 8.3 Role Hierarchy

```
C-Level
 └── Department Roles
      └── Employee
```

Hierarchy is enforced logically, not via shortcuts.

---

## 9. Security Considerations

### 9.1 Zero-Trust Retrieval

* Vector DB output is untrusted by default
* Metadata governs all access
* Similarity score never overrides security

---

### 9.2 Inference Attack Prevention

* No indication of hidden data
* Silent filtering of restricted chunks
* Consistent response behavior

---

## 10. Validation & Testing

### 10.1 Functional Tests

| Role      | Query                   | Expected Outcome |
| --------- | ----------------------- | ---------------- |
| Employee  | Leave policies          | General docs     |
| HR        | Performance reviews     | HR + General     |
| Marketing | Q4 campaigns            | Marketing        |
| C-Level   | Financial + HR insights | All departments  |

---

### 10.2 Security Tests

| Scenario                           | Result  |
| ---------------------------------- | ------- |
| Employee queries salaries          | Blocked |
| HR queries finance data            | Blocked |
| Department role queries other dept | Blocked |
| C-Level queries any data           | Allowed |

---

### 10.3 Performance Tests

* Retrieval latency < 500 ms
* Stable response under repeated queries
* No memory leaks or indexing errors

---

## 11. Deliverables (Milestone 2)

* Embedding generation module
* Chroma vector database with indexed documents
* RBAC-enabled semantic search service
* Role hierarchy configuration
* Security and validation test results
* Week 3 & Week 4 documentation
* Milestone 2 documentation

---

## 12. Key Design Decisions

1. **RBAC enforced before generation**

   * Prevents data leakage
   * Aligns with enterprise security standards

2. **Metadata-driven authorization**

   * Flexible
   * Auditable
   * Extendable

3. **Over-fetch + filter model**

   * Balances recall and security

4. **Local vector store**

   * Simplifies development
   * Eliminates cloud dependency

---

## 13. Milestone Completion Statement

**Milestone 2 is successfully completed.**

At the end of this milestone:

* The system supports secure semantic search
* Role-based access is strictly enforced
* The retrieval layer is production-ready
* The system is safe to integrate with LLM-based RAG

---

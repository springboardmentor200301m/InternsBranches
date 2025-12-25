---

# 📘 Week 4 Documentation

## Role-Based Semantic Search, Query Processing & RBAC Enforcement

**Project:** Company Internal Chatbot with Role-Based Access Control (RBAC) and Retrieval-Augmented Generation (RAG)

---

## 1. Overview

Week 4 focuses on enforcing **strict role-based access control (RBAC)** during semantic search and query processing. While Week 3 enabled semantic retrieval, Week 4 ensures that **only authorized document chunks are ever returned**, regardless of query intent or similarity score.

This week marks the transition from a *pure semantic system* to a **secure enterprise-grade retrieval system**.

---

## 2. Objectives

The primary objectives of Week 4 are:

* Enforce RBAC at query-time
* Prevent unauthorized data retrieval
* Implement role hierarchy logic
* Normalize and validate user queries
* Prepare the system for safe RAG integration
* Validate RBAC through negative and adversarial tests

---

## 3. Context: Why RBAC at Search Time Matters

In enterprise systems, **security must be enforced before generation**.

If unauthorized chunks reach the LLM:

* Sensitive data may leak
* Hallucinations may include restricted context
* Compliance requirements are violated

Therefore, RBAC is enforced **immediately after retrieval and before RAG**.

---

## 4. Query Processing Architecture

### 4.1 High-Level Flow

```
User Query
 → Query Normalization
 → Semantic Retrieval (Over-Fetch)
 → Role-Based Filtering
 → Authorized Chunks
```

The LLM is not involved at this stage.

---

## 5. Query Normalization

Before semantic search, incoming queries are normalized:

* Trim whitespace
* Convert to lowercase (if required)
* Remove non-semantic noise
* Preserve intent-critical terms

Purpose:

* Improve embedding consistency
* Reduce noisy retrieval
* Prevent malformed inputs

---

## 6. Semantic Search with Over-Fetching

### 6.1 Over-Fetch Strategy

Instead of retrieving exactly `top_k` results, the system retrieves a larger candidate set:

```
n_results = max(top_k * 5, 20)
```

This allows:

* RBAC filtering without starving results
* High recall even after access restrictions

---

### 6.2 Retrieval Without Trust

At this stage:

* Chroma returns **all semantically similar chunks**
* No trust is placed on similarity score alone
* Metadata is treated as the authority

---

## 7. Role-Based Access Control Enforcement

### 7.1 RBAC Filtering Logic

Each retrieved chunk contains an `allowed_roles` metadata field.

Filtering rule:

```
chunk is allowed ⇔ user_role ∈ allowed_roles
```

Chunks failing this condition are **silently discarded**.

---

### 7.2 Role Hierarchy Handling

The role hierarchy is enforced logically:

```
C-Level > Department Role > Employee
```

This means:

* C-Level users automatically satisfy all access conditions
* Department users only access their department + general
* Employees are restricted to general documents

No hard-coded shortcuts are used.

---

## 8. Security Design Principles

### 8.1 Zero-Trust Retrieval

* Vector DB results are never trusted blindly
* Every chunk is validated against RBAC rules
* LLM never receives unauthorized context

---

### 8.2 Backend-Only Enforcement

RBAC is enforced:

* In backend services
* Independent of frontend behavior
* Independent of user-provided tokens or claims

Frontend **cannot bypass** access control.

---

## 9. Handling Unauthorized Queries

If a user submits a query that:

* Semantically matches restricted content
* But lacks permission

The system:

* Returns only authorized results (if any)
* Or returns an empty/limited response
* Does **not reveal the existence** of restricted data

This prevents information leakage via inference.

---

## 10. Validation & Test Scenarios

### 10.1 Positive Tests (Expected Access)

| User Role | Query                           | Expected Result   |
| --------- | ------------------------------- | ----------------- |
| HR        | “Summarize performance reviews” | HR + General data |
| Marketing | “Q4 campaign results”           | Marketing data    |
| Employee  | “Company leave policy”          | General handbook  |
| C-Level   | “Financial risks and HR costs”  | All departments   |

---

### 10.2 Negative Tests (Blocked Access)

| User Role | Query                          | Expected Result |
| --------- | ------------------------------ | --------------- |
| Employee  | “Employee salaries”            | ❌ No HR data    |
| Marketing | “Engineering architecture”     | ❌ Blocked       |
| HR        | “Quarterly revenue”            | ❌ Blocked       |
| Finance   | “Employee performance ratings” | ❌ Blocked       |

---

### 10.3 Adversarial / Edge Tests

* Ambiguous queries spanning departments
* Queries attempting inference attacks
* Broad prompts designed to over-retrieve

Observed behavior:

* Unauthorized chunks consistently filtered
* No cross-role data leakage detected

---

## 11. Performance Considerations

* RBAC filtering adds minimal latency
* Filtering operates on small candidate sets
* Overall retrieval latency remains <500ms

Security correctness prioritized over micro-optimizations.

---

## 12. Deliverables (Week 4)

* RBAC-enabled semantic search module
* Query normalization utilities
* Role hierarchy enforcement logic
* Access control validation tests
* Search performance metrics
* Week 4 documentation

---

## 13. Key Design Decisions (Week 4)

1. **RBAC after retrieval, before generation**

   * Prevents data leakage
   * Protects LLM from sensitive context

2. **Over-fetch + filter approach**

   * Maintains recall
   * Ensures robustness under strict RBAC

3. **Backend-enforced access**

   * Eliminates client-side trust
   * Hardens security posture

4. **Silent denial of unauthorized data**

   * Prevents inference attacks
   * Improves security transparency

---

## 14. Outcome of Week 4

At the end of Week 4:

* Semantic search is fully RBAC-aware
* Unauthorized access is consistently blocked
* The system is safe for RAG integration
* Milestone 2 objectives are fully met

---

### ✅ Milestone Status

**Milestone 2 (Vector Database, Semantic Search & RBAC Enforcement) is complete.**

---

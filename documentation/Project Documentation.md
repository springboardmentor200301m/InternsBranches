---

# 📘 Company Internal Chatbot with Role-Based Access Control (RBAC)

## Retrieval-Augmented Generation (RAG) System – Final Project Documentation

---

## 1. Project Overview

Modern organizations store large volumes of sensitive internal information across departments such as Finance, HR, Marketing, and Engineering. Access to this data must be **strictly controlled**, yet employees and leadership often require **quick, natural-language access** to relevant information.

This project implements a **secure internal chatbot** that uses **Retrieval-Augmented Generation (RAG)** combined with **Role-Based Access Control (RBAC)** to ensure that:

* Users only see information they are authorized to access
* All answers are grounded in company documents
* Large Language Models (LLMs) do not hallucinate or leak data
* The system is explainable, auditable, and production-ready

---

## 2. Problem Statement

Traditional chatbots and search systems suffer from:

* Weak access control
* Hallucinated responses
* Data leakage risks
* Lack of explainability
* Poor auditability

The challenge is to build a system that:

* Understands natural-language queries
* Enforces strict RBAC
* Uses LLMs safely
* Produces traceable, source-backed answers

---

## 3. Solution Summary

This project delivers a **secure, enterprise-grade internal chatbot** with:

* JWT-based authentication
* Hierarchical RBAC enforcement
* Semantic search over company documents
* RAG-based answer generation
* LLM provider abstraction (Groq / OpenAI / Stub)
* Source attribution for every answer
* Streamlit frontend for usability
* FastAPI backend for security and scalability

---

## 4. High-Level Architecture

```
User (Streamlit UI)
      ↓
Authentication (JWT)
      ↓
RBAC Middleware
      ↓
Semantic Search (Chroma)
      ↓
Context Assembly
      ↓
LLM (Groq – LLaMA 3.1)
      ↓
Answer + Sources
```

Security is enforced **before retrieval and generation**, not after.

---

## 5. Technology Stack

| Component       | Technology            |
| --------------- | --------------------- |
| Backend         | FastAPI (Python)      |
| Frontend        | Streamlit             |
| Vector DB       | Chroma                |
| Embeddings      | Sentence-Transformers |
| LLM             | Groq (LLaMA 3.1)      |
| Auth            | OAuth2 + JWT          |
| Database        | SQLite                |
| Language        | Python 3.8+           |
| Version Control | GitHub                |

---

## 6. Data Sources

Documents are provided via a GitHub repository and organized by department:

* Finance: Financial reports
* HR: Employee data (CSV)
* Marketing: Campaign and performance reports
* Engineering: Technical documentation
* General: Employee handbook

Each document is mapped to **explicit role permissions**.

---

## 7. Role-Based Access Control (RBAC)

### 7.1 Supported Roles

* Employee
* Finance
* HR
* Marketing
* Engineering
* C-Level

### 7.2 Role Hierarchy

```
C-Level
 └── Department Roles
      └── Employee
```

Rules:

* Higher roles inherit lower-level access
* Lower roles cannot escalate privileges
* RBAC enforced server-side only

---

## 8. Authentication & Authorization

### 8.1 Authentication Model

* OAuth2 Password Flow
* JWT tokens
* Stateless authentication

JWT payload includes:

```json
{
  "sub": "username",
  "role": "hr",
  "exp": <timestamp>
}
```

### 8.2 Authorization Enforcement

RBAC is enforced at:

1. API endpoints
2. Semantic search filtering
3. RAG context construction
4. LLM prompt generation

---

## 9. Data Processing Pipeline

### 9.1 Document Parsing

* Markdown files parsed section-wise
* HR CSV parsed row-wise
* Text normalized and cleaned

### 9.2 Chunking Strategy

* Chunk size: ~300 tokens
* Sequential chunk IDs
* Metadata attached:

  * department
  * source_file
  * allowed_roles

---

## 10. Vector Database & Search

* Embeddings generated using Sentence-Transformers
* Stored in Chroma with metadata
* Over-fetch strategy used
* Final filtering performed by RBAC logic

Only authorized chunks are returned.

---

## 11. Retrieval-Augmented Generation (RAG)

### 11.1 RAG Flow

```
User Query
 → Auth & RBAC
 → Vector Search
 → Context Selection
 → Prompt Construction
 → LLM Generation
 → Answer + Sources
```

### 11.2 Prompt Grounding

System prompt enforces:

* Context-only answers
* No hallucination
* Explicit refusal if context is insufficient

---

## 12. LLM Integration

### 12.1 Provider

* **Groq**
* Model: `llama-3.1-8b-instant`

### 12.2 LLM Abstraction

The `LLMClient` supports:

* Groq
* OpenAI (optional)
* Stub mode

This enables easy provider switching without modifying RAG logic.

---

## 13. Hallucination & Security Controls

* Context-only prompting
* Low temperature (0.1)
* RBAC before retrieval
* Prompt injection defense
* No hidden data exposure

If no valid context exists:

> “I don’t have enough information to answer this question.”

---

## 14. Source Attribution

Every answer includes:

* Chunk ID
* Source file
* Department
* Similarity score

This ensures:

* Transparency
* Trust
* Auditability

---

## 15. Frontend (Streamlit)

### 15.1 Features

* Login interface
* Role display
* Chat UI
* Answer rendering
* Source citations
* Logout support

### 15.2 Security Model

Frontend:

* Does not enforce RBAC
* Does not filter data
* Does not assemble context
* Only displays backend responses

---

## 16. Testing & Validation

### 16.1 RBAC Tests

| Role     | Unauthorized Query | Result |
| -------- | ------------------ | ------ |
| Employee | Salary info        | ❌      |
| HR       | Finance data       | ❌      |
| Finance  | HR records         | ❌      |
| C-Level  | All data           | ✅      |

### 16.2 Security Tests

* JWT tampering blocked
* Prompt injection neutralized
* Jailbreak attempts failed
* No cross-role leakage observed

---

## 17. Performance Evaluation

| Stage          | Avg Time    |
| -------------- | ----------- |
| Authentication | <100 ms     |
| Vector Search  | ~200 ms     |
| LLM Response   | ~200–400 ms |
| End-to-End     | <3 s        |

---

## 18. Logging & Auditability

Logged events:

* Login attempts
* Role resolution
* Queries
* Retrieval metadata
* LLM calls
* Errors

Enables:

* Security audits
* Usage analysis
* Incident investigation

---

## 19. Deployment Readiness

* `.env`-based configuration
* No hard-coded secrets
* Stateless backend
* Docker-ready
* Cloud or on-prem deployable

---

## 20. Milestone Summary

| Milestone | Focus                 | Status |
| --------- | --------------------- | ------ |
| 1         | Data & Vector DB      | ✅      |
| 2         | Search & RBAC         | ✅      |
| 3         | Auth & RAG            | ✅      |
| 4         | Frontend & Deployment | ✅      |

---

## 21. Final Outcome

At project completion:

* The system is secure, explainable, and production-grade
* RBAC is enforced end-to-end
* LLM usage is responsible and controlled
* Answers are grounded and auditable
* The project meets enterprise AI standards

---

## 22. Conclusion

This project demonstrates how **LLMs can be safely integrated into enterprise systems** when combined with:

* Strong RBAC
* Secure retrieval pipelines
* Thoughtful prompt design
* Transparent answer attribution

It goes beyond a demo chatbot and represents a **real-world internal AI assistant architecture**.

---

## ✅ Project Status

**PROJECT COMPLETED SUCCESSFULLY**

---

# 📕 Milestone 3 Documentation

## Authentication, RBAC Middleware & Retrieval-Augmented Generation (RAG)

**Project:** Company Internal Chatbot with Role-Based Access Control (RBAC)
**Milestone Duration:** Weeks 5–6
**Milestone Status:** ✅ Completed

## 1. Milestone Overview

Milestone 3 transforms the system from a **secure search backend** into a **fully authenticated, role-aware, intelligent assistant** capable of generating **context-grounded responses** using Retrieval-Augmented Generation (RAG).

This milestone introduces:

* Secure user authentication
* Role-based access enforcement at API level
* End-to-end RAG pipeline
* Large Language Model (LLM) integration
* Source-attributed, hallucination-free responses

Security, correctness, and explainability are treated as **first-class design goals**.

---

## 2. Objectives

The objectives of Milestone 3 are:

* Implement secure user authentication using JWT
* Enforce RBAC via middleware (not frontend trust)
* Integrate an LLM in a controlled, auditable manner
* Build a full RAG pipeline
* Prevent hallucination and prompt injection
* Provide transparent source attribution
* Maintain LLM provider flexibility

---

## 3. Authentication System

### 3.1 Authentication Model

The system uses **OAuth2 Password Flow with JWT tokens**.

**Key Characteristics:**

* Stateless authentication
* Short-lived access tokens
* Role embedded in token payload
* Server-side role validation against database

---

### 3.2 User Storage

* SQLite database
* Fields:

  * username
  * hashed_password
  * role
  * active status

Passwords are:

* Hashed using industry-standard cryptographic hashing
* Never stored or transmitted in plaintext

---

### 3.3 JWT Token Structure

Example payload:

```json
{
  "sub": "carol_hr",
  "role": "hr",
  "exp": 1764662083
}
```

JWT is validated on every protected request.

---

## 4. RBAC Middleware

### 4.1 Role Hierarchy

The system enforces a strict role hierarchy:

```
C-Level
  └── Department Roles (Finance, HR, Marketing, Engineering)
        └── Employee
```

Rules:

* Higher roles inherit lower-level access
* Lower roles can never escalate privileges
* Role enforcement occurs server-side only

---

### 4.2 RBAC Enforcement Points

RBAC is enforced at **multiple layers**:

1. API endpoint access
2. Semantic search filtering
3. RAG context assembly
4. LLM prompt construction

This guarantees **defense in depth**.

---

## 5. Retrieval-Augmented Generation (RAG)

### 5.1 RAG Pipeline Flow

```
User Query
 → JWT Validation
 → Role Resolution
 → RBAC-Filtered Semantic Search
 → Context Selection
 → Prompt Construction
 → LLM Generation
 → Answer + Source Attribution
```

The LLM never sees unauthorized data.

---

### 5.2 Semantic Retrieval

* Query embedded using sentence-transformers
* Vector search performed in Chroma
* Over-fetch strategy used
* Final filtering performed by RBAC logic

Only **authorized chunks** reach the LLM.

---

## 6. LLM Integration

### 6.1 Selected Provider

* **Provider:** Groq
* **Model:** `llama-3.1-8b-instant`

---

### 6.2 LLM Abstraction Layer

The system uses an abstract `LLMClient` supporting:

* Groq
* OpenAI (optional)
* Stub / offline mode

This ensures:

* Vendor independence
* Easy provider switching
* Clean separation of concerns

---

### 6.3 Prompt Grounding

The system prompt enforces strict grounding:

```text
You are a company assistant.
Answer only using the provided context.
If the information is not present, say you do not know.
Never hallucinate or infer beyond the context.
```

---

## 7. Hallucination & Abuse Prevention

### 7.1 Hallucination Control

* Context-only prompting
* Low temperature (0.1)
* Explicit refusal instructions
* No chain-of-thought leakage

---

### 7.2 Prompt Injection Defense

Attempts such as:

* “Ignore previous instructions”
* “Reveal confidential data”
* “Act as admin”

are blocked because:

* RBAC precedes retrieval
* LLM cannot access hidden context
* System prompt overrides user input

---

## 8. Source Attribution & Transparency

Every response includes:

* Chunk ID
* Source document
* Department
* Similarity score

Example response:

```json
{
  "answer": "...",
  "sources": [
    {
      "id": "general/employee_handbook.md::chunk_6",
      "department": "general",
      "source_file": "employee_handbook.md",
      "score": 0.54
    }
  ]
}
```

This ensures:

* Explainability
* Trust
* Audit readiness

---

## 9. Testing & Validation

### 9.1 Functional Testing

| Role     | Query               | Result    |
| -------- | ------------------- | --------- |
| Employee | Salary details      | ❌ Blocked |
| HR       | Performance reviews | ✅ Allowed |
| Finance  | HR data             | ❌ Blocked |
| C-Level  | Any dept            | ✅ Allowed |

---

### 9.2 Security Testing

* JWT tampering attempts rejected
* Role escalation attempts blocked
* LLM jailbreak attempts neutralized
* No cross-department leakage detected

---

## 10. Deliverables (Milestone 3)

* JWT authentication system
* RBAC middleware
* Secure FastAPI backend
* RAG orchestration module
* LLM abstraction layer
* Groq LLM integration
* Prompt templates
* Source attribution system
* Security & functionality test results
* Milestone documentation

---

## 11. Success Criteria Evaluation

| Metric                   | Target            | Status |
| ------------------------ | ----------------- | ------ |
| Secure authentication    | Required          | ✅      |
| RBAC enforcement         | Zero leaks        | ✅      |
| RAG correctness          | Context-only      | ✅      |
| Hallucination prevention | No hallucinations | ✅      |
| Response latency         | < 3s              | ✅      |

---

## 12. Outcome of Milestone 3

At the completion of Milestone 3:

* The system is fully authenticated and role-secure
* Answers are grounded, explainable, and auditable
* Unauthorized access is technically impossible
* LLM usage is safe, controlled, and replaceable
* The backend is production-grade and extensible

---

## ✅ Milestone Completion Status

**Milestone 3: COMPLETED SUCCESSFULLY**

---

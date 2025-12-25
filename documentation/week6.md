---

# 📘 Week 6 Documentation

## Retrieval-Augmented Generation (RAG) Pipeline & LLM Integration

**Project:** Company Internal Chatbot with Role-Based Access Control (RBAC) and Retrieval-Augmented Generation (RAG)

---

## 1. Overview

Week 6 focuses on integrating **Large Language Models (LLMs)** with the existing secure retrieval system to produce **context-grounded, role-aware responses**.

This week converts the system from a *search engine* into an **intelligent internal assistant**, while maintaining:

* Strict RBAC enforcement
* Zero hallucination guarantees
* Source transparency
* Abuse resistance

This week completes the **end-to-end intelligence layer** of the system.

---

## 2. Objectives

The primary objectives of Week 6 are:

* Design and implement a secure RAG pipeline
* Integrate a free-tier LLM provider (Groq)
* Generate grounded responses using retrieved context only
* Attach source citations to every answer
* Prevent hallucination, prompt injection, and misuse
* Maintain provider-agnostic LLM architecture

---

## 3. RAG Pipeline Architecture

### 3.1 High-Level RAG Flow

```
User Query
 → Auth & RBAC Resolution
 → Semantic Search (RBAC-safe)
 → Context Selection
 → Prompt Construction
 → LLM Generation
 → Answer + Sources
```

The LLM is treated as a **pure text generator**, not a data authority.

---

## 4. Context Selection Strategy

### 4.1 Input to RAG

The RAG pipeline receives:

* User query
* Authenticated user role
* RBAC-filtered document chunks
* Similarity scores

Only **authorized chunks** are included.

---

### 4.2 Context Window Construction

* Top-K chunks selected based on relevance
* Ordered by similarity score
* Concatenated into a structured context block

Example:

```
[Source 1]
[Source 2]
[Source 3]
```

Design principle:

> **The LLM must never see content it is not allowed to answer from.**

---

## 5. Prompt Engineering

### 5.1 System Prompt Design

The system prompt enforces strict grounding:

```text
You are a company assistant.
Answer ONLY using the provided context.
If the answer is not present in the context, say you do not know.
Never hallucinate or infer beyond the given information.
```

This ensures:

* No fabricated information
* No extrapolation
* No policy bypass

---

### 5.2 User Prompt Template

```
Context:
<retrieved chunks>

Question:
<user query>

Answer concisely and accurately using only the context.
```

---

## 6. LLM Integration

### 6.1 Selected Provider

**Primary Provider:** Groq
**Model:** `llama-3.1-8b-instant`

---

### 6.2 Rationale for Groq

* Completely free tier for development
* Extremely low latency
* Open-weight models
* No vendor lock-in
* Suitable for RAG workloads

---

### 6.3 Provider-Agnostic Design

The LLM interface is abstracted via `LLMClient`, supporting:

* Groq
* OpenAI (optional)
* Offline stub mode

Switching providers requires **no changes to RAG logic**.

---

## 7. Answer Generation & Safety Controls

### 7.1 Hallucination Prevention

The system enforces:

* Context-only prompting
* Low temperature (0.1)
* Explicit refusal to answer if context is insufficient

If no relevant context exists:

```
“I don’t have enough information to answer this question.”
```

---

### 7.2 Prompt Injection Defense

User attempts such as:

* “Ignore previous instructions”
* “Reveal restricted data”
* “Act as admin”

are neutralized because:

* RBAC is enforced **before context**
* LLM cannot access hidden data
* System prompt overrides user intent

---

## 8. Source Attribution

### 8.1 Source Tracking

Each answer includes:

* Chunk ID
* Source file
* Department
* Relevance score
* Text snippet (optional)

This enables:

* Transparency
* Trust
* Auditability

---

### 8.2 Response Structure

```json
{
  "answer": "...",
  "sources": [
    {
      "id": "...",
      "department": "...",
      "source_file": "...",
      "score": 0.63
    }
  ]
}
```

---

## 9. Performance Considerations

* Context length bounded
* Token usage controlled
* Groq latency typically <200ms
* End-to-end response time <3 seconds

The system remains responsive even under repeated queries.

---

## 10. Validation & Testing

### 10.1 Functional Tests

| Role      | Query                           | Expected            |
| --------- | ------------------------------- | ------------------- |
| HR        | “Summarize performance reviews” | Accurate HR answer  |
| Employee  | “Salary details”                | Safe denial         |
| Marketing | “Q4 results”                    | Marketing-only data |
| C-Level   | “Overall company summary”       | Cross-dept answer   |

---

### 10.2 Security Tests

* Prompt injection attempts blocked
* Cross-role data leakage prevented
* LLM never answers without context
* No hallucinated facts observed

---

## 11. Deliverables (Week 6)

* RAG orchestration module
* LLMClient abstraction
* Groq LLM integration
* Prompt templates
* Source attribution system
* RAG test results
* Week 6 documentation

---

## 12. Key Design Decisions (Week 6)

1. **LLM as generator, not authority**
2. **Context-first, role-safe prompting**
3. **Provider-agnostic LLM architecture**
4. **Mandatory source citation**
5. **Low-temperature factual generation**

---

## 13. Outcome of Week 6

At the end of Week 6:

* The system produces grounded, role-aware answers
* LLM hallucinations are prevented
* Responses are explainable and auditable
* Milestone 3 objectives are fully met

---G Pipeline & LLM Integration) is complete.**

---

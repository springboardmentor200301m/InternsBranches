# Milestone 3: RAG Pipeline & LLM Integration

**Goal:** Build a production-grade Retrieval-Augmented Generation (RAG) pipeline using a free LLM, with role-aware retrieval, prompt augmentation, source attribution, and confidence scoring.

---

## 1. Overview
This milestone focuses on integrating a Large Language Model (LLM) with a Retrieval-Augmented Generation (RAG) pipeline to generate accurate, explainable, and role-based responses from a document corpus.

The system ensures:
- Answers are grounded in retrieved documents
- Sources are explicitly cited
- Confidence scores reflect retrieval quality

---

## 2. System Architecture

### 2.1 High-Level Flow
```text
User Query
   ↓
Authentication & Role Validation
   ↓
Role-Based Document Filtering
   ↓
Semantic Retrieval (Top-K Chunks)
   ↓
Prompt Augmentation (Context + Instructions)
   ↓
LLM Response Generation
   ↓
Source Attribution + Confidence Score
   ↓
Final Answer to User
```

### 2.2 System Prompt
> You are an assistant that answers strictly using the provided context. If the answer is not present in the context, say "Information not available". Always cite sources using document IDs.

### 2.3 Context Template
```text
Context:
{retrieved_chunks}

User Question:
{user_query}

Instructions:
- Use only the context above
- Provide a concise, factual answer
- Add source citations at the end
```

---

## Module 6: RAG Pipeline Implementation (Week 6)

### 1. Objective
Build the retrieval and generation orchestration logic, integrating the Groq LLM with the RBAC-filtered vector store results.

### 2. Output Format
```json
{
    "answer": "...",
    "sources": ["doc_1.md", "doc_2.csv"],
    "confidence": 0.95
}
```

---

## 3. Identified Gaps
- LLM API failures result in generic error messages
- Retrieval failures are not clearly distinguished from generation failures
- User receives no guidance when the system cannot answer a query

---

## Module 5: User Authentication & RBAC Middleware
**Week 5 – Backend Security & Access Control**

---

### 1. Objective
The objective of this module is to design and implement a secure FastAPI backend that supports:
- User authentication using JWT tokens
- Role-Based Access Control (RBAC) enforcement
- Secure session handling
- Access auditing for accountability

This module ensures that only authorized users can access protected resources and that role boundaries are strictly enforced across the application.

---

### 2. System Overview
**Architecture Components**
```text
Client (Streamlit / API Client)
        │
        ▼
FastAPI Backend
  ├── Authentication (JWT)
  ├── RBAC Middleware
  ├── Audit Logging
  └── SQLite User Database
```

---

### 3. User Data Storage
**Database**
- SQLite is used for simplicity and portability.
- Designed for local development and demos.
- Can be replaced with PostgreSQL/MySQL in production.

**JWT Token Details**
- **Algorithm:** HS256
- **Expiry:** Configurable (e.g., 30–60 minutes)
- **Payload Example:**
```json
{
  "sub": "john_doe",
  "role": "finance",
  "exp": 1712345678
}
```

---

### 4. Authentication Endpoints
**`POST /auth/login`**
Authenticates user and returns JWT token.

**Request:**
```text
username=finance_user
password=********
```

**Response:**
```json
{
  "access_token": "jwt_token_here",
  "token_type": "bearer"
}
```


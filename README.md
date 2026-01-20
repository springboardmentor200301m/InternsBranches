Company Internal RAG Chatbot with Role-Based Access Control (RBAC)

Author: Aare Keerthi
Duration: Weeks 1–8
Project Type: Enterprise Internal Chatbot (RAG + RBAC)

1. Project Overview

This project implements a secure internal company chatbot using Retrieval Augmented Generation (RAG) combined with Role-Based Access Control (RBAC).
The system enables employees to query internal documents while ensuring strict access control, data security, and hallucination-resistant AI responses.

The solution is fully offline, cost-free, and production-ready, using open-source models and tools only.

2. Key Features

Role-Based Access Control (RBAC)

Secure JWT Authentication

Semantic Search using Vector Databases

Retrieval Augmented Generation (RAG)

Offline LLM-based Answer Generation

Streamlit Frontend

Source Attribution & Confidence Scoring

Zero unauthorized data leakage

No paid APIs or external services

3. Tech Stack

Programming Language: Python

Backend: FastAPI

Frontend: Streamlit

Embeddings: Sentence Transformers (MiniLM)

Vector Database: ChromaDB

LLM: google/flan-t5-small (offline)

Authentication: JWT + SQLite

Data Storage: Parquet

Version Control: Git & GitHub

Milestone 1: Data Preparation & Ingestion (Weeks 1–2)
4. Objective

Prepare internal company documents for RAG

Clean, chunk, and annotate documents

Assign RBAC metadata

Generate structured dataset for embeddings

5. Environment Setup

Dependencies installed:

pip install sentence-transformers langchain fastapi streamlit pandas chromadb transformers tqdm pyjwt

6. Document Repository & Structure

Mentor-provided repository was cloned and explored.

data/
├── raw/
│   ├── engineering/
│   ├── Finance/
│   ├── HR/
│   ├── marketing/
│   └── general/


Documents were in Markdown (.md) and CSV (.csv) formats.

7. Role-to-Document Mapping

A keyword-based heuristic was used:

ROLE_MAP = {
    'finance': ['finance','qtr','quarter','balance','income','financial'],
    'marketing': ['market','campaign','brand','marketing','seo','ad'],
    'hr': ['hr','employee','payroll','handbook','policy'],
    'engineering': ['architecture','design','api','engineering','tech'],
    'general': ['handbook','policy','company','general']
}

8. Preprocessing Pipeline
Pipeline Steps

Document parsing

Text cleaning

Tokenization

Chunking (300–512 tokens, overlap 64)

Department detection

RBAC metadata assignment

Parquet output generation

9. Chunk Metadata Structure

Each chunk contains:

id

source_file

department

allowed_roles

chunk_seq

text

RBAC rules:

Department docs → [department, c_level]

General docs → [employees, general, c_level]

10. Output & Validation

Output file:

data/processed_chunks.parquet


Validation confirmed:

Correct department classification

Correct RBAC assignment

Proper chunk sequencing

No missing text

High-quality cleaned content

Milestone 2: Vector Database & Semantic Search (Weeks 3–4)
11. Objective

Generate embeddings

Store them in a persistent vector database

Enable RBAC-aware semantic search

12. Embedding Model

Model: sentence-transformers/all-MiniLM-L6-v2

384-dimensional embeddings

Fast and lightweight

Production-ready for RAG

13. Vector Database

Database: ChromaDB

Client: PersistentClient

Storage: Local disk (vectordb_store/)

All document chunks were indexed with:

Embeddings

Original text

Department

Allowed roles

Source file

Chunk sequence

14. RBAC Search Logic
Role Hierarchy
ROLE_HIERARCHY = {
    "c_level": ["finance", "hr", "engineering", "marketing", "general", "employees"],
    "finance": ["finance"],
    "hr": ["hr"],
    "engineering": ["engineering"],
    "marketing": ["marketing"],
    "employees": ["general"]
}


Access is granted only if:

user_role ∩ allowed_roles ≠ ∅

15. Semantic Search Flow

Normalize query

Generate query embedding

Vector similarity search

Apply RBAC filtering

Return authorized results only

Milestone 3: RAG Pipeline & Authentication (Weeks 5–6)
16. Objective

Secure APIs using JWT

Enforce RBAC before retrieval

Generate grounded LLM responses

Prevent hallucinations and data leakage

17. Authentication System

SQLite database for users

JWT tokens issued on login

Role embedded in token

Token required for protected endpoints

Sample users:

finance_user / test

hr_user / test

employee_user / test

admin / admin

18. RAG Pipeline Flow
User Query
   ↓
JWT Authentication
   ↓
Role Extraction
   ↓
RBAC-Filtered Semantic Search
   ↓
Context Construction (Top-K)
   ↓
Prompt Augmentation
   ↓
Offline LLM Inference
   ↓
Answer + Sources + Confidence

19. LLM Integration

Model: google/flan-t5-small

Runs fully offline

No paid APIs

Safe fallback handling if model fails

20. Output Format
{
  "answer": "...",
  "sources": ["Finance/quarterly_financial_report.md"],
  "confidence": 0.33
}

Milestone 4: Frontend & Deployment (Weeks 7–8)
21. Frontend

Built using Streamlit

Secure login screen

Interactive chat interface

Displays user role

Shows sources and confidence

22. Frontend–Backend Integration

Endpoints:

/auth/login

/chat/query

JWT token is attached to every request.

23. Testing & Validation

Validated scenarios:

Role-based access control

Empty queries

Invalid credentials

Token expiration

No accessible documents

LLM failure handling

Results:

Zero unauthorized access

No system crashes

Clean fallback responses

24. Performance Metrics

Retrieval latency: < 500 ms

End-to-end response time: < 3 seconds

Smooth UI performance

25. Security & Git Practices

.env for secrets (not committed)

.gitignore excludes:

Virtual environments

Generated Parquet files

Vector DB storage

Model weights

Only mentor-provided data committed

26. Role-Based Access Summary
Role	Access
HR	Payroll, employee policies
Finance	Financial reports
Engineering	Technical documentation
Employees	General policies
C-Level	Full access
27. Conclusion

All four milestones have been successfully completed.

The project delivers a secure, scalable, and enterprise-ready internal chatbot with:

Strong RBAC enforcement

Hallucination-resistant RAG

Offline LLM inference

Transparent and trusted AI responses

This solution is production-ready, cost-free, and aligned with enterprise AI best practices.

28. How to Run
pip install -r requirements.txt
python download_llm.py
python app.py
streamlit run frontend/app.py

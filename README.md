# 🏢 Company Internal Chatbot with Role-Based Access Control (RBAC)

A **secure internal AI assistant** built using **Retrieval Augmented Generation (RAG)** that allows employees to query company documents while enforcing **strict role-based access control (RBAC)**.

This system is designed to simulate a **real enterprise internal knowledge assistant**, ensuring:

- Users only access documents permitted by their role
- AI responses are grounded strictly in authorized company data
- Unauthorized data is never retrieved or generated
- Every response is traceable to its source

---

## 📌 Core Capabilities

- 🔐 **JWT-based authentication**
- 🧭 **Strict role-based access control**
- 📚 **Semantic search over company documents**
- 🧠 **RAG pipeline with source attribution**
- 🔄 **Pluggable LLM architecture (OpenAI / Groq / Stub)**
- 🗂️ **Vector database with metadata filtering**
- 🧪 **RBAC validation and misuse testing**
- 🖥️ **Streamlit-based user interface for interaction**

---

## 🏗️ High-Level Architecture

```

User (Streamlit / Swagger)
↓
Authentication (JWT)
↓
Role Extraction
↓
RBAC Enforcement
↓
Semantic Retrieval (Vector DB)
↓
Context Assembly
↓
LLM Generation (Optional)
↓
Answer + Sources

```

🔐 **Security and authorization are enforced before retrieval and generation.**

---

## 🛠️ Technology Stack

| Layer | Technology |
|-----|-----------|
| Backend API | FastAPI |
| Frontend | Streamlit |
| Vector Database | Chroma |
| Embeddings | Sentence Transformers |
| LLM | OpenAI / Groq (optional) |
| Authentication | OAuth2 + JWT |
| Database | SQLite |
| Language | Python 3.9+ |

---

## 📁 Project Structure

```

company-chatbot/
│
├── app/                    # Backend application
│   ├── main.py             # FastAPI entry point
│   ├── auth.py             # Authentication & JWT logic
│   ├── rbac.py             # Role hierarchy & permissions
│   ├── search.py           # Semantic search with RBAC filtering
│   ├── rag.py              # RAG pipeline
│   ├── llm_client.py       # LLM abstraction layer
│   ├── vectorstore.py      # Vector DB operations
│
├── frontend/
│   └── app.py              # Streamlit frontend (main UI entry)
│
├── scripts/
│   ├── explore_data.py     # Dataset inspection
│   ├── preprocess_docs.py # Chunking & metadata tagging
│   ├── build_vector_db.py # Embedding generation & indexing
│   ├── test_search.py     # RBAC & retrieval validation
│
├── data/
│   ├── raw/                # Original documents (MD, CSV)
│   ├── processed/          # Chunked & enriched documents
│
├── requirements.txt
├── README.md
└── .env.example

````

---

## 👥 User Roles & Permissions

| Role | Accessible Data |
|----|----|
| Employee | General company handbook |
| Finance | Finance + General |
| HR | HR + General |
| Marketing | Marketing + General |
| Engineering | Engineering + General |
| C-Level | Full access (all departments) |

RBAC rules are enforced **at retrieval time**, not post-generation.

---

## 🚀 Getting Started (Local Setup)

### Step 1: Clone the Repository

```bash
git clone https://github.com/sai-kumar-dev/company-chatbot.git
cd company-chatbot
````

---

### Step 2: Create and Activate Virtual Environment

```bash
python -m venv venv
```

Activate it:

**Windows**

```bash
venv\Scripts\activate
```

**Mac / Linux**

```bash
source venv/bin/activate
```

---

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

Ensure Python version is **3.9 or above**.

---

## 📊 Data Preparation & Indexing (Mandatory)

This phase prepares company documents for semantic search.

---

### Step 4: Explore the Dataset

```bash
python -m scripts.explore_data
```

This script:

* Lists all departments
* Shows document types (Markdown, CSV)
* Previews content
* Confirms data structure

📌 Purpose: understand document scope and role mapping.

---

### Step 5: Preprocess and Chunk Documents

```bash
python -m scripts.preprocess_docs
```

This performs:

* Text cleaning
* Section extraction
* Chunking into ~300-token segments
* Metadata enrichment:

  * department
  * source file
  * allowed roles

Output:

```
data/processed/document_chunks.jsonl
```

Each chunk is RBAC-aware.

---

### Step 6: Build Vector Database

```bash
python -m scripts.build_vector_db
```

This step:

* Generates embeddings using Sentence Transformers
* Indexes chunks into Chroma
* Stores metadata for secure filtering

This step is required **only once**, unless documents change.

---

### Step 7: Validate Search & RBAC Enforcement

```bash
python -m scripts.test_search
```

This script verifies:

* Same query returns different results for different roles
* Unauthorized documents are never retrieved
* Role hierarchy behaves correctly

This is **critical validation evidence**.

---

## 🔐 Backend API (FastAPI)

### Step 8: Start Backend Server

```bash
uvicorn app.main:app --reload
```

Server URL:

```
http://127.0.0.1:8000
```

---

### API Documentation (Swagger UI)

Open:

```
http://127.0.0.1:8000/docs
```

Swagger UI provides:

* OAuth2 password-based login
* Automatic Bearer token handling
* Interactive testing of secured endpoints

---

## 🧠 LLM Configuration (Optional)

By default, the system runs in **stub mode** (no external LLM calls).

### Enable Groq (Recommended Free Tier)

Create `.env` file:

```env
LLM_PROVIDER=groq
GROQ_API_KEY=your_api_key_here
GROQ_MODEL=llama3-8b-8192
```

### Enable OpenAI

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o-mini
```

Restart the backend after changing environment variables.

---

## 🖥️ Frontend (Streamlit Application)

### Step 9: Run Streamlit App

```bash
streamlit run frontend/app.py
```

Application runs at:

```
http://localhost:8501
```

This is the **main user-facing application**.

---

## 🔒 Security & Abuse Protection

* RBAC enforced before retrieval
* JWT required for all protected endpoints
* Prompt injection cannot bypass permissions
* LLM never receives unauthorized context
* Source attribution ensures auditability

---

## 📦 Milestones Overview

| Milestone   | Description                         |
| ----------- | ----------------------------------- |
| Milestone 1 | Data preparation & metadata tagging |
| Milestone 2 | Vector DB & RBAC search             |
| Milestone 3 | Authentication & RAG pipeline       |
| Milestone 4 | Frontend, testing & documentation   |

---

## 🧠 Design Principles

* Security-first architecture
* Authorization before generation
* Explicit access control
* Provider-agnostic LLM integration
* Enterprise-readiness over demos

---

## 📌 Notes for Reviewers

To understand the system quickly:

1. Start with `scripts/test_search.py`
2. Then review `app/search.py`
3. Then `app/rag.py`

These files represent the core logic.

---

## 📈 Future Improvements

* Conversation memory
* Usage analytics & audit logs
* Admin dashboard
* Fine-grained permissions
* Multi-tenant support

---

## ✅ Summary

This project demonstrates:

* Secure AI system design
* Production-style RBAC enforcement
* Reliable RAG implementation
* Clear separation of concerns
* Strong emphasis on correctness and safety

```

# RBAC RAG Chat - Enterprise Internal Chatbot

A production-ready Role-Based Access Control (RBAC) enabled Retrieval-Augmented Generation (RAG) system. This platform provides secure, role-specific access to company documentation through a conversational AI powered by Groq (Llama 3.3).

---

## 🎯 Project Overview

This system is designed for corporate environments where data isolation is critical. It ensures that sensitive documents (Finance, HR, Engineering) are only accessible to authorized personnel, even when queried via an LLM.

- **RBAC**: Multi-layer enforcement from API to Vector Store.
- **RAG**: Intelligent retrieval of relevant chunks for grounded AI responses.
- **High Performance**: Sub-second retrieval and optimized LLM generation.
- **Secure**: Modern hashing and JWT-based identity management.

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Streamlit Frontend                       │
│  - Interactive Chat UI                                       │
│  - Source Transparency & Citations                           │
│  - Performance Metadata Display                              │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP REST API (JWT Authenticated)
┌────────────────────▼────────────────────────────────────────┐
│                     FastAPI Backend                          │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │  Auth Layer │  │ RAG Orchestr.│  │  Semantic        │   │
│  │  (Identity) │  │  Pipeline    │  │  Search (RBAC)   │   │
│  └─────────────┘  └──────────────┘  └──────────────────┘   │
└────────┬──────────────────┬──────────────────┬─────────────┘
         │                  │                  │
    ┌────▼─────┐      ┌────▼──────┐     ┌────▼──────┐
    │ SQLite   │      │  Groq LLM │     │ ChromaDB  │
    │ (Users)  │      │ (Llama 3.3)│     │ (Vectors) │
    └──────────┘      └───────────┘     └───────────┘
```

### Technical Stack
- **Backend**: FastAPI (Python 3.13+)
- **Frontend**: Streamlit
- **Vector DB**: ChromaDB
- **LLM**: Groq API (Llama-3.3-70b-versatile)
- **Embeddings**: Sentence-Transformers (all-MiniLM-L6-v2)
- **Database**: SQLite with SQLAlchemy ORM
- **Security**: PBKDF2-SHA256 (hashlib), JWT (JOSE)

---

## 🔒 Security & RBAC Implementation

### 1. Multi-Layer Enforcement
Access control is implemented at four distinct levels:
1.  **API Layer**: Every request requires a valid JWT. The user's role is extracted from the cryptographically signed token.
2.  **Retrieval Filtering**: When querying ChromaDB, internal filters use the `allowed_roles` metadata to ensure the user never sees unauthorized document chunks.
3.  **LLM Isolation**: Only authorized context is sent to the LLM. The LLM has zero knowledge of documents outside the user's scope.
4.  **C-Level Override**: A specific `c_level` role provides unrestricted access across all organizational departments.

### 2. Password Security
We use Python's built-in `hashlib` with **PBKDF2-HMAC-SHA256** and 100,000 iterations. This setup is NIST-compliant and specifically chosen to be compatible with modern infrastructure (Python 3.13).

---

## 🚀 Getting Started

### Prerequisites
- Python 3.13+
- Groq API Key ([Get one here](https://console.groq.com/))

### Easy Startup (Windows)
We provide automated scripts for a 1-click startup experience:
1.  **Step 1**: Run `.\start_backend.bat` (Initializes DB and starts API)
2.  **Step 2**: Run `.\start_frontend.bat` (Starts Streamlit UI)

### Docker Deployment (Recommended for Production)
```bash
docker-compose up --build
```

### Manual Installation
1.  **Clone & Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
2.  **Environment Setup**:
    Create a `.env` file:
    ```env
    SECRET_KEY=your_secret_key
    GROQ_API_KEY=your_groq_api_key
    ```
3.  **Run Backend**:
    ```bash
    uvicorn app.main:app --reload --port 8000
    ```
4.  **Run Frontend**:
    ```bash
    streamlit run frontend/app.py
    ```

---

## 👥 Default Test Users

| Username     | Password     | Role        | Scope                                  |
|-------------|--------------|-------------|----------------------------------------|
| `ceo`         | `password123`  | `c_level`     | Full Unrestricted Access               |
| `alice_fin`   | `password123`  | `finance`     | Finance Department Documents           |
| `bob_mark`    | `password123`  | `marketing`   | Marketing Department Documents         |
| `carol_hr`    | `password123`  | `hr`          | HR Policies & Employee Info            |
| `dave_eng`    | `password123`  | `engineering` | Technical Specs & Architecture         |
| `erin_emp`    | `password123`  | `employee`    | General Corporate Documentation        |

---

## 🧪 Testing & Performance

### Automated Verification
Run the system-wide integration test to verify RBAC enforcement for all roles:
```bash
python tests/test_rbac.py
```

### Performance Monitoring
The system includes built-in performance tracking:
- **Middleware**: Every API request duration is logged to the console.
- **Headers**: Responses include `X-Process-Time` representing backend latency.
- **Targets**: 
  - Auth: < 50ms
  - Retrieval: < 200ms
  - End-to-End: < 5s (depending on LLM inference)

---

## 📁 Project Structure

```text
.
├── app/                          # Backend Engines
│   ├── main.py                   # FastAPI Gateways & Middleware
│   ├── auth.py                   # PBKDF2 Hashing & JWT Logic
│   ├── rag_pipeline.py           # RAG Orchestration
│   └── semantic_search.py        # RBAC-Aware Retrieval
├── frontend/                     # UI Components
│   └── app.py                    # Streamlit Interface
├── data/                         # Persistent Storage
│   ├── app.db                    # User Identity Data
│   └── vector_db/                # ChromaDB Collections
├── tests/                        # Quality Assurance
│   └── test_rbac.py              # Role Verification Suite
└── documentation/                # Full Technical Guides
    ├── milestone1.md             # Data Prep & Vector DB
    ├── milestone2.md             # Backend Auth & Search
    ├── milestone3.md             # RAG Pipeline & LLM
    └── milestone4.md             # Frontend & Deployment
```

---

## 📖 Extended Documentation

- **[Milestone 1: Data Preparation](documentation/milestone1.md)**: Environment setup and document processing.
- **[Milestone 2: Backend & Search](documentation/milestone2.md)**: Vector DB indexing and RBAC search logic.
- **[Milestone 3: RAG & Security](documentation/milestone3.md)**: LLM integration and JWT authentication.
- **[Milestone 4: Frontend & UI](documentation/milestone4.md)**: Streamlit interface and deployment.

---


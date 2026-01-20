# RBAC-RAG Chatbot

A **secure internal chatbot** that combines **Role-Based Access Control (RBAC)** with **Retrieval Augmented Generation (RAG)** to ensure users can access **only authorized information** while still benefiting from semantic search and Large Language Models (LLMs).

This project is designed as an **enterprise-ready internal knowledge assistant**, suitable for organizations handling sensitive departmental data.

---

## 🌟 Project Vision & Overview

The goal of this project is to build a **secure, intelligent internal chatbot** for organizations where information access must be tightly controlled.

Instead of allowing all users to query all documents, the system:

* Understands **who the user is** (role-based)
* Retrieves **only authorized documents**
* Generates responses **strictly grounded in permitted data**

This ensures **data confidentiality**, **compliance**, and **trustworthy AI responses**.

---

## 🔄 How the System Works (End-to-End)

1. Internal documents are collected and organized by department
2. Documents are cleaned, normalized, and split into meaningful chunks
3. Each chunk is tagged with **role-based access metadata**
4. Chunks are converted into **vector embeddings** for semantic search
5. User submits a query along with their role
6. Semantic search retrieves relevant chunks
7. **RBAC filtering removes unauthorized results**
8. Authorized context is sent to the LLM using **RAG**
9. A secure, role-aware response is generated

---

## 🚀 Project Overview

Traditional chatbots often return information without considering **user permissions**, which can lead to data leakage. This project solves that problem by:

* Enforcing **RBAC at retrieval time**
* Allowing **semantic search** over internal documents
* Ensuring **LLM responses are grounded only in authorized data**

The chatbot adapts its responses based on the **user’s role** (Admin, HR, Finance, Engineering, Marketing, Employee, etc.).

---

## 🧩 System Architecture (High-Level)

* **Document Layer** → Internal company documents
* **Preprocessing Layer** → Cleaning, chunking, tagging
* **Embedding Layer** → Sentence-transformer embeddings
* **Vector Database** → Chroma / Qdrant
* **Access Control Layer** → Role-based filtering
* **LLM Layer** → RAG-powered response generation

---

---

## 🏗️ Data Preparation & RBAC Mapping

### 🎯 Objective

Prepare internal documents for semantic search while ensuring **role-level access control**.

### ✅ Key Tasks Completed

* Explored and analyzed company documents
* Organized documents by departments (Finance, HR, Engineering, Marketing, General)
* Cleaned and normalized raw files
* Chunked documents into smaller, meaningful text units
* Created **role-to-document mapping**
* Added metadata for RBAC filtering

### 📁 Important Outputs

* `docs_repo/` – Raw departmental documents
* `preprocessing/` – Scripts for cleaning and chunking
* `processed/` –

  * `chunks.jsonl`
  * `chunks_tagged.jsonl`
  * `qa_summary.json`
* `mappings/role_document_mapping.yaml`

### 🔐 Security Considerations

* No secrets stored in code
* API keys handled via `.env` (ignored by Git)

---

## 🧠 Semantic Search with RBAC Enforcement

### 🎯 Objective

Enable **semantic retrieval** while enforcing **role-based access control during search**.

### ✅ Key Tasks Completed

* Integrated `sentence-transformers (all-MiniLM-L6-v2)` for embeddings
* Built vector database layer using **Chroma / Qdrant**
* Stored embeddings along with RBAC metadata
* Implemented **cosine similarity-based semantic search**
* Applied **RBAC filtering at retrieval time**
* Validated access control across multiple roles

### 🔑 RBAC Enforcement Logic

* Each document chunk is tagged with allowed roles
* Even if a chunk is semantically relevant, it is **excluded** if the user role is unauthorized
* Higher roles inherit permissions from lower roles

### 📂 Key Files

* `embeddings.py` – Embedding generation
* `vector_db.py` – Vector database initialization & queries
* `semantic_search.py` – Semantic similarity search
* `rbac_search.py` – RBAC-aware retrieval logic

---

## 🔐 Security Best Practices

* API keys stored in environment variables
* `.env` excluded via `.gitignore`
* Vector DB storage directories not pushed to GitHub
* Clear separation of **logic vs secrets**

---

## 🛠️ Tech Stack

* **Language:** Python
* **LLMs:** OpenRouter (LLaMA 3.1), Hugging Face (FLAN-T5)
* **Embeddings:** Sentence-Transformers (MiniLM)
* **Vector DB:** Chroma / Qdrant
* **Security:** RBAC, environment variables

---

## 📈 Project Progress & Roadmap

### ✅ Implemented

* Role-based document organization
* Document preprocessing and chunking
* Role-to-document access mapping
* Semantic search using vector embeddings
* RBAC-enforced retrieval pipeline
* Secure LLM integration using RAG

### ⏳ In Progress / Planned

* Authentication & JWT-based login
* FastAPI backend APIs
* Role-aware request handling middleware
* UI / dashboard integration
* Audit logging and monitoring

---

## 📄 How to Run (Basic)

```bash
pip install -r requirements.txt
python preprocessing/preprocess.py
python embeddings.py
python rbac_search.py
```

> Note: Create a `.env` file with required API keys before running.

---

## ⭐ Why This Project Matters

* Demonstrates **AI + Security integration**
* Solves real-world enterprise problems
* Resume and interview ready
* Aligns with modern RAG-based architectures

---

## 👤 Author

**Venkata Harika**
B.Tech CSE | AI | RBAC | RAG

---

> ⚠️ This repository intentionally excludes secrets and sensitive credentials.

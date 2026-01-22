# 🤖 Company Internal Chatbot with Role-Based Access Control (RBAC)

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)


A secure internal chatbot system powered by **Retrieval-Augmented Generation (RAG)** that provides role-based access to company documents using semantic search and AI.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [System Architecture](#system-architecture)
- [Technology Stack](#technology-stack)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [Security](#security)
- [Performance](#performance)


---

## 🎯 Overview

This project implements a comprehensive internal chatbot system for organizations that need to:
- ✅ Provide employees with instant access to company information
- ✅ Enforce strict role-based data access policies
- ✅ Use AI to understand natural language questions
- ✅ Deliver accurate, context-aware responses with source citations
- ✅ Maintain complete audit trails for compliance

Built with modern Python frameworks and AI technologies, this system demonstrates production-ready implementation of authentication, authorization, and intelligent information retrieval.

---

## ✨ Features

### 🔐 **Security & Authentication**
- JWT-based authentication with token expiration
- bcrypt password hashing for secure storage
- Role-based access control (RBAC) at API level
- Comprehensive audit logging

### 🤖 **AI-Powered Search**
- Semantic search using sentence transformers
- FAISS vector database for efficient retrieval
- Role-filtered document access
- Source attribution for transparency

### 👥 **Multi-Role Support**
- **Finance**: Access to financial reports and budgets
- **Marketing**: Access to campaigns and market analysis
- **HR**: Access to employee data and policies
- **Engineering**: Access to technical documentation
- **C-Level**: Access to ALL documents
- **Employees**: Access to general company handbook

### 💻 **User Interface**
- Clean Streamlit web interface
- Interactive chat with message history
- Real-time document retrieval
- Source citation display

### 📊 **Admin Features**
- Audit log viewing (C-Level only)
- User management capabilities
- System health monitoring

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Streamlit Frontend                      │
│              (User Interface & Authentication)               │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           │ HTTP/REST API
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Backend                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │     JWT      │  │     RBAC     │  │    Audit     │      │
│  │     Auth     │  │  Middleware  │  │   Logging    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└──────────────────────────┬──────────────────────────────────┘
                           │
          ┌────────────────┴────────────────┐
          │                                 │
          ▼                                 ▼
┌──────────────────┐            ┌──────────────────────┐
│   SQLite         │            │   RAG Pipeline       │
│   Database       │            │   ┌──────────────┐   │
│   - Users        │            │   │  Embeddings  │   │
│   - Audit Logs   │            │   │   (384-dim)  │   │
└──────────────────┘            │   └──────────────┘   │
                                │   ┌──────────────┐   │
                                │   │  FAISS Index │   │
                                │   │  (Vector DB) │   │
                                │   └──────────────┘   │
                                │   ┌──────────────┐   │
                                │   │  Document    │   │
                                │   │  Metadata    │   │
                                │   └──────────────┘   │
                                └──────────────────────┘
```

---

## 🛠️ Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **Backend Framework** | FastAPI | 0.104+ |
| **Frontend** | Streamlit | 1.28+ |
| **Database** | SQLite | 3 |
| **ORM** | SQLAlchemy | 2.0+ |
| **Authentication** | PyJWT | 2.8+ |
| **Password Hashing** | passlib[bcrypt] | 1.7+ |
| **Vector Database** | FAISS | Latest |
| **Embeddings** | sentence-transformers | Latest |
| **Embedding Model** | all-MiniLM-L6-v2 | 384 dimensions |
| **Language** | Python | 3.8+ |

---

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Git

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/internal-chatbot-rbac.git
cd internal-chatbot-rbac
```

### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install fastapi uvicorn sqlalchemy bcrypt pyjwt
pip install streamlit
pip install faiss-cpu sentence-transformers numpy
pip install requests python-multipart
```

### Step 4: Set Up the Project

```bash
# Create vector database from documents
python generate_embeddings.py

# Seed test users
python seed_users.py
```

---

## 🚀 Quick Start

### 1. Start the Backend API

```bash
python main.py
```

The API will be available at: `http://localhost:8000`  
API Documentation: `http://localhost:8000/docs`

### 2. Start the Frontend (New Terminal)

```bash
streamlit run app.py
```

The web interface will open automatically at: `http://localhost:8501`

### 3. Login with Test Credentials

| Username | Password | Role |
|----------|----------|------|
| finance_user | finance123 | Finance |
| marketing_user | marketing123 | Marketing |
| hr_user | hr123 | HR |
| engineering_user | engineering123 | Engineering |
| employee_user | employee123 | Employees |
| clevel_user | clevel123 | C-Level |

---

## 📖 Usage

### Using the Web Interface

1. **Login**: Enter your username and password
2. **Ask Questions**: Type natural language questions in the chat
3. **View Sources**: Expand source citations to see which documents were used
4. **Chat History**: Scroll through previous conversations
5. **Logout**: Click the logout button in the sidebar

### Using the API

#### 1. Login

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"finance_user","password":"finance123"}'
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "username": "finance_user",
  "role": "Finance",
  "expires_in": 1800
}
```

#### 2. Query the Chatbot

```bash
curl -X POST "http://localhost:8000/api/query" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"query":"What are the Q3 financial results?"}'
```

Response:
```json
{
  "query": "What are the Q3 financial results?",
  "response": "Based on your Finance role access, I found...",
  "sources": [
    {
      "source": "Q3_Financial_Report.md",
      "department": "finance"
    }
  ],
  "role": "Finance",
  "timestamp": "2026-01-08T12:00:00",
  "context_used": true
}
```

---

## 📚 API Documentation

### Authentication Endpoints

#### `POST /api/auth/login`
Authenticate user and receive JWT token

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:** LoginResponse with access_token

---

#### `GET /api/auth/me`
Get current user information

**Headers:** `Authorization: Bearer {token}`

**Response:** User information including role

---

### Query Endpoints

#### `POST /api/query`
Submit a query to the RAG-powered chatbot

**Headers:** `Authorization: Bearer {token}`

**Request Body:**
```json
{
  "query": "string"
}
```

**Response:** AI-generated response with sources

---

### Protected Endpoints

#### `GET /api/finance/reports`
**Access:** Finance, C-Level only

#### `GET /api/marketing/campaigns`
**Access:** Marketing, C-Level only

#### `GET /api/hr/employees`
**Access:** HR, C-Level only

#### `GET /api/audit/logs`
**Access:** C-Level only

---

### Utility Endpoints

#### `GET /`
Root endpoint with API information

#### `GET /health`
Health check and system status

---

## 🧪 Testing

### Run Authentication Tests

```bash
python test_auth.py
```

### Run RAG Pipeline Tests

```bash
python rag_pipeline.py
```

### Run Complete Integration Tests

```bash
python test_integration.py
```

**Expected Output:**
- Total Tests: 30+
- Success Rate: >80%
- Performance: All queries < 3s

---

## 📁 Project Structure

```
internal-chatbot-rbac/
│
├── app.py                      # Streamlit frontend application
├── main.py                     # FastAPI backend server
├── auth.py                     # JWT authentication logic
├── database.py                 # SQLAlchemy models & database
├── rag_pipeline.py            # RAG query engine
├── generate_embeddings.py     # Vector database creation
├── seed_users.py              # Populate test users
├── test_auth.py               # Authentication tests
├── test_integration.py        # End-to-end integration tests
│
├── data/                       # Company documents
│   ├── finance/               # Financial reports
│   ├── marketing/             # Marketing documents
│   ├── hr/                    # HR documents
│   ├── engineering/           # Technical docs
│   └── general/               # General handbook
│
├── vector_db/                  # FAISS vector database
│   ├── faiss_index.bin        # Vector embeddings
│   └── metadata.pkl           # Document metadata
│
├── rbac_chatbot.db            # SQLite database
│
├── requirements.txt            # Python dependencies
├── README.md                   # This file
└── LICENSE                     # MIT License
```

---

## 🔒 Security

### Authentication
- **JWT Tokens**: HS256 algorithm with SECRET_KEY
- **Token Expiration**: 30 minutes (configurable)
- **Password Hashing**: bcrypt with cost factor 12

### Authorization
- **RBAC Middleware**: Enforces role-based access on every request
- **Role Hierarchy**: C-Level > Department Roles > Employees
- **Data Isolation**: Users only see documents they're authorized to access

### Audit Logging
- All authentication attempts logged
- All API requests tracked with user, timestamp, and action
- C-Level users can view complete audit trail

### Best Practices
- Never commit SECRET_KEY to version control
- Use environment variables for sensitive configuration
- Implement rate limiting in production
- Use HTTPS in production
- Regular security audits

---

## ⚡ Performance

### Metrics

| Metric | Target | Achieved |
|--------|--------|----------|
| Login Response Time | < 200ms | ✅ |
| Token Validation | < 50ms | ✅ |
| Vector Search | < 500ms | ✅ |
| End-to-End Query | < 3s | ✅ |
| Database Size | Minimal | 0.08 MB |

### Optimization Tips

1. **Vector Database**: FAISS is optimized for fast similarity search
2. **Embeddings**: Cached model loaded once at startup
3. **Database**: SQLite with indexes on frequently queried columns
4. **API**: FastAPI with async support where possible

---

---

## 📊 Statistics

- **Lines of Code**: ~2000+
- **Test Coverage**: 80%+
- **API Endpoints**: 10+
- **Supported Roles**: 6
- **Response Time**: < 3s
- **Development Time**: 8 weeks

---

**Made by [Lokeshwar G]**

**Last Updated**: January 21, 2026

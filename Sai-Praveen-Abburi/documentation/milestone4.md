# Milestone 4: Frontend & Deployment

**Weeks 7–8**

This milestone focuses on user-facing interaction, system integration, and production readiness of the RBAC-enabled RAG chatbot.

---

## Module 7: Streamlit Frontend Development (Week 7)

### 1. Objective
To build an interactive, role-aware frontend that allows authenticated users to:
- Log in securely
- Ask questions
- View AI-generated answers
- Transparently inspect source documents used in responses

The frontend strictly reflects backend RBAC decisions and never bypasses security rules.

---

### 2. System Overview

**Frontend Architecture**
```text
Streamlit UI
 ├── Login Screen
 ├── JWT Session Management
 ├── Chat Interface
 ├── Source Attribution Panel
 └── Backend API Client
        │
        ▼
FastAPI Backend (Auth + RBAC + RAG)
```

---

### 3. Streamlit Application Design

**Key UI Sections**

#### 3.1 Login Interface
- Username + password login
- OAuth2 password flow compatible
- Displays authentication errors clearly
- Stores JWT token securely in session state

#### 3.2 User Info Panel
Displayed in sidebar after login:
- Username
- Role
- Logout option

This ensures role transparency to the user.

---

### 4. Chat Interface

**Features**
- Multi-turn chat support
- Persistent session-based conversation history
- Input validation (empty queries blocked)
- Loading indicator while processing

**Message Flow**
```text
User Query
 ↓
Backend /rag API
 ↓
RBAC-filtered documents
 ↓
LLM response
 ↓
Answer + Sources rendered
```

---

### 5. Source Attribution & Transparency

**Source Display**
Each response includes:
- Document ID
- Department
- Source file name
- Relevance score
- Text snippet used

---

### 6. Backend Integration

**API Client Responsibilities**
- Attach JWT token to requests
- Handle authentication errors
- Display backend errors safely
- Prevent unauthorized calls
---

## Module 8: Deployment & Final Testing (Week 8)

### 1. Objective
Ensure the system is production-ready through Dockerization, performance testing, and final security audits.

### 2. Tasks
- **Docker Integration**: Create Dockerfile and Docker Compose for easy deployment.
- **Integration Testing**: Run the full suite of RBAC verification tests.
- **Performance Benchmarking**: Verify sub-second retrieval and stable LLM generation times.
- **Documentation Finalization**: Complete technical guides and user manuals.

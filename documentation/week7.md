---

# 📘 Week 7 Documentation

## Frontend Development & Secure System Integration

**Project:** Company Internal Chatbot with Role-Based Access Control (RBAC) and RAG

---

## 1. Overview

Week 7 introduces the **user-facing layer** of the system.
The goal is to expose the secure RAG backend through an **intuitive, role-aware web interface** without weakening security guarantees.

This week converts the project from a *backend system* into a **usable internal product**.

---

## 2. Objectives

The objectives of Week 7 are:

* Build a clean, minimal frontend using Streamlit
* Implement secure login flow
* Integrate frontend with FastAPI backend
* Display role context to users
* Show answer citations transparently
* Preserve RBAC enforcement end-to-end
* Maintain session safety and logout capability

---

## 3. Frontend Architecture

### 3.1 Technology Choice

**Frontend Framework:** Streamlit
**Backend API:** FastAPI
**Communication:** REST (JSON)

**Rationale:**

* Fast prototyping
* Python-native
* Excellent for internal tools
* No frontend framework overhead

---

### 3.2 Frontend–Backend Interaction

```
Streamlit UI
  → Login Request (/auth/login)
  → JWT Token Stored in Session
  → RAG Request (/rag)
  → Answer + Sources Returned
  → UI Rendering
```

RBAC is enforced **only on backend**, never trusted from frontend.

---

## 4. Authentication Flow (Frontend)

### 4.1 Login Screen

Users provide:

* Username
* Password

Flow:

1. Credentials sent to `/auth/login`
2. Backend returns JWT token
3. Token stored in Streamlit session state
4. User role extracted from backend response

---

### 4.2 Session Management

* JWT stored in `st.session_state`
* Token sent via `Authorization: Bearer <token>`
* Logout clears session state
* No token persistence on disk

---

## 5. Chat Interface Design

### 5.1 Core UI Components

* Role banner (shows current role)
* Chat history display
* Input text box
* Send button
* Source citation panel
* Logout button

---

### 5.2 Chat Workflow

1. User submits a question
2. UI sends request to `/rag`
3. Backend performs:

   * Auth validation
   * RBAC enforcement
   * Retrieval
   * LLM generation
4. UI renders:

   * Answer
   * Sources used

---

## 6. Source Transparency

### 6.1 Source Display

Each response includes:

* Source file name
* Department
* Relevance score

Sources are shown in:

* Expandable section
* Read-only format

This reinforces:

* Trust
* Explainability
* Enterprise readiness

---

## 7. Security Considerations (Frontend)

### 7.1 Zero Trust UI

The frontend:

* Never decides access
* Never filters documents
* Never constructs context
* Never decodes roles manually

All security decisions are made server-side.

---

### 7.2 Error Handling

Handled gracefully:

* Invalid login
* Expired tokens
* Backend unavailability
* Empty responses

User sees:

* Clear error messages
* No stack traces
* No sensitive info leaks

---

## 8. Integration Testing

### 8.1 Role-Based UI Validation

| Role      | Query               | Expected |
| --------- | ------------------- | -------- |
| Employee  | Salary info         | Denied   |
| HR        | Performance reviews | Allowed  |
| Marketing | Q4 campaigns        | Allowed  |
| Finance   | HR records          | Denied   |
| C-Level   | Cross-dept summary  | Allowed  |

---

### 8.2 UX Validation

* Login/logout works reliably
* Chat remains responsive
* History preserved per session
* Sources always shown
* No UI crashes observed

---

## 9. Performance & Stability

* Frontend latency dominated by backend RAG
* UI overhead negligible
* Groq inference latency acceptable
* System remains interactive under repeated queries

---

## 10. Deliverables (Week 7)

* Streamlit frontend application
* Login & session handling logic
* Secure API client integration
* Role-aware UI rendering
* Source citation UI
* Frontend error handling
* Week 7 documentation

---

## 11. Key Design Decisions

1. **Backend-only security enforcement**
2. **Stateless frontend sessions**
3. **Minimal UI to reduce attack surface**
4. **Explicit role visibility**
5. **Mandatory source transparency**

---

## 12. Outcome of Week 7

At the end of Week 7:

* Users can securely log in
* Queries flow end-to-end through RAG
* RBAC is preserved across UI and backend
* Responses are explainable and auditable
* System is ready for final testing and deployment

---

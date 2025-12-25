---

# 📘 Week 5 Documentation

## User Authentication, Authorization & RBAC Middleware

**Project:** Company Internal Chatbot with Role-Based Access Control (RBAC) and Retrieval-Augmented Generation (RAG)

---

## 1. Overview

Week 5 focuses on building a **secure authentication and authorization layer** for the system.
This week ensures that **every request is tied to a verified user identity and role**, and that **RBAC is enforced consistently across all protected endpoints**.

This milestone transitions the system from an internal prototype to an **enterprise-grade secured application**.

---

## 2. Objectives

The primary objectives of Week 5 are:

* Implement user authentication using industry-standard mechanisms
* Secure backend APIs using JWT-based authorization
* Enforce RBAC via backend middleware
* Prevent role spoofing and token misuse
* Prepare the system for safe RAG + LLM usage
* Enable auditability and access traceability

---

## 3. Authentication Architecture

### 3.1 Authentication Flow

```
Username + Password
 → Credential Verification
 → JWT Token Issuance
 → Token-Based Access to APIs
```

Authentication is **state-less**, scalable, and backend-controlled.

---

## 4. User Data Management

### 4.1 User Storage

A lightweight relational database (SQLite) is used to store:

* User credentials
* User roles
* Account metadata

Fields include:

* `id`
* `username`
* `hashed_password`
* `role`
* `created_at`

---

### 4.2 Password Security

* Passwords are never stored in plain text
* Secure hashing is applied using industry-standard cryptographic hashing
* Password verification occurs server-side only

Design principle:

> **Passwords are write-only secrets.**

---

## 5. JWT-Based Authentication

### 5.1 Token Design

Upon successful login, the backend issues a **JSON Web Token (JWT)** containing:

* User identifier (`sub`)
* Token expiration timestamp
* Minimal identifying information

**Important security decision:**

> User role is **resolved from the database per request**, not trusted from the JWT.

---

### 5.2 Token Usage

* Token is sent in the `Authorization: Bearer <token>` header
* Backend validates token on every protected request
* Expired or malformed tokens are rejected

---

## 6. OAuth2 Password Flow (FastAPI)

### 6.1 Rationale

OAuth2 Password Flow is used because:

* It is a standard pattern for internal applications
* Works seamlessly with FastAPI
* Integrates cleanly with Swagger UI

---

### 6.2 Login Endpoint

```
POST /auth/login
```

Responsibilities:

* Validate credentials
* Generate JWT
* Return access token and token type

---

## 7. Authorization & RBAC Middleware

### 7.1 Middleware Responsibility

The RBAC middleware is responsible for:

* Extracting JWT from request
* Validating token integrity
* Loading the authenticated user from database
* Attaching user context to request lifecycle

---

### 7.2 Request Context Injection

For every protected request:

```text
request.state.user = {
  id,
  username,
  role
}
```

This ensures:

* Downstream services rely on trusted backend data
* Role spoofing via token manipulation is impossible

---

## 8. RBAC Enforcement Strategy

### 8.1 Separation of Concerns

RBAC enforcement is **not** mixed into:

* Frontend logic
* LLM prompts
* Vector database queries directly

Instead:

* Authentication resolves identity
* RBAC enforces authorization
* Retrieval logic uses trusted role context

---

### 8.2 Zero-Trust Principle

Even with a valid token:

* Every request re-checks authorization
* Role is fetched fresh from the database
* No cached assumptions are made

---

## 9. Security Threat Mitigation

### 9.1 Prevented Attack Vectors

| Threat                  | Mitigation               |
| ----------------------- | ------------------------ |
| Token forgery           | Signature verification   |
| Role spoofing           | DB-based role resolution |
| Unauthorized API access | JWT validation           |
| Expired token reuse     | Expiry enforcement       |
| Frontend bypass         | Backend-only enforcement |

---

### 9.2 Failure Handling

* Invalid credentials → `401 Unauthorized`
* Missing token → `401 Unauthorized`
* Expired token → `401 Unauthorized`
* Invalid token → `403 Forbidden`

No sensitive error details are exposed.

---

## 10. Validation & Testing

### 10.1 Authentication Tests

* Valid login returns JWT
* Invalid password rejected
* Non-existent user rejected

---

### 10.2 Authorization Tests

* Protected endpoints inaccessible without token
* Role correctly resolved per request
* JWT tampering attempts fail

---

### 10.3 Integration Tests

* Auth + semantic search integration verified
* RBAC enforced consistently across endpoints

---

## 11. Deliverables (Week 5)

* Authentication service (`/auth/login`, `/auth/me`)
* JWT token management
* RBAC middleware
* User database with sample accounts
* Security validation tests
* Week 5 documentation

---

## 12. Key Design Decisions (Week 5)

1. **JWT for stateless auth**

   * Scalable and standard

2. **Role fetched from DB, not JWT**

   * Prevents privilege escalation

3. **Backend-only RBAC**

   * Eliminates client-side trust

4. **OAuth2 password flow**

   * Industry-accepted pattern

---

## 13. Outcome of Week 5

At the end of Week 5:

* All backend APIs are secured
* Users are authenticated and authorized reliably
* RBAC enforcement is centralized and consistent
* The system is safe for RAG + LLM interaction

---

## 🛠️ Implementation Highlights (Technical Report)

### 🔹 1. Security Architecture
* **Authentication:** Implemented **OAuth2 with Password Flow**. Passwords are hashed using `bcrypt` before storage.
* **Session Management:** Uses **JWT (JSON Web Tokens)** with an expiration time of 30 minutes. The user's role is encoded directly into the token payload for stateless verification.

### 🔹 2. RAG Pipeline Optimization
* **Vector Store:** utilized **ChromaDB** for local persistence of embeddings.
* **Embeddings:** Applied `sentence-transformers/all-MiniLM-L6-v2` for efficient semantic search.
* **Hybrid Search Strategy:**
    1.  **Strict Mode:** Searches internal documents first with a high similarity threshold.
    2.  [cite_start]**Fallback Mode:** If no documents match (e.g., "Capital of France"), the system seamlessly switches to General AI knowledge[cite: 12, 16, 27].

### 🔹 3. Role-Based Access Control (RBAC) Logic
* **Filter Mechanism:** RBAC is enforced at the **Database Query Level**.
* **Logic:** `results = vector_db.similarity_search(query, filter={"$or": [{"dept": user_role}, {"dept": "General"}]})`
* [cite_start]**Outcome:** A Finance user is physically unable to retrieve HR documents, ensuring 100% data isolation[cite: 14, 15, 20].

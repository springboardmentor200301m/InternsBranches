# Milestone 2: Backend Auth & Search (Weeks 3–4)

---

## Module 3: Vector Database & Embedding Generation (Week 3)

### Objective
Generate embeddings for all document chunks from GitHub documents, index them into a vector database, and enable semantic search functionality.

---

### Tasks Completed
1. **Select and Download Embedding Model**
   - Used `sentence-transformers/all-MiniLM-L6-v2` for generating semantic embeddings of text chunks.
2. **Generate Vector Embeddings**
   - Converted each pre-processed document chunk into a fixed-size vector representation.
   - Ensured embeddings capture semantic meaning for effective similarity search.
3. **Initialize Vector Database**
   - Set up Chroma as the vector storage backend.
   - Configured database to store embeddings along with associated metadata.
4. **Index Embeddings with Metadata**
   - Indexed each chunk with metadata including:
     - `department`
     - `source_file`
     - `chunk_index`
     - `allowed_roles`
     - `source_path`
5. **Implement Semantic Search Functionality**
   - Developed search interface to query vector database and return top-k most relevant chunks.
   - Integrated search scoring for ranking results by similarity.

### Deliverables
- Embedding generation module ready for any document set.
- Populated vector database containing all document chunks with metadata.
- Semantic search functionality with query interface.
- Performance benchmarking report demonstrating search accuracy and speed.

---

## Module 4: Role-Based Search & Query Processing (Week 4)

### Objective
Implement role-based access control (RBAC) at the search level to enforce secure, role-specific document access.

---

### Tasks Completed
1. **Build RBAC Filtering Logic**
   - Filter search results based on user roles and allowed roles for each chunk.
   - Ensure unauthorized roles do not receive access to restricted documents.
2. **Implement Role Hierarchy**
   - Defined hierarchy:
     - **C-Level**: access to all documents.
     - **Department Staff**: access limited to their department documents.
     - **General Employee**: access limited to general documents only.
3. **Preprocess and Normalize Queries**
   - Standardized incoming user queries for consistent search results.
   - Handled text normalization, tokenization, and case standardization.
4. **Select Most Relevant Chunks per Query**
   - Semantic search returns top-k results.
   - RBAC filter ensures only permitted chunks are displayed.
5. **Test and Validate Role-Based Access**
   - Verified access control:
     - Finance users cannot access HR documents.
     - Department-specific restrictions correctly enforced.
     - C-Level users can access all documents.

### Deliverables
- Role-based access control filtering module.
- Query processing and normalization utilities.
- Role permission configuration and hierarchy definition.
- Role-based access validation test suite with results.



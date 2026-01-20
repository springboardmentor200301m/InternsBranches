## Performance Optimization

The following optimizations were applied to ensure efficient and responsive system behavior:

1. **Top-K Context Limiting**
   Only the top 3 most relevant document chunks are sent to the LLM. This reduces prompt size, improves response time, and minimizes hallucination risk.

2. **RBAC Enforcement Before LLM Invocation**
   Role-based access control is applied before document retrieval. If no authorized documents are found, the LLM is not called, preventing unnecessary computation and API usage.

3. **Local Vector Database**
   ChromaDB is used in persistent local mode, enabling fast similarity search without network latency.

4. **Model Caching**
   The sentence-transformers embedding model is cached locally after the first load, eliminating repeated downloads and reducing startup time.

5. **Lightweight Embedding Model**
   The all-MiniLM-L6-v2 model was selected due to its balance of speed, low memory usage, and acceptable semantic accuracy.

These optimizations ensure the system performs efficiently while maintaining accuracy and security.

# API Specification

## semantic_search(query, user_role, k)
- Description: Performs RBAC-filtered semantic search
- Input:
  - query: string
  - user_role: string
  - k: int
- Output:
  - List of authorized document chunks

## build_rag_context(chunks)
- Description: Builds context and source metadata
- Output:
  - Context text
  - Source list

## query_llm(prompt, system_prompt)
- Description: Sends RAG prompt to LLM
- Handles:
  - API failure
  - Timeout

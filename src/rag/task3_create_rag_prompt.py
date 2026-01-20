"""
RAG Prompt Builder – Milestone 4
"""

def create_rag_prompt(query: str, retrieved_chunks: list, role: str):
    context = "\n\n".join(
        chunk.get("content", "")
        for chunk in retrieved_chunks
        if chunk.get("content")
    )

    prompt = f"""
You are an internal company assistant.

User Role: {role}

Use ONLY the information below to answer the question.

Context:
{context}

Question:
{query}

Answer:
"""
    return prompt.strip()

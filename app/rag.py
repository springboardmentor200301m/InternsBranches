# app/rag.py
from typing import List, Dict, Any

from .search import semantic_search
from .llm_client import LLMClient
from .schemas import Source


def build_context_block(hits: List[Dict[str, Any]]) -> str:
    """
    Turn search hits into a formatted context string for the LLM.
    """
    blocks = []
    for i, hit in enumerate(hits, start=1):
        meta = hit["metadata"]
        source_id = hit["id"]
        department = meta.get("department", "")
        source_file = meta.get("source_file", "")
        text = hit["text"]

        block = f"""[SOURCE {i}]
id: {source_id}
department: {department}
file: {source_file}

{text}
"""
        blocks.append(block.strip())

    return "\n\n".join(blocks)


def build_rag_prompt(query: str, hits: List[Dict[str, Any]]) -> str:
    context_block = build_context_block(hits)

    prompt = f"""
You are an internal chatbot for a fintech company.
You answer employee questions strictly based on the provided sources.
You must:
- Use only the context below (do NOT hallucinate).
- If the answer is not present, clearly say you don't know.
- When you give an answer, reference which SOURCE numbers you used (e.g., "Based on SOURCE 1 and SOURCE 3").

-------------------- CONTEXT START --------------------
{context_block}
-------------------- CONTEXT END ----------------------

User question:
{query}

Now provide a helpful, concise answer for the user.
If relevant, mention SOURCE numbers in your explanation.
"""
    return prompt.strip()


async def generate_rag_answer(
    query: str,
    user_role: str,
    top_k: int = 4,
) -> tuple[str, List[Source]]:
    """
    Full RAG pipeline:
      - semantic_search with RBAC
      - prompt construction
      - LLM call
      - source packaging
    """
    hits = semantic_search(query, user_role=user_role, top_k=top_k)

    # Build source objects for API response
    sources: List[Source] = []
    for h in hits:
        meta = h["metadata"]
        sources.append(
            Source(
                id=h["id"],
                department=meta.get("department", ""),
                source_file=meta.get("source_file", ""),
                score=h["score"],
                snippet=h["text"][:300].replace("\n", " ") + ("..." if len(h["text"]) > 300 else ""),
            )
        )

    # If no hits (RBAC blocked or irrelevant), we can short-circuit
    if not hits:
        return (
            "I couldn't find any relevant information for your role in the available documents.",
            sources,
        )

    # Build prompt and call LLM
    prompt = build_rag_prompt(query, hits)
    client = LLMClient()
    answer = await client.generate(prompt)

    return answer, sources

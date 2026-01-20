"""
TASK 1: Source Attribution + Structured Context
"""

from src.search.semantic_search_role import role_filtered_search


def build_llm_context(query: str, user_role: str, top_k: int = 3):
    """
    Builds structured context WITH source metadata.
    Returns:
    - context_text (str)
    - sources (list of dicts)
    """

    chunks = role_filtered_search(
        query=query,
        user_role=user_role,
        top_k=top_k
    )

    if not chunks:
        return "", []

    context_blocks = []
    sources = []

    for idx, chunk in enumerate(chunks, start=1):
        doc_name = chunk.get("source")
        dept = chunk.get("department")

        context_blocks.append(
            f"""[Document {idx}]
Document: {doc_name}
Department: {dept}

{chunk.get("content").strip()}
"""
        )

        sources.append({
            "document": doc_name,
            "department": dept
        })

    context_text = "\n---\n".join(context_blocks)
    return context_text, sources


# -------------------------------
# MANUAL TEST
# -------------------------------
if __name__ == "__main__":
    ctx, srcs = build_llm_context("What is the leave policy?", "hr")

    print("\n📦 CONTEXT:\n")
    print(ctx)

    print("\n📚 SOURCES:\n")
    for s in srcs:
        print(s)

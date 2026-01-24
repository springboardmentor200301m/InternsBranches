import asyncio
from app.semantic_search import semantic_search
from app.prompt_builder import build_user_prompt
from app.llm import LLMClient



def extract_sources(chunks):
    sources = []
    for c in chunks:
        meta = c["metadata"]
        sources.append({
            "document": meta.get("source_file"),
            "department": meta.get("department"),
        })
    return sources


def compute_confidence(chunks: list[dict]) -> float:
    """
    Compute confidence score (0.0 – 1.0) based on retrieval quality.

    Logic:
    - No chunks → 0.0
    - Lower distance = higher relevance
    - More good chunks = higher confidence
    """

    if not chunks:
        return 0.0

    # 1️⃣ Convert distances to similarity scores (inverse)
    similarities = []
    for c in chunks:
        dist = c.get("score", 1.0)
        sim = max(0.0, 1.0 - dist)   # clamp
        similarities.append(sim)

    # 2️⃣ Average relevance
    avg_similarity = sum(similarities) / len(similarities)

    # 3️⃣ Coverage bonus (more chunks → more confidence)
    coverage_bonus = min(len(chunks) / 3, 1.0)  # max at 5 chunks

    # 4️⃣ Final confidence (weighted)
    confidence = (0.7 * avg_similarity) + (0.3 * coverage_bonus)

    return round(confidence, 2)



async def rag_answer(query: str, user_role: str, top_k: int = 3) -> tuple:

    # 1️⃣ Retrieve-data
    chunks = semantic_search(
        query=query,
        user_role=user_role,
        top_k=top_k,
    )

    # 2️⃣ Build prompt
    prompt = build_user_prompt(
        user_query=query,
        retrieved_chunks=chunks,
    )

    # 3️⃣ LLM call (ASYNC)
    llm = LLMClient(provider="groq")
    try:
        answer = await llm.generate(prompt)
    except Exception as e:
        answer = "The system is temporarily unable to generate a response. Please try again later."
        print(f"LLM Error: {e}")

    # 4️⃣ Format sources to match frontend expectations
    sources = []
    for c in chunks:
        meta = c.get("metadata", {})
        sources.append({
            "id": c.get("id", ""),
            "department": meta.get("department", ""),
            "source_file": meta.get("source_file", ""),
            "score": c.get("score", 0.0),
            "snippet": c.get("text", "")[:200] + "..."  # First 200 chars
        })

    return answer, sources




# async def main():
#     response = await rag_answer(
#         query="What are the quarterly reports?",
#         user_role="c_level",
#     )
#     print(response)


# if __name__ == "__main__":
#     asyncio.run(main())

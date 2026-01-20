# src/rag/task1_retrieve_chunks.py

from src.search.semantic_search_role import role_filtered_search

def retrieve_allowed_chunks():
    query = "What is the leave policy?"
    user_role = "HR"
    top_k = 5

    results = role_filtered_search(
        query=query,
        user_role=user_role,
        top_k=top_k
    )

    print(f"\n🔍 Query: {query}")
    print(f"👤 Role: {user_role}")
    print(f"📄 Retrieved Top-{top_k} Allowed Chunks:\n")

    if not results:
        print("❌ No accessible chunks found.")
        return []

    for i, chunk in enumerate(results, start=1):
        print(f"--- Chunk {i} ---")
        print(chunk["content"])
        print()

    return results


if __name__ == "__main__":
    retrieve_allowed_chunks()

from embeddings.embedder import load_embedding_model
from vectordb.chroma_client import get_chroma_client
from search.query_normalizer import normalize_query
from search.rbac import has_access


def semantic_search(query, user_role, top_k=5):
    query = normalize_query(query)
    if not query:
        return []

    user_role = user_role.lower()  # ✅ normalize role

    model = load_embedding_model()
    query_embedding = model.encode(query).tolist()

    client = get_chroma_client()
    collection = client.get_collection("company_docs")

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )

    filtered_results = []

    for i in range(len(results["documents"][0])):
        metadata = results["metadatas"][0][i]

        allowed_roles = metadata.get("allowed_roles", [])
        if isinstance(allowed_roles, str):
            allowed_roles = [r.strip().lower() for r in allowed_roles.split(",")]

        if not has_access(user_role, allowed_roles):
            continue

        filtered_results.append({
            "text": results["documents"][0][i],
            "source_file": metadata.get("source_file"),
            "department": metadata.get("department"),
            "score": round(1 - results["distances"][0][i], 3)
        })

    return filtered_results

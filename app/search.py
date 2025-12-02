from typing import List, Dict, Any

from sentence_transformers import SentenceTransformer

from .vectorstore import get_collection, get_embedding_model


def semantic_search(
    query: str,
    user_role: str,
    top_k: int = 5,
) -> List[Dict[str, Any]]:
    """
    Run semantic search and then enforce RBAC in Python.
    """
    user_role = user_role.lower().strip()

    collection = get_collection()
    model: SentenceTransformer = get_embedding_model()

    query_embedding = model.encode([query]).tolist()[0]

    # Note: no "ids" in include – this Chroma version doesn't allow that
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=max(top_k * 5, 20),  # over-fetch to allow RBAC filtering
        include=["documents", "metadatas", "distances"],
    )

    # Chroma still returns "ids" even if we don't ask for it in include
    ids = results.get("ids", [[]])[0]
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    hits: List[Dict[str, Any]] = []

    for _id, doc, meta, dist in zip(ids, docs, metas, distances):
        allowed_roles_str = meta.get("allowed_roles", "") or ""
        allowed_roles_list = [
            r.strip().lower()
            for r in allowed_roles_str.split(",")
            if r.strip()
        ]

        # Enforce RBAC here
        if user_role not in allowed_roles_list:
            continue

        hits.append(
            {
                "id": _id,
                "text": doc,
                "metadata": meta,
                "score": float(dist),
            }
        )

    return hits[:top_k]

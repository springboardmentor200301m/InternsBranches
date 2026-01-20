"""
Semantic Search with Role-Based Access Control (RBAC)
"""

import re
import chromadb
from sentence_transformers import SentenceTransformer

CHROMA_DB_PATH = "data/chroma_db"
COLLECTION_NAME = "company_docs"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

VALID_ROLES = [
    "employees",
    "hr",
    "finance",
    "marketing",
    "engineering",
    "c-level"
]

ROLE_INHERITANCE = {
    "hr": ["employees"],
    "finance": ["employees"],
    "engineering": ["employees"],
    "marketing": ["employees"],
    "c-level": ["employees", "hr", "finance", "engineering", "marketing"]
}

# -------------------------------
# Utilities
# -------------------------------
def normalize_query(query: str) -> str:
    query = query.lower()
    query = re.sub(r"[^a-z0-9\s]", " ", query)
    query = re.sub(r"\s+", " ", query)
    return query.strip()

def is_valid_query(query: str) -> bool:
    return bool(query and len(query.strip()) >= 3)

# -------------------------------
# Core RBAC Search
# -------------------------------
def role_filtered_search(query: str, user_role: str, top_k: int = 5):
    if not user_role:
        return []

    user_role = user_role.lower().strip()
    if user_role not in VALID_ROLES:
        return []

    query = normalize_query(query)
    if not is_valid_query(query):
        return []

    effective_roles = {user_role}
    effective_roles.update(ROLE_INHERITANCE.get(user_role, []))

    model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    query_embedding = model.encode(query).tolist()

    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    collection = client.get_collection(COLLECTION_NAME)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    authorized_chunks = []

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    for doc, meta in zip(documents, metadatas):

        allowed_roles_raw = (
            meta.get("allowed_roles")
            or meta.get("roles")
            or meta.get("Allowed_Roles")
            or ""
        )

        allowed_roles = set(
            r.strip().lower()
            for r in allowed_roles_raw
            .replace("[", "")
            .replace("]", "")
            .replace("'", "")
            .split(",")
            if r.strip()
        )

        if effective_roles.intersection(allowed_roles):
            authorized_chunks.append({
                "content": doc,
                "source": meta.get("source") or meta.get("document_name"),
                "department": meta.get("department"),
                "allowed_roles": allowed_roles_raw
            })

    return authorized_chunks


# --------------------------------------------------
# ✅ FRONTEND WRAPPER (IMPORTANT)
# --------------------------------------------------
def role_based_search(query: str, role: str, top_k: int = 5):
    """
    Frontend-safe wrapper for RBAC search
    """
    return role_filtered_search(
        query=query,
        user_role=role,
        top_k=top_k
    )

from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer

from app.vectorStore import get_collection, get_embedding_model


# --------------------------------------------------
# TEST QUERIES
# --------------------------------------------------
TEST_QUERIES = [
    ("Show me employee salary details", "guest"),   
    ("Show me employee salary details", "finance"),   
    ("Show me employee salary details", "employee"),  
    ("Show me employee salary details", "hr"),         
    ("Show me employee salary details", "c-level"),    

    ("Explain Q4 financial report", "employee"),    
    ("Explain Q4 financial report", "finance"),      
    ("Explain Q4 financial report", "c-level"),       

    ("Explain system architecture", "engineering"),   
    ("Explain system architecture", "employee"),      

    ("Give company policies overview", "employee"),
]


# --------------------------------------------------
# ROLE NORMALIZATION
# --------------------------------------------------
ROLE_ALIASES = {
    "c-level": "c_level",
    "c_level": "c_level",
    "employee": "employees",
    "employees": "employees",
}


def normalize_role(role: str) -> str:
    role = role.lower().strip()
    return ROLE_ALIASES.get(role, role)


# --------------------------------------------------
# QUERY NORMALIZATION
# --------------------------------------------------
def normalize_query(query: str) -> str:
    return " ".join(query.lower().strip().split())


# --------------------------------------------------
# RBAC CHECK (CORRECT)
# --------------------------------------------------
def has_access(user_role: str, allowed_roles: List[str]) -> bool:
    user_role = normalize_role(user_role)

    allowed_roles = [normalize_role(r) for r in allowed_roles]

    # C-Level can access everything
    if user_role == "c_level":
        return True

    # Explicit allow only
    return user_role in allowed_roles


# --------------------------------------------------
# SEMANTIC SEARCH WITH RBAC
# --------------------------------------------------
def semantic_search(    query: str,    user_role: str,    top_k: int = 3) -> List[Dict[str, Any]]:

    query = normalize_query(query)
    user_role = normalize_role(user_role)

    collection = get_collection()
    model: SentenceTransformer = get_embedding_model()

    query_embedding = model.encode([query]).tolist()[0]

    # Over-fetch to allow RBAC filtering
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=max(top_k * 5, 20),
        include=["documents", "metadatas", "distances"],
    )

    ids = results.get("ids", [[]])[0]
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    hits: List[Dict[str, Any]] = []

    for _id, doc, meta, dist in zip(ids, docs, metas, distances):
        allowed_roles_raw = meta.get("allowed_roles", "")

        allowed_roles = [
            r.strip().lower()
            for r in allowed_roles_raw.split(",")
            if r.strip()
        ]

        if not has_access(user_role, allowed_roles):
            continue

        hits.append(
            {
                "id": _id,
                "text": doc,
                "metadata": meta,
                "score": float(dist),
            }
        )

        if len(hits) >= top_k:
            break

    return hits


# --------------------------------------------------
# RBAC TEST RUNNER
# --------------------------------------------------
def run_rbac_tests():
    for query, role in TEST_QUERIES:
        print("=" * 80)
        print(f"Query: {query}")
        print(f"Role:  {role}")
        print("-" * 80)

        results = semantic_search(query, role, top_k=3)

        if not results:
            print("❌ ACCESS BLOCKED (RBAC working)")
        else:
            print("✅ ACCESS GRANTED")
            for i, r in enumerate(results, start=1):
                meta = r["metadata"]
                print(f"[{i}] score={r['score']:.4f}")
                print(f"    id:        {meta.get('department')}/{meta.get('source_file')}::chunk_{meta.get('chunk_index')}")
                print(f"    department:{meta.get('department')}")
                print(f"    source:    {meta.get('source_file')}")
                print(f"    roles:     {meta.get('allowed_roles')}")
                
                # Print a snippet of text (first 200 chars or full text)
                text_snippet = r["text"]
                if len(text_snippet) > 300:
                    text_snippet = text_snippet[:300] + "..."
                print(f"    text:      {text_snippet}")
                print()

if __name__ == "__main__":
    run_rbac_tests()

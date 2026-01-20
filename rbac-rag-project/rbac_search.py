import re
import chromadb
from sentence_transformers import SentenceTransformer

# -------------------------------------------------
# ROLE HIERARCHY
# -------------------------------------------------
ROLE_HIERARCHY = {
    "Admin": ["Engineering", "Finance", "Marketing", "HR", "C-Level"],
    "C-Level": ["Engineering", "Finance", "Marketing"],
    "Engineering": ["Engineering"],
    "Finance": ["Finance"],
    "Marketing": ["Marketing"],
    "HR": ["HR"],
    "Employee": ["General"]
}

# -------------------------------------------------
# QUERY NORMALIZATION & VALIDATION
# -------------------------------------------------
def normalize_query(query: str) -> str:
    query = query.strip().lower()
    if not re.search(r"[a-z0-9]", query):
        return ""
    return query

# -------------------------------------------------
# LOAD VECTOR DATABASE (ONCE)
# -------------------------------------------------
print("Loading vector database...")
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection("rbac_documents")
print("Total records in DB:", collection.count())

# -------------------------------------------------
# LOAD EMBEDDING MODEL (ONCE)
# -------------------------------------------------
print("Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

# -------------------------------------------------
# SEMANTIC SEARCH + RBAC (RAG-READY)
# -------------------------------------------------
def semantic_search(query: str, user_role: str, k: int = 3):
    """
    Performs semantic search with RBAC filtering.
    Returns authorized chunks with clean metadata for RAG.
    """

    query = normalize_query(query)
    if not query:
        return []

    if user_role not in ROLE_HIERARCHY:
        return []

    query_embedding = model.encode(query).tolist()

    try:
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=10
        )
    except Exception:
        return []

    if not results.get("documents") or not results["documents"][0]:
        return []

    allowed_departments = ROLE_HIERARCHY[user_role]
    allowed_chunks = []

    MAX_ACCEPTABLE_DISTANCE = 2.5

    for i, metadata in enumerate(results["metadatas"][0]):
        distance = results["distances"][0][i]
        department = metadata.get("department")

        # 🔐 RBAC + relevance check (per chunk)
        if department in allowed_departments and distance <= MAX_ACCEPTABLE_DISTANCE:
            allowed_chunks.append({
                "content": results["documents"][0][i],
                "metadata": {
                    "document": metadata.get("file_name", "Unknown"),
                    "department": department
                },
                "score": distance
            })

        if len(allowed_chunks) == k:
            break

    return allowed_chunks

# -------------------------------------------------
# BUILD RAG CONTEXT + SOURCES (NO HALLUCINATION)
# -------------------------------------------------
def build_rag_context(chunks):
    """
    Separates LLM context and source attribution.
    LLM sees ONLY context, never metadata.
    """
    context = []
    sources = []

    for chunk in chunks:
        context.append(chunk["content"])
        sources.append({
            "document": chunk["metadata"]["document"],
            "department": chunk["metadata"]["department"]
        })

    return context, sources

# -------------------------------------------------
# CLI TESTING (RBAC + RAG VALIDATION)
# -------------------------------------------------
if __name__ == "__main__":
    print("\n🔹 RBAC Semantic Search (RAG-Ready CLI Mode)")

    user_role = input(
        "Enter your role (Admin / C-Level / Engineering / Finance / Marketing / HR / Employee): "
    ).strip()

    if user_role not in ROLE_HIERARCHY:
        print("❌ Invalid role. Access denied.")
        exit()

    print(f"✔ Logged in as role: {user_role}")

    raw_query = input("\nEnter your search query: ")
    query = normalize_query(raw_query)

    if not query:
        print("❌ Invalid query: Query cannot be empty or meaningless.")
        exit()

    chunks = semantic_search(query, user_role, k=5)

    # 🔒 TASK 4: No-context handling (NO LLM CALL)
    if not chunks:
        print("\n❌ No information available for your role.")
        exit()

    context, sources = build_rag_context(chunks)

    print("\n🔹 Retrieved Context (for LLM):\n")
    for idx, text in enumerate(context, 1):
        print(f"Chunk {idx}:")
        print(text[:300])
        print("-" * 60)

    print("\n🔹 Source Attribution:\n")
    for src in sources:
        print(f"- {src['document']} ({src['department']})")

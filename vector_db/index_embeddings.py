import os
from vector_db.chroma_client import get_chroma_collection

ROLE_CONTEXT = {
    "Finance": "finance, revenue, profit, loss, budgeting, risk management",
    "Marketing": "marketing strategy, brand campaign, market analysis",
    "Engineering": "engineering systems, architecture, APIs, technology",
    "HR": "recruitment, employee policy, payroll, HR management",
    "Legal": "contracts, compliance, legal policy, regulations",
    "General": "company policy, employee handbook, organizational rules"
}

def enrich_text(text, role):
    context = ROLE_CONTEXT.get(role, "")
    return f"[ROLE: {role}]\n[CONTEXT]\n{context}\n\n[CONTENT]\n{text}"

def index_documents():
    collection = get_chroma_collection()

    # 🔒 Guard: do not re-index if data exists
    if collection.count() > 0:
        print("⚠️ Documents already indexed. Skipping indexing.")
        return

    documents = []
    metadatas = []
    ids = []

    idx = 0

    for root, _, files in os.walk("data"):
        for file in files:
            if not file.endswith((".md", ".txt", ".csv")):
                continue

            path = os.path.join(root, file)
            role = root.split(os.sep)[-1].capitalize()

            with open(path, encoding="utf-8", errors="ignore") as f:
                text = f.read()

            documents.append(enrich_text(text, role))
            metadatas.append({
                "role": role,
                "source": path
            })
            ids.append(f"{path}_{idx}")
            idx += 1

    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )

    print(f"✅ Indexed {len(documents)} documents")

if __name__ == "__main__":
    index_documents()

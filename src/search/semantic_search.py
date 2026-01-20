import chromadb
from sentence_transformers import SentenceTransformer
import os

# ---------------- CONFIG ----------------
CHROMA_PATH = os.path.join("data", "chroma_db")
COLLECTION_NAME = "company_docs"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
TOP_K = 3
# ----------------------------------------


def load_vector_db():
    print("🔹 Loading ChromaDB...")
    client = chromadb.PersistentClient(path=CHROMA_PATH)

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )
    return collection


def load_embedding_model():
    print("🔹 Loading embedding model...")
    return SentenceTransformer(EMBEDDING_MODEL_NAME)


def semantic_search(query: str):
    # 1️⃣ Load DB
    collection = load_vector_db()

    # 2️⃣ Load embedding model
    model = load_embedding_model()

    # 3️⃣ Generate query embedding
    print(f"\n🔍 User Query: {query}")
    query_embedding = model.encode(query).tolist()

    # 4️⃣ Perform semantic search
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=TOP_K
    )

    # 5️⃣ Display results
    print("\n📌 Search Results:\n")
    for i in range(len(results["documents"][0])):
        print(f"Result {i + 1}")
        print("-" * 40)
        print("Document:", results["metadatas"][0][i]["document_name"])
        print("Department:", results["metadatas"][0][i]["department"])
        print("Allowed Roles:", results["metadatas"][0][i]["allowed_roles"])
        print("\nContent Snippet:\n")
        print(results["documents"][0][i][:500], "...\n")

    return results


# ---------------- MAIN ----------------
if __name__ == "__main__":
    user_query = input("\n💬 Enter your search query: ")
    semantic_search(user_query)

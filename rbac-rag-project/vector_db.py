import json
import chromadb
from sentence_transformers import SentenceTransformer

def load_jsonl(path):
    data = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            data.append(json.loads(line))
    return data

print("Loading processed chunks...")
chunks = load_jsonl("processed/chunks_tagged.jsonl")
print("Total chunks:", len(chunks))

# ✅ CORRECT persistent client
print("Initializing persistent ChromaDB...")
client = chromadb.PersistentClient(path="./chroma_db")

collection = client.get_or_create_collection(
    name="rbac_documents"
)

print("Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

texts = [c["text"] for c in chunks]

print("Generating embeddings...")
embeddings = model.encode(texts).tolist()

metadatas = [{
    "department": c["department"],
    "file_name": c["file_name"],
    "accessible_roles": ",".join(c["accessible_roles"])
} for c in chunks]

ids = [f"chunk_{i}" for i in range(len(chunks))]

print("Inserting into vector DB...")
collection.add(
    documents=texts,
    embeddings=embeddings,
    metadatas=metadatas,
    ids=ids
)

print("Inserted records:", collection.count())
print("Insertion complete (persistent)")

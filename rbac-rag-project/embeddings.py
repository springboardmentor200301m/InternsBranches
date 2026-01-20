import json
from sentence_transformers import SentenceTransformer

# ---------- Load chunks ----------
def load_jsonl(path):
    data = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            data.append(json.loads(line))
    return data

print("Loading processed chunks...")
chunks = load_jsonl("processed/chunks_tagged.jsonl")
print("Total chunks:", len(chunks))

# ---------- Load embedding model ----------
print("Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")
print("Model loaded")

# ---------- Generate embeddings ----------
texts = [c["text"] for c in chunks]
print("Generating embeddings...")
embeddings = model.encode(texts)

print("Total embeddings:", len(embeddings))

# ---------- Verify embedding dimension ----------
print("Embedding dimension:", len(embeddings[0]))

# ---------- Temporary storage ----------
temp_store = []

for i, emb in enumerate(embeddings):
    temp_store.append({
        "embedding": emb.tolist(),
        "metadata": {
            "department": chunks[i]["department"],
            "file_name": chunks[i]["file_name"],
            "accessible_roles": chunks[i]["accessible_roles"]
        }
    })

print("Temporary embedding store size:", len(temp_store))
print("Sample stored item keys:", temp_store[0].keys())

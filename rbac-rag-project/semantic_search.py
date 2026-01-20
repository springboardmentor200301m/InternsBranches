import chromadb
import time
from sentence_transformers import SentenceTransformer

# -----------------------------
# Query normalization
# -----------------------------
def normalize_query(query: str) -> str:
    return query.strip().lower()

# -----------------------------
# Load Vector DB
# -----------------------------
print("Loading persistent vector database...")
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection("rbac_documents")
print("Total records in DB:", collection.count())

# -----------------------------
# Accept & validate query
# -----------------------------
raw_query = input("\nEnter your search query: ")
query = normalize_query(raw_query)

if not query:
    print("❌ Invalid query: Query cannot be empty.")
    exit()

# -----------------------------
# Load embedding model
# -----------------------------
print("Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

# -----------------------------
# Generate query embedding
# -----------------------------
print("Generating query embedding...")
query_embedding = model.encode(query).tolist()

# -----------------------------
# Semantic search with latency measurement
# -----------------------------
print("Performing semantic search...")
start_time = time.time()

results = collection.query(
    query_embeddings=[query_embedding],
    n_results=5
)

end_time = time.time()
latency = end_time - start_time

# -----------------------------
# Handle no results
# -----------------------------
if not results["documents"] or not results["documents"][0]:
    print("❌ No results found for the given query.")
    exit()

# -----------------------------
# Display results (Quality Evaluation)
# -----------------------------
print("\nTop Search Results:\n")
for i, doc in enumerate(results["documents"][0]):
    print(f"Result {i+1}:")
    print(doc[:300])
    print("Source File:", results["metadatas"][0][i]["file_name"])
    print("Department:", results["metadatas"][0][i]["department"])
    print("-" * 50)

# -----------------------------
# Performance output (Benchmarking)
# -----------------------------
print(f"\nSearch latency: {latency:.4f} seconds")

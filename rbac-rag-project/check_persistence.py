import chromadb

# SAME persistent path
client = chromadb.PersistentClient(path="./chroma_db")

# 🔍 List all collections first
collections = client.list_collections()
print("Available collections:", [c.name for c in collections])

# Now get the existing one
collection = client.get_collection(name="rbac_documents")

print("Persistent records count:", collection.count())

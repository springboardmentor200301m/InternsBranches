# src/vectordb/chroma_setup.py
import os
import json
import numpy as np
from sentence_transformers import SentenceTransformer
import chromadb

CHROMA_PATH = "data/chroma_db"
COLLECTION_NAME = "rbac_documents"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
DATA_PATH = "data/processed_chunks_with_metadata.json"
EMBEDDINGS_PATH = "data/temp_embeddings.npy"

# Load processed chunks
with open(DATA_PATH, "r", encoding="utf-8") as f:
    chunks = json.load(f)

# Load embeddings
embeddings = np.load(EMBEDDINGS_PATH)

assert len(chunks) == embeddings.shape[0], "Chunks and embeddings count mismatch!"

# Initialize persistent ChromaDB
client = chromadb.PersistentClient(path=CHROMA_PATH)

# Create or get collection
collection = client.get_or_create_collection(name=COLLECTION_NAME)

documents, metadatas, ids = [], [], []

for i, chunk in enumerate(chunks):
    documents.append(chunk["content"])
    metadatas.append({
        "source": chunk["document_name"],
        "department": chunk["department"],
        "allowed_roles": ",".join(chunk["allowed_roles"].split(","))
    })
    ids.append(f"chunk_{i}")

collection.add(
    documents=documents,
    embeddings=embeddings.tolist(),
    metadatas=metadatas,
    ids=ids
)

print(f"✅ Collection '{COLLECTION_NAME}' created with {len(documents)} documents!")

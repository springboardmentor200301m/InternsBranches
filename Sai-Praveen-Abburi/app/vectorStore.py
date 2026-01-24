from pathlib import Path
import json
from typing import List, Dict

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer


# --------------------------------------------------
# CONFIG
# --------------------------------------------------
PROCESSED_DATA_PATH = Path("data/processed/processed_chunks.json")
VECTOR_DB_DIR = Path("data/vector_db")
COLLECTION_NAME = "company_docs"
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


# --------------------------------------------------
# SINGLETONS
# --------------------------------------------------
_embedding_model = None
_chroma_client = None
_collection = None


# --------------------------------------------------
# LOADERS
# --------------------------------------------------
def get_embedding_model() -> SentenceTransformer:
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return _embedding_model


def get_chroma_client() -> chromadb.Client:
    global _chroma_client
    if _chroma_client is None:
        _chroma_client = chromadb.PersistentClient(
            path=str(VECTOR_DB_DIR),
            settings=Settings(anonymized_telemetry=False),
        )
    return _chroma_client


def get_collection():
    global _collection
    if _collection is None:
        client = get_chroma_client()
        _collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


# --------------------------------------------------
# LOAD CHUNKS
# --------------------------------------------------
def load_chunks() -> List[Dict]:
    with PROCESSED_DATA_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)



# --------------------------------------------------
# INDEXING PIPELINE
# --------------------------------------------------
def index_chunks(batch_size: int = 64) -> None:
    chunks = load_chunks()
    print(f"Loaded {len(chunks)} chunks")

    model = get_embedding_model()
    client = get_chroma_client()

    # Reset collection safely
    try:
        client.delete_collection(COLLECTION_NAME)
        print(f"Deleted existing collection '{COLLECTION_NAME}'")
    except Exception:
        print("No existing collection found")

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]

        ids = [c["id"] for c in batch]
        texts = [c["text"] for c in batch]

        metadatas = [
            {
                "source_file": c["source_file"],
                "source_path": c.get("source_path", ""),
                "department": c["department"],
                "chunk_index": c.get("chunk_index", i + idx),
                "allowed_roles": ",".join(c["allowed_roles"]),
            }
            for idx, c in enumerate(batch)
        ]

        embeddings = model.encode(texts).tolist()

        collection.add(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
        )

        print(f"Indexed chunks {i} → {i + len(batch) - 1}")

    print("✅ Indexing completed successfully")
    for metadata in metadatas:
        print(metadata)


# --------------------------------------------------
# RUN
# --------------------------------------------------
if __name__ == "__main__":
    index_chunks()

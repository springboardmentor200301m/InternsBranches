from pathlib import Path
from typing import List, Dict, Any

import json
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

from .config import (
    DATA_PROCESSED_DIR,
    VECTOR_DB_DIR,
    VECTOR_COLLECTION_NAME,
)

# Lazy singletons so we don't reload model / client repeatedly
_embedding_model: SentenceTransformer | None = None
_chroma_client: chromadb.api.ClientAPI | None = None
_collection = None


def get_embedding_model() -> SentenceTransformer:
    global _embedding_model
    if _embedding_model is None:
        # Small, fast, good-quality sentence transformer
        _embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    return _embedding_model


def get_chroma_client() -> chromadb.api.ClientAPI:
    global _chroma_client
    if _chroma_client is None:
        _chroma_client = chromadb.PersistentClient(
            path=str(VECTOR_DB_DIR),
            settings=Settings(
                anonymized_telemetry=False,
            ),
        )
    return _chroma_client


def get_collection():
    global _collection
    if _collection is None:
        client = get_chroma_client()
        _collection = client.get_or_create_collection(
            name=VECTOR_COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},  # cosine similarity
        )
    return _collection


def load_chunks() -> List[Dict[str, Any]]:
    chunks_path = DATA_PROCESSED_DIR / "document_chunks.jsonl"
    chunks: List[Dict[str, Any]] = []
    with chunks_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            chunks.append(json.loads(line))
    return chunks


def index_chunks(batch_size: int = 64) -> None:
    """
    Load preprocessed chunks, generate embeddings, and index into Chroma.
    """
    from .config import VECTOR_COLLECTION_NAME  # if not already imported at top
    chunks = load_chunks()
    print(f"Loaded {len(chunks)} chunks from processed data")

    model = get_embedding_model()
    client = get_chroma_client()

    # --- Safely recreate collection instead of delete(where={}) ---
    try:
        # If collection exists, delete it (full reset)
        client.delete_collection(VECTOR_COLLECTION_NAME)
        print(f"Deleted existing collection '{VECTOR_COLLECTION_NAME}'")
    except Exception as e:
        print(f"No existing collection to delete or delete failed: {e}")

    # Create a fresh collection
    collection = client.get_or_create_collection(
        name=VECTOR_COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    # Batch insert
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]

        ids = [c["id"] for c in batch]
        texts = [c["text"] for c in batch]
        metadatas = [
            {
                "source_file": c["source_file"],
                "source_path": c["source_path"],
                "department": c["department"],
                "chunk_index": c["chunk_index"],
                # store as comma-separated string to satisfy Chroma type rules
                "allowed_roles": ",".join(c["allowed_roles"]),
            }
            for c in batch
        ]


        embeddings = model.encode(texts).tolist()

        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
        )

        print(f"Indexed batch {i}–{i + len(batch) - 1}")

    print("Indexing complete.")

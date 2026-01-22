import os
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["CHROMA_LOG_LEVEL"] = "ERROR"

from chromadb import PersistentClient
from embeddings.embedding_function import LocalEmbeddingFunction

CHROMA_PATH = "chroma_store"
COLLECTION_NAME = "rbac_docs"

# 🔹 Load embedding model ONCE
_embedding_function = LocalEmbeddingFunction()

def get_chroma_collection():
    client = PersistentClient(path=CHROMA_PATH)

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=_embedding_function
    )

    return collection

import chromadb
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PERSIST_DIR = os.path.join(BASE_DIR, "vectordb_store")

def get_chroma_client():
    os.makedirs(PERSIST_DIR, exist_ok=True)   # 🔥 FORCE folder creation
    return chromadb.PersistentClient(
        path=PERSIST_DIR
    )

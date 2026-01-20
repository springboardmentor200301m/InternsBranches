import os
import chromadb
from chromadb.config import Settings

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CHROMA_PATH = os.path.join(PROJECT_ROOT, "data", "chroma_db")

client = chromadb.Client(
    Settings(
        persist_directory=CHROMA_PATH,
        anonymized_telemetry=False
    )
)

print("📦 Existing collections:")
for col in client.list_collections():
    print(" -", col.name)

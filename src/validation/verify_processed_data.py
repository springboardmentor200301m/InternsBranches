import json
import os

DATA_PATH = "data/processed_chunks_with_metadata.json"

REQUIRED_KEYS = {
    "document_name",
    "full_path",
    "department",
    "allowed_roles",
    "chunk_id",
    "content"
}

def verify_processed_data():
    assert os.path.exists(DATA_PATH), "Processed data file not found!"

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    print(f"Total chunks loaded: {len(chunks)}")

    for i, chunk in enumerate(chunks):
        missing = REQUIRED_KEYS - chunk.keys()
        if missing:
            raise ValueError(f"Chunk {i} missing keys: {missing}")

        if not chunk["content"].strip():
            raise ValueError(f"Empty content in chunk {i}")

    print("✅ Processed data verification PASSED")

if __name__ == "__main__":
    verify_processed_data()

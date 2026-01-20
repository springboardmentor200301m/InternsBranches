import json
import os
import sys
import numpy as np

# ---- Add project root to path ----
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(PROJECT_ROOT)

from sentence_transformers import SentenceTransformer

DATA_PATH = "data/processed_chunks_with_metadata.json"
EMBEDDING_SAVE_PATH = "data/temp_embeddings.npy"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

def load_chunks():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        chunks = json.load(f)
    return [chunk["content"] for chunk in chunks]

def main():
    print("\n--- Embedding Generation Started ---\n")

    # 1. Load model
    print("Loading embedding model...")
    model = SentenceTransformer(MODEL_NAME)
    print("Model loaded successfully.")

    # 2. Load chunks
    texts = load_chunks()
    print(f"Total chunks loaded: {len(texts)}")

    # 3. Generate embeddings
    print("Generating embeddings...")
    embeddings = model.encode(texts, show_progress_bar=True)

    # 4. Verify dimensions
    embeddings = np.array(embeddings)
    print(f"Embedding shape: {embeddings.shape}")

    assert embeddings.shape[0] == len(texts), "Mismatch in chunk count!"
    assert embeddings.shape[1] == 384, "Unexpected embedding dimension!"

    print("Embedding dimensions verified (384).")

    # 5. Store embeddings temporarily
    np.save(EMBEDDING_SAVE_PATH, embeddings)
    print(f"Embeddings saved to: {EMBEDDING_SAVE_PATH}")

    print("\n✅ Embedding pipeline completed successfully!\n")

if __name__ == "__main__":
    main()

import pandas as pd
from sentence_transformers import SentenceTransformer

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

_model = None  # 👈 global cache


def load_embedding_model():
    """
    Loads embedding model only once (singleton).
    """
    global _model
    if _model is None:
        print("🔄 Loading embedding model...")
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def load_chunks(path="data/processed_chunks.parquet"):
    return pd.read_parquet(path)


def generate_embeddings(model, texts):
    return model.encode(
        texts,
        batch_size=32,
        show_progress_bar=True
    )


def verify_dimensions(embeddings):
    assert embeddings.shape[1] == 384, "Embedding dimension mismatch"


if __name__ == "__main__":
    model = load_embedding_model()
    df = load_chunks()
    emb = generate_embeddings(model, df["text"].tolist()[:2])
    verify_dimensions(emb)
    print("✅ Embeddings OK:", emb.shape)

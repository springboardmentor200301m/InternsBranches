from sentence_transformers import SentenceTransformer

class LocalEmbeddingFunction:
    def __init__(self):
        print("🔹 Loading local embedding model...")
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        print("✅ Local embedding model loaded")

    def __call__(self, input):
        """
        input: List[str]
        output: List[List[float]]
        """
        embeddings = self.model.encode(input, convert_to_numpy=True)
        return embeddings.tolist()

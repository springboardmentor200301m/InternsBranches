from embeddings.embedder import *
from vectordb.chroma_client import get_chroma_client

def index_documents():
    model = load_embedding_model()
    df = load_chunks()

    embeddings = generate_embeddings(model, df["text"].tolist())
    verify_dimensions(embeddings)

    client = get_chroma_client()
    collection = client.get_or_create_collection("company_docs")

    for i, row in df.iterrows():
        collection.add(
            ids=[row["id"]],
            embeddings=[embeddings[i].tolist()],
            documents=[row["text"]],
            metadatas=[{
                "department": row["department"],
                "allowed_roles": ",".join(row["allowed_roles"]),
                "source_file": row["source_file"],
                "chunk_seq": row["chunk_seq"]
            }]
        )
    print("✅ Documents indexed successfully")

if __name__ == "__main__":
    index_documents()

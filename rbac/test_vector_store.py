from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

def test_vector_store():
    embed_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vs = FAISS.load_local("rbac/faiss_index", embed_model, allow_dangerous_deserialization=True)
    print("Vector store loaded\n")

if __name__ == "__main__":
    test_vector_store()

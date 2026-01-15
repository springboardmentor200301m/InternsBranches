from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


DATA_DIR = "data"

def load_documents_with_roles():
    documents = []

    for role in os.listdir(DATA_DIR):
        role_path = os.path.join(DATA_DIR, role)

        if not os.path.isdir(role_path):
            continue

        for file in os.listdir(role_path):
            file_path = os.path.join(role_path, file)

            if file.endswith((".md", ".txt", ".csv")):
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                doc = Document(
                    page_content=content,
                    metadata={
                        "role": role,
                        "source": file
                    }
                )

                documents.append(doc)

    return documents

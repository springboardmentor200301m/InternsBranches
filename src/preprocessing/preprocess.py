import os
import re
import json
import pandas as pd
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(PROJECT_ROOT)

from src.utils.role_metadata import detect_department, allowed_roles_for_department

BASE_DIR = "data_repo"

def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    text = text.replace("\x0c", "")
    return text.strip()

def load_document(path):
    if path.endswith(".md"):
        with open(path, "r", encoding="utf-8") as f:
            return clean_text(f.read())
    elif path.endswith(".csv"):
        df = pd.read_csv(path)
        return clean_text(df.to_string())
    return ""

def chunk_text(text, chunk_size=350):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks

def process_documents():
    all_chunks = []

    for root, dirs, files in os.walk(BASE_DIR):
        for file in files:
            if file.endswith(".md") or file.endswith(".csv"):
                file_path = os.path.join(root, file)

                department = detect_department(file_path)
                allowed_roles = allowed_roles_for_department(department)

                doc_text = load_document(file_path)
                chunks = chunk_text(doc_text)

                for idx, chunk in enumerate(chunks):
                    all_chunks.append({
                        "document_name": file,              # TASK 5: Source info – document name
                        "full_path": file_path,              # TASK 5: Source info – file location
                        "department": department,            # TASK 5: Source info – department
                        "allowed_roles": ",".join(allowed_roles),  # TASK 5: Source info – RBAC roles
                        "chunk_id": idx,
                        "content": chunk
                    })

    return all_chunks

if __name__ == "__main__":
    chunks = process_documents()

    with open("data/processed_chunks_with_metadata.json", "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=4)

    print(f"Processing with metadata complete! Total chunks: {len(chunks)}")
    print("Saved to: data/processed_chunks_with_metadata.json")

import os
import markdown
import pandas as pd
import json
import re

# ---------- READ FILES ----------
def read_markdown(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return markdown.markdown(f.read())

def read_csv(file_path):
    return pd.read_csv(file_path).to_string()

# ---------- CLEAN TEXT ----------
def clean_text(text):
    cleaned = re.sub(r'\s+', ' ', text)  # remove extra spaces/newlines
    cleaned = re.sub(r'[^\x00-\x7F]+', ' ', cleaned)  # remove special chars
    return cleaned.strip()

# ---------- LOAD ALL DOCUMENTS ----------
def load_documents(folder):
    docs = []
    for root, dirs, files in os.walk(folder):
        for file in files:
            path = os.path.join(root, file)

            if file.endswith(".md"):
                content = read_markdown(path)
            elif file.endswith(".csv"):
                content = read_csv(path)
            else:
                continue

            cleaned = clean_text(content)

            docs.append({
                "file_name": file,
                "path": path,
                "content": cleaned
            })
    return docs

# ---------- CHUNK TEXT ----------
def chunk_text(text, size=400):
    words = text.split()
    chunks = []

    for i in range(0, len(words), size):
        chunk = " ".join(words[i:i+size])
        chunks.append(chunk)

    return chunks

# ---------- MAIN PROCESS ----------
docs = load_documents("../docs_repo")

output_chunks = []

for doc in docs:
    chunks = chunk_text(doc["content"])

    for idx, chunk in enumerate(chunks):
        output_chunks.append({
            "chunk_id": f"{doc['file_name']}_chunk_{idx}",
            "file_name": doc["file_name"],
            "text": chunk,
            "role_permissions": "auto",  # you will fill based on YAML later
        })

# ---------- SAVE OUTPUT ----------
os.makedirs("../processed", exist_ok=True)

with open("../processed/chunks.jsonl", "w", encoding="utf-8") as f:
    for item in output_chunks:
        f.write(json.dumps(item) + "\n")

print("Processing Complete!")
print("Total Chunks:", len(output_chunks))

import re
import pandas as pd
import os
import uuid
import json


# -------------------------------------------------------
# ROLE → DOCUMENT MAPPING (edit as required)
# -------------------------------------------------------
ROLE_DOCUMENT_MAP = {
  "finance": ["finance", "budget", "revenue"],
  "marketing": ["marketing"],
  "hr": ["hr", "employees"],
  "engineering": ["engineering", "tech"],
  "employees": ["general"],
  "c_level": ["finance", "marketing", "hr", "engineering", "general"]
}

def save_chunks_to_json(chunks, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)




class DataPreprocessor:
    def __init__(self, max_chunk_size=500):
        self.max_chunk_size = max_chunk_size

    # STEP 1: Load File
    def load_file(self, path):
        if path.endswith(".md"):
            with open(path, "r", encoding="utf-8") as f:
                return f.read()

        elif path.endswith(".csv"):
            df = pd.read_csv(path)
            df = df.dropna(how='all')
            df = df.fillna('')
            return df.to_string()

        else:
            raise ValueError(f"Unsupported file type: {path}")

    # STEP 2: Remove junk
    def remove_junk(self, text):
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'#+', '', text)
        return text

    # STEP 3: Normalize
    def normalize(self, text):
        text = text.lower()
        text = text.replace("\n", " ")
        text = " ".join(text.split())
        return text

    # STEP 4: Remove noise
    def remove_noise(self, text):
        text = re.sub(r'http\S+', '', text)
        text = re.sub(r'\S+@\S+', '', text)
        text = re.sub(r'page \d+', '', text, flags=re.I)
        text = re.sub(r'©.*?\d+', '', text)
        return text

    # STEP 5: Standardize
    def standardize_format(self, text):
        text = re.sub(r'\s*-\s*', '- ', text)
        text = re.sub(r'\s+', ' ', text)
        return text

    # STEP 6: Chunking
    def chunk_text(self, text):
        words = text.split()
        chunks = []
        chunk = []

        for word in words:
            if len(chunk) + 1 > self.max_chunk_size:
                chunks.append(" ".join(chunk))
                chunk = []
            chunk.append(word)

        if chunk:
            chunks.append(" ".join(chunk))

        return chunks

    # STEP 7: Final clean
    def final_clean(self, chunks):
        return [c.strip() for c in chunks if c.strip()]

    # STEP 8: Assign metadata
    def assign_metadata(self, chunks, department, file_name):
        metadata_chunks = []

        for chunk in chunks:
            # Determine allowed roles
            allowed_roles = [
                role for role, docs in ROLE_DOCUMENT_MAP.items()
                if department in docs
            ]

            metadata_chunks.append({
                "id": str(uuid.uuid4()),
                "text": chunk,
                "source_file": file_name,
                "department": department,
                "allowed_roles": allowed_roles
            })

        return metadata_chunks

    # Full pipeline
    def preprocess_file(self, path, department):
        file_name = os.path.basename(path)

        text = self.load_file(path)
        text = self.remove_junk(text)
        text = self.normalize(text)
        text = self.remove_noise(text)
        text = self.standardize_format(text)
        chunks = self.chunk_text(text)
        chunks = self.final_clean(chunks)

        # return chunks WITH metadata
        return self.assign_metadata(chunks, department, file_name)


# ====================================================================
# MAIN 
# ====================================================================
if __name__ == "__main__":
    all_chunks = []
    folder_path = r"D:\Rbac_rag_Chat\data\raw"
    preprocessor = DataPreprocessor(max_chunk_size=500)

    for department_folder in os.listdir(folder_path):
        dept_path = os.path.join(folder_path, department_folder)

        if not os.path.isdir(dept_path):
            continue

        # department = folder name (convert lowercase)
        department = department_folder.lower()

        print(f"Inside Department: {department_folder}")

        for file_name in os.listdir(dept_path):
            file_path = os.path.join(dept_path, file_name)

            print("  Found file:", file_path)

            if file_path.endswith(".md") or file_path.endswith(".csv"):
                chunks = preprocessor.preprocess_file(file_path, department)
                all_chunks.extend(chunks)

    output_file = "processed_chunks.json"
    save_chunks_to_json(all_chunks, 'D:\Rbac_rag_Chat\data\processed\processed_chunks.json')

    print(f"Saved {len(all_chunks)} chunks to {output_file}")


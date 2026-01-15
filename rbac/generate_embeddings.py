"""
Module 6: Generate Embeddings and Create Vector Database using FAISS

"""

import os
import json
import pickle
from pathlib import Path
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from datetime import datetime

# Role-to-document mapping
ROLE_DOCUMENT_MAP = {
    "Finance": ["finance"],
    "Marketing": ["marketing"],
    "HR": ["hr"],
    "Engineering": ["engineering"],
    "Employees": ["general"],
    "C-Level": ["finance", "marketing", "hr", "engineering", "general"]
}

def load_documents_from_folder(folder_path):
    """Load all markdown and text files from a folder"""
    documents = []
    folder = Path(folder_path)
    
    if not folder.exists():
        print(f"⚠️  Folder not found: {folder_path}")
        return documents
    
    for file_path in folder.glob("*.*"):
        if file_path.suffix in ['.md', '.txt', '.csv']:
            try:
                # Try UTF-8 first, then fall back to other encodings
                content = None
                for encoding in ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
                    try:
                        with open(file_path, 'r', encoding=encoding) as f:
                            content = f.read()
                        break
                    except UnicodeDecodeError:
                        continue
                
                if content:
                    documents.append({
                        'content': content,
                        'source': str(file_path.name),
                        'folder': folder.name,
                        'file_type': file_path.suffix
                    })
                    print(f"✅ Loaded: {file_path.name}")
                else:
                    print(f"⚠️  Skipped {file_path.name}: encoding issue")
            except Exception as e:
                print(f"❌ Error loading {file_path.name}: {e}")
    
    return documents

def chunk_text(text, chunk_size=500, overlap=50):
    """Split text into overlapping chunks"""
    chunks = []
    words = text.split()
    
    for i in range(0, len(words), chunk_size - overlap):
        chunk = ' '.join(words[i:i + chunk_size])
        if len(chunk.strip()) > 50:
            chunks.append(chunk)
    
    return chunks

def main():
    print("="*70)
    print("MODULE 6: GENERATING EMBEDDINGS & VECTOR DATABASE (FAISS)")
    print("="*70)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Initialize embedding model
    print("📥 Loading embedding model...")
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    print("✅ Embedding model loaded\n")
    
    # Load documents from each department folder
    data_path = Path("./data")
    all_chunks = []
    all_metadata = []
    
    departments = ["finance", "marketing", "hr", "engineering", "general"]
    
    for dept in departments:
        dept_path = data_path / dept
        print(f"📂 Processing {dept.upper()} department...")
        
        documents = load_documents_from_folder(dept_path)
        
        if not documents:
            print(f"⚠️  No documents found in {dept} folder")
            continue
        
        # Process each document
        for doc in documents:
            chunks = chunk_text(doc['content'])
            print(f"   📄 {doc['source']}: {len(chunks)} chunks")
            
            for idx, chunk in enumerate(chunks):
                # Determine which roles can access this document
                accessible_roles = []
                for role, allowed_depts in ROLE_DOCUMENT_MAP.items():
                    if dept in allowed_depts:
                        accessible_roles.append(role)
                
                all_chunks.append(chunk)
                all_metadata.append({
                    "department": dept,
                    "source": doc['source'],
                    "chunk_index": idx,
                    "accessible_roles": accessible_roles,
                    "file_type": doc['file_type']
                })
        
        print(f"✅ {dept.upper()}: {len(documents)} documents processed\n")
    
    if not all_chunks:
        print("❌ No documents found! Please check your data folder structure.")
        print("\nExpected structure:")
        print("data/")
        print("  ├── finance/")
        print("  ├── marketing/")
        print("  ├── hr/")
        print("  ├── engineering/")
        print("  └── general/")
        return
    
    # Generate embeddings
    print(f"🔄 Generating embeddings for {len(all_chunks)} chunks...")
    embeddings = model.encode(all_chunks, show_progress_bar=True)
    embeddings = np.array(embeddings).astype('float32')
    print("✅ Embeddings generated\n")
    
    # Create FAISS index
    print("💾 Creating FAISS index...")
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    print("✅ FAISS index created\n")
    
    # Save FAISS index and metadata
    print("💾 Saving vector database...")
    os.makedirs("./vector_db", exist_ok=True)
    
    faiss.write_index(index, "./vector_db/faiss_index.bin")
    
    with open("./vector_db/metadata.pkl", "wb") as f:
        pickle.dump({
            "chunks": all_chunks,
            "metadata": all_metadata
        }, f)
    
    print("✅ Vector database saved successfully!\n")
    
    # Summary
    print("="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Total chunks indexed: {len(all_chunks)}")
    print(f"Total documents processed: {len(set(m['source'] for m in all_metadata))}")
    print(f"Departments covered: {', '.join(departments)}")
    print(f"Vector database location: ./vector_db/")
    print(f"  - faiss_index.bin ({embeddings.nbytes / (1024*1024):.2f} MB)")
    print(f"  - metadata.pkl")
    print("="*70)
    print(f"\nFinished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n✨ Ready for RAG pipeline integration!")

if __name__ == "__main__":
    main()
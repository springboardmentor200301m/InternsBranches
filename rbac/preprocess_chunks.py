import os
import json
import re
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

BASE_DIR = "../data"  
OUTPUT_FILE = "document_chunks.json"
INDEX_DIR = "faiss_index"

ROLE_KEYWORDS = {
    "Finance": ["finance", "financial", "quarterly", "budget", "revenue", "profit", "investment"],
    "Marketing": ["marketing", "campaign", "market", "analytics", "customer", "advertising"],
    "HR": ["hr", "employee", "hiring", "policy", "handbook", "benefits", "payroll"],
    "Engineering": ["engineering", "technical", "architecture", "development", "api", "software"],
    "Employees": ["general", "handbook", "policy", "company", "overview"]
}


def clean_text(text):
    """Clean and normalize text content"""
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\.{2,}', '.', text)
    text = text.strip()
    return text


def determine_accessible_roles(role_folder, filename, content):
    """Determine which roles should have access to this document"""
    accessible_roles = [role_folder]
    
    filename_lower = filename.lower()
    content_lower = content.lower()
    
    for role, keywords in ROLE_KEYWORDS.items():
        if role == role_folder:
            continue
        if any(keyword in filename_lower or keyword in content_lower for keyword in keywords):
            accessible_roles.append(role)
    
    if "C-Level" not in accessible_roles:
        accessible_roles.append("C-Level")
    
    return list(set(accessible_roles))


def load_documents():
    """Load documents with enhanced metadata"""
    documents = []
    stats = {
        "total_files": 0,
        "total_size_bytes": 0,
        "files_by_role": {},
        "files_by_type": {}
    }
    
    for role in os.listdir(BASE_DIR):
        role_path = os.path.join(BASE_DIR, role)
        if not os.path.isdir(role_path):
            continue
        
        stats["files_by_role"][role] = 0
        
        for file in os.listdir(role_path):
            file_path = os.path.join(role_path, file)
            
            if file.endswith((".md", ".txt")):
                file_type = "markdown"
            elif file.endswith(".csv"):
                file_type = "csv"
            else:
                continue
            
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                content = clean_text(content)
                accessible_roles = determine_accessible_roles(role, file, content)
                
                stats["total_files"] += 1
                stats["total_size_bytes"] += len(content)
                stats["files_by_role"][role] += 1
                stats["files_by_type"][file_type] = stats["files_by_type"].get(file_type, 0) + 1
                
                documents.append({
                    "role": role,
                    "file_name": file,
                    "content": content,
                    "accessible_roles": accessible_roles,
                    "file_type": file_type,
                    "file_path": file_path
                })
                
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
    
    return documents, stats


def split_into_chunks(documents):
    """Split documents into chunks with enhanced metadata"""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=512,
        chunk_overlap=50,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    
    chunks = []
    chunk_stats = {
        "total_chunks": 0,
        "chunks_by_role": {},
        "avg_chunk_size": 0
    }
    
    total_chunk_length = 0
    
    for doc in documents:
        texts = splitter.split_text(doc["content"])
        
        for idx, text in enumerate(texts):
            chunk_data = {
                "role": doc["role"],
                "file_name": doc["file_name"],
                "chunk_id": idx,
                "total_chunks": len(texts),
                "chunk": text,
                "accessible_roles": doc["accessible_roles"],
                "file_type": doc["file_type"],
                "source": doc["file_path"]
            }
            chunks.append(chunk_data)
            
            chunk_stats["total_chunks"] += 1
            total_chunk_length += len(text)
            
            for role in doc["accessible_roles"]:
                chunk_stats["chunks_by_role"][role] = \
                    chunk_stats["chunks_by_role"].get(role, 0) + 1
    
    chunk_stats["avg_chunk_size"] = total_chunk_length / chunk_stats["total_chunks"] if chunk_stats["total_chunks"] > 0 else 0
    
    return chunks, chunk_stats


def save_metadata_mapping(chunks, output_path="metadata_mapping.json"):
    """Save metadata mapping for documentation"""
    mapping = []
    for chunk in chunks:
        mapping.append({
            "source": chunk["file_name"],
            "chunk_id": chunk["chunk_id"],
            "accessible_roles": chunk["accessible_roles"],
            "file_type": chunk["file_type"],
            "preview": chunk["chunk"][:100] + "..."
        })
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(mapping, f, indent=2)
    
    print(f"✅ Metadata mapping saved to {output_path}")


def print_statistics(file_stats, chunk_stats):
    """Print comprehensive statistics"""
    print("\n" + "="*60)
    print("PREPROCESSING STATISTICS")
    print("="*60)
    
    print(f"\n📁 File Statistics:")
    print(f"   Total Files Processed: {file_stats['total_files']}")
    print(f"   Total Size: {file_stats['total_size_bytes']:,} bytes")
    
    print(f"\n   Files by Role:")
    for role, count in file_stats['files_by_role'].items():
        print(f"      • {role}: {count} files")
    
    print(f"\n   Files by Type:")
    for file_type, count in file_stats['files_by_type'].items():
        print(f"      • {file_type}: {count} files")
    
    print(f"\n📄 Chunk Statistics:")
    print(f"   Total Chunks: {chunk_stats['total_chunks']}")
    print(f"   Average Chunk Size: {chunk_stats['avg_chunk_size']:.0f} characters")
    
    print(f"\n   Chunks by Role Access:")
    for role, count in sorted(chunk_stats['chunks_by_role'].items()):
        print(f"      • {role}: {count} accessible chunks")
    
    print("\n" + "="*60)


def run_preprocessing():
    """Main preprocessing pipeline with validation"""
    print("="*60)
    print("STARTING DOCUMENT PREPROCESSING")
    print("="*60)
    
    print("\n📂 Loading documents...")
    docs, file_stats = load_documents()
    print(f"✅ Loaded {len(docs)} documents")
    
    print("\n✂️  Splitting into chunks...")
    chunks, chunk_stats = split_into_chunks(docs)
    print(f"✅ Created {len(chunks)} chunks")
    
    print_statistics(file_stats, chunk_stats)
    
    print("\n💾 Saving document chunks...")
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2)
    print(f"✅ Chunks saved to {OUTPUT_FILE}")
    
    print("\n📋 Saving metadata mapping...")
    save_metadata_mapping(chunks)
    
    print("\n🔢 Generating embeddings...")
    embed_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    texts = [c["chunk"] for c in chunks]
    
    print("\n🗄️  Creating vector store...")
    vector_store = FAISS.from_texts(texts, embed_model)
    
    print("\n💾 Saving vector index...")
    os.makedirs(INDEX_DIR, exist_ok=True)
    vector_store.save_local(INDEX_DIR)
    print(f"✅ Vector index saved to {INDEX_DIR}")
    
    print("\n" + "="*60)
    print("VALIDATION CHECKS")
    print("="*60)
    
    all_have_roles = all("accessible_roles" in c for c in chunks)
    print(f"\n{'✅' if all_have_roles else '❌'} All chunks have accessible_roles metadata")
    
    c_level_access = sum(1 for c in chunks if "C-Level" in c["accessible_roles"])
    print(f"{'✅' if c_level_access == len(chunks) else '❌'} C-Level has access to all {len(chunks)} chunks")
    
    print("\n" + "="*60)
    print("SAMPLE CHUNKS")
    print("="*60)
    
    for i, chunk in enumerate(chunks[:3], 1):
        print(f"\n📄 Sample Chunk #{i}")
        print(f"   Source: {chunk['file_name']}")
        print(f"   Chunk ID: {chunk['chunk_id']}/{chunk['total_chunks']}")
        print(f"   Accessible Roles: {', '.join(chunk['accessible_roles'])}")
        print(f"   Preview: {chunk['chunk'][:150]}...")
    
    print("\n" + "="*60)
    print("✅ MODULE 2 PREPROCESSING COMPLETE!")
    print("="*60)
    print("\n📋 Deliverables Created:")
    print("   ✅ Preprocessing module")
    print("   ✅ Cleaned and formatted document chunks")
    print("   ✅ Role-based metadata mapping")
    print("   ✅ Vector database with embeddings")
    print("   ✅ Validation and quality assurance report")
    print("\n🎯 Next Step: Module 3 - Backend Auth & Search")


if __name__ == "__main__":
    run_preprocessing()
import os
import chromadb

# --------------------------------------------------
# Project root & paths
# --------------------------------------------------
PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

CHROMA_PATH = os.path.join(PROJECT_ROOT, "data", "chroma_db")
COLLECTION_NAME = "company_docs"

def main():
    print(f"Opening ChromaDB at: {CHROMA_PATH}")

    # 1. Open persistent ChromaDB
    client = chromadb.PersistentClient(
        path=CHROMA_PATH
    )

    # 2. Safely load collection
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME
    )

    # 3. Verify record count
    count = collection.count()
    print(f"Total records in DB: {count}")

    # 4. Peek one record (if exists)
    if count > 0:
        sample = collection.peek(1)
        print("\nSample record:")
        print(sample)
    else:
        print("⚠️ No records found in collection.")

if __name__ == "__main__":
    main()

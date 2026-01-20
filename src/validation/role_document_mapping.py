import json
from collections import defaultdict

DATA_PATH = "data/processed_chunks_with_metadata.json"

def generate_role_document_mapping():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    role_map = defaultdict(set)

    for chunk in chunks:
        for role in chunk["allowed_roles"]:
            role_map[role].add(chunk["document_name"])

    print("\n----- ROLE → DOCUMENT ACCESS MAP -----\n")
    for role, docs in role_map.items():
        print(f"{role}:")
        for doc in sorted(docs):
            print(f"  - {doc}")
        print()

if __name__ == "__main__":
    generate_role_document_mapping()

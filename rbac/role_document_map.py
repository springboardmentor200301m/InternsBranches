import os
import json

BASE_DIR = "data"  # Your main data folder

def load_documents_with_roles():
    role_map = {}

    # Walk through each role folder inside data/
    for role in os.listdir(BASE_DIR):
        role_path = os.path.join(BASE_DIR, role)

        if not os.path.isdir(role_path):
            continue

        # Collect files for this role
        files = []
        for file in os.listdir(role_path):
            file_path = os.path.join(role_path, file)

            # Accept only .md and .txt files
            if file.endswith(".md") or file.endswith(".txt"):
                files.append(file_path)

        if files:
            role_map[role] = files

    # Save role mapping as JSON (for milestone tracking)
    with open("rbac/document_chunks.json", "w", encoding="utf-8") as f:
        json.dump(role_map, f, indent=2)

    return role_map


# Export function for other modules
__all__ = ["load_documents_with_roles"]

# If running this file directly, show output
if __name__ == "__main__":
    print("Loading documents by role...\n")
    result = load_documents_with_roles()
    print("Role → Document Mapping Output:")
    print(json.dumps(result, indent=2))
    print("\nMapping saved to document_chunks.json")

import os

BASE_DIR = "data_repo"   

def explore_documents():
    print("\n--------- DOCUMENT EXPLORATION REPORT ---------\n")

    for root, dirs, files in os.walk(BASE_DIR):
        for file in files:
            if file.endswith(".md") or file.endswith(".csv"):
                file_path = os.path.join(root, file)
                print(f"FILE FOUND: {file_path}")

                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        preview = "".join(f.readlines()[:5])
                except:
                    preview = "(Unable to preview this file — likely CSV encoding)"

                print("Preview:")
                print(preview)
                print("-" * 80)

if __name__ == "__main__":
    explore_documents()

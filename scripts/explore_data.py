import os
from pathlib import Path
import textwrap
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data" / "raw"

DEPARTMENT_FOLDERS = ["Finance", "HR", "engineering", "general", "marketing"]

def summarize_markdown(path: Path, max_lines: int = 5) -> str:
    try:
        with path.open("r", encoding="utf-8") as f:
            lines = f.readlines()
        preview = "".join(lines[:max_lines])
        return preview.strip()
    except Exception as e:
        return f"<Error reading file: {e}>"

def summarize_hr_csv(path: Path, max_rows: int = 5) -> str:
    try:
        df = pd.read_csv(path)
        return f"Columns: {list(df.columns)}\nSample rows:\n{df.head(max_rows).to_string(index=False)}"
    except Exception as e:
        return f"<Error reading CSV: {e}>"

def main():
    print(f"Base data directory: {DATA_DIR}")
    print("=" * 60)

    for dept in DEPARTMENT_FOLDERS:
        folder = DATA_DIR / dept
        print(f"\n### Department: {dept}")
        print("-" * 60)

        if not folder.exists():
            print(f"Folder NOT FOUND: {folder}")
            continue

        files = list(folder.iterdir())
        print(f"Total files: {len(files)}")

        for file in files:
            if file.is_dir():
                # In case there are nested folders later
                print(f" Subfolder: {file.name}")
                continue

            print(f"\nFile: {file.name}")
            if file.suffix.lower() == ".md":
                preview = summarize_markdown(file)
                print(" Type: Markdown")
                print(" Preview:")
                print(textwrap.indent(preview, "   "))
            elif file.suffix.lower() == ".csv":
                preview = summarize_hr_csv(file)
                print(" Type: CSV")
                print(" Preview:")
                print(textwrap.indent(preview, "   "))
            else:
                print(f" Type: Unknown ({file.suffix})")

if __name__ == "__main__":
    main()

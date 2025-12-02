import json
import re
from pathlib import Path
from typing import List, Dict

import pandas as pd

from app.config import (
    BASE_DIR,
    DATA_RAW_DIR,
    DATA_PROCESSED_DIR,
    DEPARTMENTS,
    DEPARTMENT_IDS,
    DEPARTMENT_TO_ROLES,
)

# === Basic text cleaning ===

def clean_text(text: str) -> str:
    """
    Simple cleaner:
    - normalize newlines
    - collapse multiple spaces
    - strip leading/trailing whitespace
    """
    if not isinstance(text, str):
        text = str(text)

    # Normalize newlines
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Remove super long runs of blank lines (max 2)
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Collapse weird spaces
    text = re.sub(r"[ \t]+", " ", text)

    # Strip
    return text.strip()


# === Chunking util (approx "tokens" via words) ===

def chunk_text(
    text: str,
    max_tokens: int = 300,
    overlap: int = 50,
) -> List[str]:
    """
    Very rough token approximation using words.
    max_tokens ~ max words per chunk.
    overlap ~ overlapping words between chunks for context continuity.
    """
    words = text.split()
    if not words:
        return []

    chunks = []
    start = 0
    n = len(words)

    while start < n:
        end = min(start + max_tokens, n)
        chunk_words = words[start:end]
        chunk = " ".join(chunk_words).strip()
        if chunk:
            chunks.append(chunk)
        # move with overlap
        if end == n:
            break
        start = end - overlap

    return chunks


# === Markdown parsing ===

def process_markdown_file(
    file_path: Path,
    department_folder: str,
) -> List[Dict]:
    """
    Read a markdown file, clean it, and chunk it.
    Returns list of chunk dicts with metadata.
    """
    with file_path.open("r", encoding="utf-8") as f:
        raw_text = f.read()

    cleaned = clean_text(raw_text)
    chunks = chunk_text(cleaned, max_tokens=300, overlap=50)

    dept_id = DEPARTMENT_IDS[department_folder]
    allowed_roles = DEPARTMENT_TO_ROLES.get(department_folder, [])

    base_id = f"{department_folder}/{file_path.name}"

    chunk_dicts = []
    for idx, chunk in enumerate(chunks):
        chunk_id = f"{base_id}::chunk_{idx}"
        chunk_dicts.append(
            {
                "id": chunk_id,
                "text": chunk,
                "source_file": file_path.name,
                "source_path": str(file_path.relative_to(DATA_RAW_DIR)),
                "department": dept_id,
                "chunk_index": idx,
                "allowed_roles": allowed_roles,
            }
        )

    return chunk_dicts


# === HR CSV → row-wise mini documents ===

def process_hr_csv(
    file_path: Path,
    department_folder: str,
) -> List[Dict]:
    """
    Convert each HR CSV row into a mini-document and then directly
    treat each row as a 'chunk' (rows are already small).
    """
    df = pd.read_csv(file_path)

    dept_id = DEPARTMENT_IDS[department_folder]
    allowed_roles = DEPARTMENT_TO_ROLES.get(department_folder, [])

    chunk_dicts = []

    for idx, row in df.iterrows():
        # Build a human-readable text block
        # You can customize which fields to include / mask later
        fields = []

        # Safely access known columns if they exist
        def add_field(label: str, col: str):
            if col in df.columns:
                val = row[col]
                fields.append(f"{label}: {val}")

        add_field("Employee ID", "employee_id")
        add_field("Name", "full_name")
        add_field("Role", "role")
        add_field("Department", "department")
        add_field("Email", "email")
        add_field("Location", "location")
        add_field("Date of Birth", "date_of_birth")
        add_field("Date of Joining", "date_of_joining")
        add_field("Manager ID", "manager_id")
        add_field("Salary", "salary")
        add_field("Leave Balance", "leave_balance")
        add_field("Leaves Taken", "leaves_taken")
        add_field("Attendance %", "attendance_pct")
        add_field("Performance Rating", "performance_rating")
        add_field("Last Review Date", "last_review_date")

        mini_doc = "\n".join(fields)
        mini_doc = clean_text(mini_doc)

        # If we wanted, we could still chunk this, but rows are small enough
        chunk_id = f"{department_folder}/{file_path.name}::row_{idx}"

        chunk_dicts.append(
            {
                "id": chunk_id,
                "text": mini_doc,
                "source_file": file_path.name,
                "source_path": str(file_path.relative_to(DATA_RAW_DIR)),
                "department": dept_id,
                "chunk_index": idx,
                "allowed_roles": allowed_roles,
            }
        )

    return chunk_dicts


# === Main preprocessing pipeline ===

def preprocess_all_documents() -> None:
    all_chunks: List[Dict] = []

    print(f"Raw data dir: {DATA_RAW_DIR}")
    print("=" * 80)

    for department_folder in DEPARTMENTS:
        dept_dir = DATA_RAW_DIR / department_folder
        print(f"\n=== Processing department: {department_folder} ===")

        if not dept_dir.exists():
            print(f"  WARNING: directory not found: {dept_dir}")
            continue

        for file_path in dept_dir.iterdir():
            if file_path.is_dir():
                # In case of nested structure later
                print(f"  Skipping subdirectory: {file_path.name}")
                continue

            suffix = file_path.suffix.lower()
            print(f"  File: {file_path.name} ({suffix})")

            if suffix == ".md":
                chunks = process_markdown_file(file_path, department_folder)
            elif suffix == ".csv" and department_folder == "HR":
                chunks = process_hr_csv(file_path, department_folder)
            else:
                print(f"    Skipping unsupported file type: {suffix}")
                continue

            print(f"    Generated {len(chunks)} chunks")
            all_chunks.extend(chunks)

    # Save all chunks to JSONL for later embedding
    out_path = DATA_PROCESSED_DIR / "document_chunks.jsonl"
    with out_path.open("w", encoding="utf-8") as f:
        for chunk in all_chunks:
            f.write(json.dumps(chunk, ensure_ascii=False) + "\n")

    print("\n=== Preprocessing complete ===")
    print(f"Total chunks: {len(all_chunks)}")
    print(f"Saved to: {out_path}")

    # Simple QA summary
    summarize_chunks(all_chunks)


def summarize_chunks(chunks: List[Dict]) -> None:
    from collections import Counter

    dept_counts = Counter(c["department"] for c in chunks)
    role_counts = Counter()

    for c in chunks:
        for r in c["allowed_roles"]:
            role_counts[r] += 1

    print("\n--- Chunk counts by department ---")
    for dept, count in dept_counts.items():
        print(f"  {dept}: {count}")

    print("\n--- Accessible chunks per role ---")
    for role, count in role_counts.items():
        print(f"  {role}: {count}")


if __name__ == "__main__":
    preprocess_all_documents()

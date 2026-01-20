import json
import os
import sys

# ---- FIX: Add project root to Python path ----
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(PROJECT_ROOT)

from src.utils.role_metadata import ROLE_TO_DEPT

DATA_PATH = "data/processed_chunks_with_metadata.json"
VALID_DEPARTMENTS = {"Finance", "Marketing", "HR", "Engineering", "General"}

def verify_metadata():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    for i, chunk in enumerate(chunks):
        dept = chunk["department"]
        roles = chunk["allowed_roles"]

        if dept not in VALID_DEPARTMENTS:
            raise ValueError(f"Invalid department in chunk {i}: {dept}")

        for role in roles:
            if dept not in ROLE_TO_DEPT.get(role, []):
                raise ValueError(
                    f"Role '{role}' incorrectly assigned to {dept} in chunk {i}"
                )

    print("✅ Metadata verification PASSED")

if __name__ == "__main__":
    verify_metadata()

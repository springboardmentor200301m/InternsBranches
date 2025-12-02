from pathlib import Path
from collections import defaultdict

# Base directories
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_RAW_DIR = BASE_DIR / "data" / "raw" 
DATA_PROCESSED_DIR = BASE_DIR / "data" / "processed"

DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# Departments = folder names (case-sensitive as on disk)
DEPARTMENTS = ["Finance", "HR", "engineering", "general", "marketing"]

# Canonical department ids (lowercase for metadata)
DEPARTMENT_IDS = {
    "Finance": "finance",
    "HR": "hr",
    "engineering": "engineering",
    "general": "general",
    "marketing": "marketing",
}

# Roles (lowercase)
ROLES = ["finance", "marketing", "hr", "engineering", "employee", "c_level"]

# Role → which department folders they can see
ROLE_TO_DEPARTMENTS = {
    "finance": ["Finance", "general"],
    "marketing": ["marketing", "general"],
    "hr": ["HR", "general"],
    "engineering": ["engineering", "general"],
    "employee": ["general"],   # strict for now
    "c_level": ["Finance", "HR", "engineering", "marketing", "general"],
}

# Invert into department → allowed roles (for metadata)
DEPARTMENT_TO_ROLES = defaultdict(list)
for role, dept_list in ROLE_TO_DEPARTMENTS.items():
    for dept in dept_list:
        DEPARTMENT_TO_ROLES[dept].append(role)

DEPARTMENT_TO_ROLES = dict(DEPARTMENT_TO_ROLES)




# Vector DB directory
VECTOR_DB_DIR = BASE_DIR / "data" / "vector_db"
VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)

# Chroma collection name
VECTOR_COLLECTION_NAME = "company_docs"

# Role hierarchy: who can see whose documents
ROLE_HIERARCHY = {
    "Employees": 1,
    "HR": 2,
    "Finance": 2,
    "Marketing": 2,
    "Engineering": 2,
    "C-Level": 3
}



def detect_department(file_path):
    file_path = file_path.lower()

    if "finance" in file_path:
        return "Finance"
    if "marketing" in file_path:
        return "Marketing"
    if "hr" in file_path:
        return "HR"
    if "engineering" in file_path:
        return "Engineering"
    if "general" in file_path:
        return "General"

    return "General"


ROLE_TO_DEPT = {
    "Finance": ["Finance"],
    "Marketing": ["Marketing"],
    "Engineering": ["Engineering"],
    "Employees": ["General"],
    "HR": ["HR", "General"],              # ✅ FIXED
    "C-Level": ["Finance", "Marketing", "HR", "Engineering", "General"]
}


def allowed_roles_for_department(dept):
    return ROLE_TO_DEPT.get(dept, ["Employees"])

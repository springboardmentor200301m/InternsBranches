# src/rbac/identify_user.py

ROLE_HIERARCHY = {
    "C-Level": ["C-Level", "HR", "Employees"],
    "HR": ["HR", "Employees"],
    "Employees": ["Employees"],
    "Finance": ["Finance"],
    "Marketing": ["Marketing"],
    "Engineering": ["Engineering"]
}

def get_user_role():
    print("\nAvailable roles:")
    for role in ROLE_HIERARCHY.keys():
        print(f"- {role}")

    role = input("\nEnter your role: ").strip()

    if role not in ROLE_HIERARCHY:
        raise ValueError("❌ Invalid role selected")

    print(f"\nUser Role Identified: {role}")
    return role


def get_accessible_roles(user_role):
    """
    Returns list of roles the user is allowed to access
    """
    return ROLE_HIERARCHY[user_role]

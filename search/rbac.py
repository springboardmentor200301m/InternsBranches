ROLE_HIERARCHY = {
    "c_level": ["finance", "hr", "engineering", "marketing", "general", "employees"],
    "finance": ["finance"],
    "hr": ["hr"],
    "engineering": ["engineering"],
    "marketing": ["marketing"],
    "employees": ["general"]
}

def has_access(user_role, allowed_roles):
    return any(role in ROLE_HIERARCHY.get(user_role, []) for role in allowed_roles)

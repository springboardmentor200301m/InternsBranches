def authenticate_user(username: str, role: str):
    if not username or not username.strip():
        return None, "Username cannot be empty"

    allowed_roles = [
        "Finance",
        "HR",
        "Marketing",
        "Engineering",
        "Employee",
        "C-Level",
    ]

    if role not in allowed_roles:
        return None, "Invalid role selected"

    return {
        "username": username.strip(),
        "role": role,
    }, None

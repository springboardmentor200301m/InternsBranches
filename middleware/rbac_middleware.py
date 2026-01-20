def enforce_rbac(user_role, chunk_roles):
    return user_role in chunk_roles or user_role == "c_level"

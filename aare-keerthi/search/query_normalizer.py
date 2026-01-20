import re

def normalize_query(query: str):
    if not query or not query.strip():
        return None

    query = query.lower()
    query = re.sub(r"[^a-z0-9\s]", "", query)
    return query.strip()

import requests

BACKEND_URL = "http://localhost:8000"

def login(username, password):
    res = requests.post(
        f"{BACKEND_URL}/auth/login",
        json={"username": username, "password": password}
    )
    if res.status_code == 200:
        return res.json()
    return None

def chat_query(token, query):
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.post(
        f"{BACKEND_URL}/chat/query",
        json={"query": query},
        headers=headers
    )
    if res.status_code == 200:
        return res.json()
    return None

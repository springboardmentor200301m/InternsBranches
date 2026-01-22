import streamlit as st
import requests

BACKEND_URL = "http://127.0.0.1:8000"


# ---------------------------
# Auth helpers
# ---------------------------
def get_auth_headers():
    token = st.session_state.get("access_token")
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}


# ---------------------------
# Login
# ---------------------------
def login(username: str, password: str) -> bool:
    url = f"{BACKEND_URL}/auth/login"
    data = {
        "username": username,
        "password": password,
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    resp = requests.post(url, data=data, headers=headers)

    if resp.status_code != 200:
        st.error("Login failed: incorrect username or password.")
        return False

    token_data = resp.json()
    st.session_state["access_token"] = token_data["access_token"]
    st.session_state["token_type"] = token_data["token_type"]

    me_resp = requests.get(f"{BACKEND_URL}/auth/me", headers=get_auth_headers())
    if me_resp.status_code == 200:
        st.session_state["current_user"] = me_resp.json()

    return True


# ---------------------------
# Register
# ---------------------------
def register(username: str, password: str, role: str) -> bool:
    url = f"{BACKEND_URL}/auth/register"
    body = {
        "username": username,
        "password": password,
        "role": role,
    }

    headers = {"Content-Type": "application/json"}
    resp = requests.post(url, json=body, headers=headers)

    if resp.status_code == 200:
        st.success("Registration successful! You can now log in.")
        return True
    else:
        st.error(f"Registration failed: {resp.text}")
        return False


# ---------------------------
# UI: Register
# ---------------------------
def render_register():
    st.title("📝 Register New User")

    username = st.text_input("Username", key="reg_username")
    password = st.text_input("Password", type="password", key="reg_password")

    role = st.selectbox(
        "Select Role",
        [
            "employee",
            "hr",
            "finance",
            "engineering",
            "marketing",
            "c_level",
        ],
    )

    if st.button("Register"):
        if not username or not password:
            st.warning("Username and password are required.")
        else:
            register(username, password, role)


# ---------------------------
# UI: Login
# ---------------------------
def render_login():
    st.title("🤖 Company Internal Chatbot - Login")

    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login"):
        if not username or not password:
            st.warning("Please enter both username and password.")
        else:
            if login(username, password):
                st.rerun()


# ---------------------------
# Chat
# ---------------------------
def call_rag(query: str, top_k: int = 4):
    url = f"{BACKEND_URL}/rag"
    body = {"query": query, "top_k": top_k}
    headers = get_auth_headers()
    headers["Content-Type"] = "application/json"

    resp = requests.post(url, json=body, headers=headers)
    if resp.status_code != 200:
        st.error(resp.text)
        return None

    return resp.json()


def logout():
    for key in ["access_token", "token_type", "current_user", "chat_history"]:
        st.session_state.pop(key, None)


def render_chat():
    user = st.session_state.get("current_user")

    st.sidebar.title("User Info")
    st.sidebar.markdown(f"*Username:* {user['username']}")
    st.sidebar.markdown(f"*Role:* {user['role']}")

    if st.sidebar.button("Logout"):
        logout()
        st.rerun()

    st.title("🏢 Company Internal Chatbot")

    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []
        rag_response = None

    with st.form("chat_form"):
        query = st.text_area("Your question")
        submitted = st.form_submit_button("Ask")

    if submitted and query.strip():
        with st.spinner("Thinking..."):
            rag_response = call_rag(query)
    if rag_response:
        # Store both user query and bot answer
        st.session_state["chat_history"].append({
            "query": query,
            "answer": rag_response.get("answer", ""),
            "sources": rag_response.get("sources", [])
        })

# Render chat history safely
for item in st.session_state.get("chat_history", []):
    st.markdown(f"*You:* {item.get('query', 'Unknown question')}")
    st.markdown(f"*Bot:* {item.get('answer', 'No answer')}")
    st.markdown("---")
    # Optional: show sources
    for src in item.get("sources", []):
        with st.expander(f"Source: {src.get('id', 'Unknown')}"):
            st.markdown(f"- Dept: {src.get('department', '')}")
            st.markdown(f"- File: {src.get('source_file', '')}")
            st.markdown(f"- Score: {src.get('score', 0):.3f}")
            st.markdown(f"- Snippet: {src.get('snippet', '')}")

# ---------------------------
# Main
# ---------------------------
def main():
    st.set_page_config(page_title="Company Internal Chatbot", layout="wide")

    if "access_token" not in st.session_state:
        mode = st.radio("Choose action", ["Login", "Register"])
        render_login() if mode == "Login" else render_register()
    else:
        render_chat()


if __name__ == "__main__":
    main()
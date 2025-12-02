import streamlit as st
import requests

BACKEND_URL = "http://127.0.0.1:8000"


def get_auth_headers():
    token = st.session_state.get("access_token")
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}


def login(username: str, password: str) -> bool:
    url = f"{BACKEND_URL}/auth/login"
    data = {
        "username": username,
        "password": password,
    }

    # OAuth2 password flow expects form-encoded data
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    resp = requests.post(url, data=data, headers=headers)
    if resp.status_code != 200:
        st.error("Login failed: incorrect username or password.")
        return False

    token_data = resp.json()
    st.session_state["access_token"] = token_data["access_token"]
    st.session_state["token_type"] = token_data["token_type"]

    # Fetch current user info
    me_resp = requests.get(f"{BACKEND_URL}/auth/me", headers=get_auth_headers())
    if me_resp.status_code == 200:
        st.session_state["current_user"] = me_resp.json()
    else:
        st.session_state["current_user"] = None

    return True


def logout():
    st.session_state.pop("access_token", None)
    st.session_state.pop("token_type", None)
    st.session_state.pop("current_user", None)


def call_rag(query: str, top_k: int = 4):
    url = f"{BACKEND_URL}/rag"
    body = {"query": query, "top_k": top_k}
    headers = get_auth_headers()
    headers["Content-Type"] = "application/json"

    resp = requests.post(url, json=body, headers=headers)
    if resp.status_code != 200:
        st.error(f"Error from backend: {resp.status_code} - {resp.text}")
        return None

    return resp.json()


def render_login():
    st.title("🔐 Company Internal Chatbot - Login")

    username = st.text_input("Username", value="", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login"):
        if not username or not password:
            st.warning("Please enter both username and password.")
        else:
            success = login(username, password)
            if success:
                st.rerun()


def render_chat():
    user = st.session_state.get("current_user")
    st.sidebar.title("User Info")

    if user:
        st.sidebar.markdown(f"**Username:** `{user['username']}`")
        st.sidebar.markdown(f"**Role:** `{user['role']}`")
    else:
        st.sidebar.warning("No user info loaded.")

    if st.sidebar.button("Logout"):
        logout()
        st.rerun()

    st.title("🏢 Company Internal Chatbot")

    st.markdown(
        "Ask questions about finance, marketing, HR, engineering, or company policies. "
        "Responses are restricted based on your role."
    )

    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    with st.form("chat_form"):
        query = st.text_area("Your question", height=80)
        submitted = st.form_submit_button("Ask")

    if submitted:
        if not query.strip():
            st.warning("Please enter a question.")
        else:
            with st.spinner("Thinking..."):
                rag_response = call_rag(query)
            if rag_response is not None:
                st.session_state["chat_history"].append(
                    {
                        "query": query,
                        "answer": rag_response["answer"],
                        "sources": rag_response["sources"],
                    }
                )

    # Render history (latest at bottom)
    for item in st.session_state["chat_history"]:
        st.markdown(f"**You:** {item['query']}")
        st.markdown(f"**Bot:** {item['answer']}")

        # Show sources in an expander
        with st.expander("Sources used"):
            for src in item["sources"]:
                st.markdown(
                    f"- `{src['id']}`  "
                    f"(dept: `{src['department']}`, file: `{src['source_file']}`, score: `{src['score']:.3f}`)"
                )
                st.markdown(f"  ↳ _{src['snippet']}_")
        st.markdown("---")


def main():
    st.set_page_config(
        page_title="Company Internal Chatbot",
        page_icon="💼",
        layout="wide",
    )

    if "access_token" not in st.session_state:
        render_login()
    else:
        render_chat()


if __name__ == "__main__":
    main()

import streamlit as st
import requests
from jose import jwt


st.set_page_config(
    page_title="Company RAG Assistant",
    layout="wide"
)


BACKEND_URL = "http://127.0.0.1:8000"
LOGIN_ENDPOINT = f"{BACKEND_URL}/login"
CHAT_ENDPOINT = f"{BACKEND_URL}/chat"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "token" not in st.session_state:
    st.session_state.token = None
if "role" not in st.session_state:
    st.session_state.role = None
if "messages" not in st.session_state:
    st.session_state.messages = []


def login(username, password):
    try:
        payload = {"username": username, "password": password}
        res = requests.post(LOGIN_ENDPOINT, json=payload)
        
        if res.status_code == 200:
            data = res.json()
            token = data["access_token"]
            

            decoded = jwt.decode(token, key="secret", options={"verify_signature": False})
            
            st.session_state.authenticated = True
            st.session_state.token = token
            st.session_state.role = decoded.get("role")
            st.session_state.username = username
            st.rerun()
        else:
            st.error("Invalid Username or Password")
    except requests.exceptions.ConnectionError:
        st.error(f"❌ Could not connect to Backend at {BACKEND_URL}. Is it running?")

def logout():
    st.session_state.authenticated = False
    st.session_state.token = None
    st.session_state.role = None
    st.session_state.messages = []
    st.rerun()

def get_response(query):
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    try:
        res = requests.post(CHAT_ENDPOINT, json={"query": query}, headers=headers)
        if res.status_code == 200:
            return res.json()
        elif res.status_code == 401:
            st.error("Session expired. Please log in again.")
            logout()
            return None
        else:
            return {"answer": f"Error {res.status_code}: {res.text}", "sources": [], "confidence": 0}
    except Exception as e:
        return {"answer": f"Connection Error: {str(e)}", "sources": [], "confidence": 0}


def render_login():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.header("🔐 Secure Login")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Log In", use_container_width=True)
            
            if submitted:
                login(username, password)

def render_sidebar():
    with st.sidebar:
        st.markdown(f"### 👤 User: **{st.session_state.username}**")
        st.markdown(f"### 🛡️ Role: **{st.session_state.role}**")
        st.divider()
        if st.button("Logout", type="primary", use_container_width=True):
            logout()
        st.markdown("---")
        st.markdown("*Company Internal Tool v2.0*")

def render_chat():
    st.title("💬 Company Knowledge Base")
    st.caption("Ask questions about HR, Finance, or Engineering policies based on your role.")


    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("sources"):
                with st.expander("📚 View Sources & Confidence"):
                    st.write(f"**Confidence Score:** {msg['confidence']}")
                    for src in msg["sources"]:
                        st.markdown(f"- **{src['title']}** ({src['dept']}) - *{src['section']}*")


    if query := st.chat_input("Ask a question..."):
        st.session_state.messages.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(query)
        with st.chat_message("assistant"):
            with st.spinner("Analyzing documents..."):
                response = get_response(query)
                
                if response:
                    answer = response.get("answer", "No response.")
                    sources = response.get("sources", [])
                    confidence = response.get("confidence", 0.0)

                    st.markdown(answer)
                    
                    if sources:
                        with st.expander("📚 View Sources & Confidence"):
                            st.write(f"**Confidence Score:** {confidence}")
                            for src in sources:
                                st.markdown(f"- **{src['title']}** ({src['dept']}) - *{src['section']}*")
                    
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources,
                        "confidence": confidence
                    })


def main():
    if not st.session_state.authenticated:
        render_login()
    else:
        render_sidebar()
        render_chat()

if __name__ == "__main__":
    main()


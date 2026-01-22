import streamlit as st
import requests

# ================= CONFIG =================
BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Oracle | Company Knowledge Chatbot",
    layout="wide",
)

# ================= STYLING =================
def apply_custom_css():
    st.markdown("""
    <style>
        .stApp {
            background: radial-gradient(circle at top right, #1e1b4b, #0f172a, #020617);
            color: #e2e8f0;
        }

        [data-testid="stSidebar"] {
            background-color: rgba(15, 23, 42, 0.85);
            border-right: 1px solid rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
        }

        .stTextInput input, .stTextArea textarea {
            background-color: rgba(255,255,255,0.05) !important;
            color: white !important;
            border-radius: 10px !important;
            border: 1px solid rgba(255,255,255,0.1) !important;
        }

        .stButton>button {
            background: linear-gradient(45deg, #4338ca, #6d28d9) !important;
            color: white !important;
            border-radius: 10px !important;
            font-weight: 600;
            letter-spacing: 1px;
        }

        [data-testid="stChatMessage"] {
            background-color: rgba(255,255,255,0.04);
            border-radius: 16px;
            border: 1px solid rgba(255,255,255,0.06);
            padding: 10px;
        }

        h1, h2, h3 {
            color: #f8fafc;
        }
    </style>
    """, unsafe_allow_html=True)

# ================= AUTH HELPERS =================
def get_auth_headers():
    token = st.session_state.get("access_token")
    return {"Authorization": f"Bearer {token}"} if token else {}

def login(username, password):
    url = f"{BACKEND_URL}/auth/login"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {"username": username, "password": password}

    resp = requests.post(url, data=data, headers=headers)
    if resp.status_code != 200:
        st.error("❌ Invalid credentials")
        return False

    token_data = resp.json()
    st.session_state.access_token = token_data["access_token"]

    me = requests.get(f"{BACKEND_URL}/auth/me", headers=get_auth_headers())
    st.session_state.current_user = me.json() if me.status_code == 200 else None

    st.rerun()

def logout():
    for k in ["access_token", "current_user", "messages"]:
        st.session_state.pop(k, None)
    st.rerun()

# ================= RAG =================
def call_rag(query, top_k=4):
    url = f"{BACKEND_URL}/rag"
    headers = get_auth_headers()
    headers["Content-Type"] = "application/json"
    resp = requests.post(url, json={"query": query, "top_k": top_k}, headers=headers)

    if resp.status_code != 200:
        st.error("Backend error")
        return None
    return resp.json()

# ================= LOGIN UI =================
def render_login():
    apply_custom_css()
    _, col, _ = st.columns([1, 1.4, 1])

    with col:
        st.markdown("""
        <h1 style='text-align:center; letter-spacing:10px;'>ORACLE</h1>
        <p style='text-align:center; color:#94a3b8;'>Internal Company Knowledge System</p>
        """, unsafe_allow_html=True)

        with st.form("login"):
            u = st.text_input("Identity")
            p = st.text_input("Passphrase", type="password")
            submitted = st.form_submit_button("Authenticate", use_container_width=True)

            if submitted:
                login(u, p)

# ================= SIDEBAR =================
def render_sidebar():
    user = st.session_state.get("current_user")
    with st.sidebar:
        st.markdown("## SYSTEM")

        if user:
            st.markdown(f"""
            <div style="padding:15px; background:rgba(255,255,255,0.05); border-radius:12px;">
                <p style="color:#94a3b8; font-size:0.8rem;">USER</p>
                <b>{user['username']}</b>
                <p style="color:#94a3b8; font-size:0.8rem; margin-top:10px;">ROLE</p>
                <b style="color:#818cf8;">{user['role']}</b>
            </div>
            """, unsafe_allow_html=True)

        st.write("---")
        if st.button("Terminate Session", use_container_width=True):
            logout()

# ================= CHAT UI =================
def render_chat():
    apply_custom_css()
    render_sidebar()

    st.title("Knowledge Oracle")
    st.caption("Ask across HR, Finance, Engineering & Policy domains")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("sources"):
                with st.expander("Source Metadata"):
                    for s in msg["sources"]:
                        st.markdown(
                            f"**{s['department']}** | `{s['source_file']}` | score `{s['score']:.3f}`\n\n_{s['snippet']}_"
                        )

    if query := st.chat_input("Query the archives..."):
         # 1️⃣ Immediately show user message
        with st.chat_message("user"):
            st.markdown(query)
        st.session_state.messages.append({"role": "user", "content": query})

        with st.chat_message("assistant"):
            with st.spinner("Decrypting knowledge layers..."):
                res = call_rag(query)
                if res:
                    answer = res["answer"]
                    sources = res["sources"]

                    st.markdown(answer)
                    if sources:
                        with st.expander("Source Metadata"):
                            for s in sources:
                                st.markdown(
                                    f"**{s['department']}** | `{s['source_file']}` | `{s['score']:.3f}`\n\n_{s['snippet']}_"
                                )

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources
                    })

# ================= MAIN =================
def main():
    if "access_token" not in st.session_state:
        render_login()
    else:
        render_chat()

if __name__ == "__main__":
    main()

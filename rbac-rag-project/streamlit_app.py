import streamlit as st
import base64
import requests
from jose import jwt

from rbac_search import semantic_search, build_rag_context
from llm_service import build_system_prompt, build_user_prompt, query_llm

# -------------------------------------------------
# JWT CONFIG (MUST MATCH BACKEND)
# -------------------------------------------------
SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"
AUTH_API = "http://127.0.0.1:8000/login"

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Secure Company AI Assistant",
    page_icon="🤖",
    layout="wide"
)

# -------------------------------------------------
# LOAD ROBOT IMAGE
# -------------------------------------------------
def load_image(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return ""

ROBOT_IMG = load_image("assets/robot.png")

# -------------------------------------------------
# CSS
# -------------------------------------------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0f172a, #1e293b);
    color: #e2e8f0;
}
header, footer {visibility: hidden;}

.main-wrapper {
    height: 100vh;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 6%;
}

.robot-img {
    width: 420px;
    animation: float 7s ease-in-out infinite;
}

@keyframes float {
    0%,100% {transform: translateY(0);}
    50% {transform: translateY(-25px);}
}

.login-card {
    background: rgba(30,41,59,0.95);
    border-radius: 24px;
    padding: 50px;
    width: 460px;
    border: 1px solid rgba(96,165,250,0.3);
}

.title {
    color: #60a5fa;
    font-size: 3rem;
    font-weight: 900;
    text-align: center;
}

.stButton>button {
    background: linear-gradient(90deg,#3b82f6,#60a5fa);
    color: white;
    font-weight: bold;
    padding: 14px;
    border-radius: 12px;
    width: 100%;
}
            /* ===============================
   FORCE CHAT TEXT COLOR (WHITE)
   =============================== */

/* Chat message text */
.stChatMessage p,
.stChatMessage span,
.stChatMessage div {
    color: #ffffff !important;
}

/* User message bubble */
[data-testid="stChatMessageUser"] {
    color: #ffffff !important;
}

/* Assistant message bubble */
[data-testid="stChatMessageAssistant"] {
    color: #ffffff !important;
}

/* Input placeholder text */
textarea::placeholder {
    color: #cbd5e1 !important;
}

/* Captions & small text */
.stCaption, .stMarkdown {
    color: #e5e7eb !important;
}
/* ===============================
   FIX INPUT LABEL VISIBILITY
   =============================== */

/* Text input & password labels */
label, 
label span,
div[data-testid="stTextInput"] label,
div[data-testid="stTextInput"] span,
div[data-testid="stPassword"] label,
div[data-testid="stPassword"] span {
    color: #e5e7eb !important;
    font-size: 16px !important;
    font-weight: 600 !important;
}

/* Optional: input text color */
input {
    color: #020617 !important;
    font-size: 16px !important;
}

</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# SESSION STATE
# -------------------------------------------------
for key, default in {
    "logged_in": False,
    "username": None,
    "role": None,
    "token": None,
    "messages": []
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# -------------------------------------------------
# LOGOUT
# -------------------------------------------------
if st.session_state.logged_in:
    col1, col2 = st.columns([9,1])
    with col2:
        if st.button("Logout"):
            st.session_state.clear()
            st.rerun()

# -------------------------------------------------
# LOGIN (JWT AUTH)
# -------------------------------------------------
if not st.session_state.logged_in:
    st.markdown('<div class="main-wrapper">', unsafe_allow_html=True)

    st.markdown(
        f"<img src='data:image/png;base64,{ROBOT_IMG}' class='robot-img'>",
        unsafe_allow_html=True
    )

    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.markdown('<div class="title">RBAC AI Chatbot</div>', unsafe_allow_html=True)
    st.caption("🔐 JWT-Secured Enterprise Access")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login Securely"):
        try:
            res = requests.post(
                AUTH_API,
                json={"username": username, "password": password},
                timeout=5
            )

            if res.status_code != 200:
                st.error("Invalid username or password")
            else:
                token = res.json()["access_token"]
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

                st.session_state.logged_in = True
                st.session_state.username = payload["sub"]
                st.session_state.role = payload["role"]
                st.session_state.token = token
                st.session_state.messages = [
                    ("assistant",
                     f"Welcome **{payload['sub']}** 👋  \nRole: **{payload['role']}**")
                ]
                st.rerun()

        except Exception:
            st.error("Authentication server not reachable")

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# -------------------------------------------------
# CHAT UI
# -------------------------------------------------
st.markdown(f"## Hello, **{st.session_state.username}**")
st.caption(f"🔐 Role: `{st.session_state.role}` | JWT Authenticated")

for role, msg in st.session_state.messages:
    st.chat_message(role).markdown(msg)

if prompt := st.chat_input("Ask a role-authorized question..."):
    st.session_state.messages.append(("user", prompt))
    st.chat_message("user").markdown(prompt)

    with st.spinner("🔍 Enforcing RBAC & generating answer..."):
        chunks = semantic_search(prompt, st.session_state.role, k=3)

        if not chunks:
            answer = "❌ No information available for your role."
        else:
            ctx, _ = build_rag_context(chunks)
            system = build_system_prompt(st.session_state.role)
            user_prompt = build_user_prompt("\n\n".join(ctx), prompt)
            answer = query_llm(user_prompt, system)

    st.session_state.messages.append(("assistant", answer))
    st.rerun()

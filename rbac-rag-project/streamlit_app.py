import streamlit as st
import base64
from pathlib import Path
import random
from rbac_search import semantic_search, build_rag_context
from llm_service import build_system_prompt, build_user_prompt, query_llm

# ────────────────────────────────────────────────
# PAGE CONFIG
# ────────────────────────────────────────────────
st.set_page_config(
    page_title="Secure Company AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ────────────────────────────────────────────────
# LOAD ROBOT IMAGE AS BASE64
# ────────────────────────────────────────────────
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

ROBOT_PATH = "assets/robot.png"  # or "assets/robot.png"
try:
    ROBOT_BASE64 = get_base64_of_bin_file(ROBOT_PATH)
except FileNotFoundError:
    ROBOT_BASE64 = ""
    st.warning("robot.png not found! Place it in the same folder.")

# ────────────────────────────────────────────────
# CSS - BOLD SKY BLUE TEXT (No Glow)
# ────────────────────────────────────────────────
st.markdown(f"""
<style>
    .stApp {{
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
        background-attachment: fixed;
        color: #e2e8f0;
    }}

    header, footer {{ visibility: hidden; height: 0px !important; }}

    /* Main wrapper */
    .main-wrapper {{
        height: 100vh;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 5%;
    }}

    /* Robot section */
    .robot-section {{
        position: relative;
        flex: 1;
        text-align: center;
        max-width: 50%;
    }}

    .robot-img {{
        width: 420px;
        height: auto;
        animation: float 7s ease-in-out infinite;
    }}

    .glow-circle {{
        position: absolute;
        border-radius: 50%;
        background: rgba(96, 165, 250, 0.12);
        border: 1px solid rgba(96, 165, 250, 0.3);
        z-index: -1;
    }}
    .circle1 {{ width: 500px; height: 500px; top: -25%; left: 0%; }}
    .circle2 {{ width: 380px; height: 380px; bottom: -15%; right: 5%; }}

    @keyframes float {{
        0%, 100% {{ transform: translateY(0px) rotate(0deg); }}
        50% {{ transform: translateY(-30px) rotate(3deg); }}
    }}

    /* Speech bubble */
    .speech-bubble {{
        position: absolute;
        background: #3b82f6;
        color: white;
        padding: 16px 24px;
        border-radius: 24px;
        border-bottom-left-radius: 4px;
        font-size: 1.15rem;
        font-weight: 500;
        max-width: 340px;
        bottom: 15%;
        left: 55%;
    }}

    /* Login card */
    .login-card {{
        background: rgba(30, 41, 59, 0.88);
        backdrop-filter: blur(18px);
        border: 1px solid rgba(96, 165, 250, 0.3);
        border-radius: 24px;
        padding: 50px 45px;
        width: 440px;
        box-shadow: 0 25px 70px rgba(0,0,0,0.6);
    }}

    /* Bold sky blue for Hello and Welcome */
    .sky-blue-bold {{
        color: #60a5fa !important;
        font-weight: 900 !important;
        text-align: center;
    }}

    .welcome-title {{
        font-size: 3rem;
    }}

    .chat-title {{
        font-size: 3.2rem;
        margin: 2rem 0 1rem;
    }}

    /* Normal text remains readable */
    p, span, .stMarkdown, .stCaption {{
        color: #e2e8f0;
    }}

    /* Chat bubbles */
    .stChatMessage {{
        background: rgba(30, 41, 59, 0.7) !important;
        border-radius: 16px !important;
        padding: 16px !important;
        margin: 12px 0 !important;
        color: #e2e8f0 !important;
    }}

    /* Input & button */
    .stChatInput input {{
        background: rgba(51, 65, 85, 0.7) !important;
        color: #e2e8f0 !important;
        border: 1px solid rgba(96, 165, 250, 0.5) !important;
        border-radius: 12px !important;
    }}

    .stButton > button {{
        background: linear-gradient(90deg, #3b82f6, #60a5fa) !important;
        color: white !important;
        border-radius: 12px !important;
        padding: 16px !important;
        font-weight: bold !important;
        width: 100% !important;
    }}
</style>
""", unsafe_allow_html=True)

# ────────────────────────────────────────────────
# SESSION STATE
# ────────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "role" not in st.session_state:
    st.session_state.role = ""
if "messages" not in st.session_state:
    st.session_state.messages = []

# ────────────────────────────────────────────────
# LOGOUT BUTTON - RED COLOR - Top right after login
# ────────────────────────────────────────────────
if st.session_state.logged_in:
    col1, col2 = st.columns([9, 1])  # Makes it right-aligned
    with col2:
        if st.button("Logout", key="logout_btn", type="primary"):
            st.session_state.clear()
            st.rerun()

# ────────────────────────────────────────────────
# LOGIN SCREEN
# ────────────────────────────────────────────────
if not st.session_state.logged_in:
    st.markdown('<div class="main-wrapper">', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="robot-section">
        <div class="glow-circle circle1"></div>
        <div class="glow-circle circle2"></div>
        <img src="data:image/png;base64,{ROBOT_BASE64}" class="robot-img" alt="Cute Blue Robot">
        <div class="speech-bubble">
            Hello! I'm your secure assistant<br>
            <strong>Can you tell me who you are?</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.markdown('<div class="sky-blue-bold welcome-title">Welcome!</div>', unsafe_allow_html=True)
    st.markdown('<div class="welcome-subtitle">Sign in to access company knowledge</div>', unsafe_allow_html=True)

    username = st.text_input("Your Name", placeholder="Enter your name")
    role = st.selectbox("Your Role", [
        "Admin", "C-Level", "Finance", "HR", "Engineering", "Employee"
    ])

    if st.button("Continue →"):
        if username.strip():
            st.session_state.logged_in = True
            st.session_state.username = username.strip()
            st.session_state.role = role
            st.session_state.messages.append(("assistant", f"Hi {username}! I'm ready to help with {role}-related questions. What would you like to know? 🤖"))
            st.rerun()
        else:
            st.error("Please enter your name")

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ────────────────────────────────────────────────
# CHAT INTERFACE
# ────────────────────────────────────────────────
st.markdown(f'<h1 class="sky-blue-bold chat-title">Hello, {st.session_state.username}!</h1>', unsafe_allow_html=True)
st.caption(f"Role: {st.session_state.role} • Secure Access Only")

for role, content in st.session_state.messages:
    if role == "user":
        st.chat_message("user").markdown(content)
    else:
        st.chat_message("assistant").markdown(content)

if prompt := st.chat_input("Ask your question..."):
    st.session_state.messages.append(("user", prompt))
    st.chat_message("user").markdown(prompt)

    with st.spinner("Thinking..."):
        chunks = semantic_search(prompt, st.session_state.role, k=4)

        if not chunks:
            response = "I'm sorry, I don't have information available for your role about this topic."
        else:
            context_parts, sources = build_rag_context(chunks)
            context = "\n\n".join(context_parts)
            system = build_system_prompt(st.session_state.role)
            user_prompt = build_user_prompt(context=context, query=prompt)
            response = query_llm(user_prompt, system)

    st.session_state.messages.append(("assistant", response))
    st.rerun()
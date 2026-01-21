import streamlit as st
import requests
from jose import jwt
import base64

st.set_page_config(
    page_title="Oracle | Knowledge Base",
    layout="wide"
)

BACKEND_URL = "http://127.0.0.1:8000"
LOGIN_ENDPOINT = f"{BACKEND_URL}/login"
CHAT_ENDPOINT = f"{BACKEND_URL}/chat"


def apply_custom_css():
    st.markdown("""
    <style>
        /* Main background */
        .stApp {
            background: radial-gradient(circle at top right, #1e1b4b, #0f172a, #020617);
            color: #e2e8f0;
        }

        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background-color: rgba(15, 23, 42, 0.8);
            border-right: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
        }

        /* Input boxes */
        .stTextInput input {
            background-color: rgba(255, 255, 255, 0.05) !important;
            color: white !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 10px !important;
        }

        /* Login Card */
        div[data-testid="stForm"] {
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            background-color: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(15px);
            padding: 30px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.8);
        }

        /* Buttons */
        .stButton>button {
            background: linear-gradient(45deg, #4338ca, #6d28d9) !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            transition: all 0.3s ease !important;
            font-weight: bold !important;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .stButton>button:hover {
            box-shadow: 0 0 15px rgba(109, 40, 217, 0.6) !important;
            transform: translateY(-2px);
        }

        /* Chat Messages */
        [data-testid="stChatMessage"] {
            background-color: rgba(255, 255, 255, 0.03) !important;
            border: 1px solid rgba(255, 255, 255, 0.05) !important;
            border-radius: 15px !important;
            margin-bottom: 10px;
        }

        /* Expander styling */
        .streamlit-expanderHeader {
            background-color: transparent !important;
            border: none !important;
            color: #94a3b8 !important;
        }

        /* Titles and headers */
        h1, h2, h3 {
            color: #f8fafc !important;
            font-family: 'Inter', sans-serif;
            font-weight: 700;
        }
        
        .stMarkdown p {
            font-size: 1.05rem;
            line-height: 1.6;
        }
    </style>
    """, unsafe_allow_html=True)


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
    except Exception as e:
        st.error(f"❌ Connection Error. Is the backend at {BACKEND_URL} running?")

def logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

def get_response(query):
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    try:
        res = requests.post(CHAT_ENDPOINT, json={"query": query}, headers=headers)
        if res.status_code == 200:
            return res.json()
        elif res.status_code == 401:
            st.error("Session expired.")
            logout()
            return None
        else:
            return {"answer": f"Error {res.status_code}", "sources": [], "confidence": 0}
    except:
        return {"answer": "The Oracle is currently unreachable.", "sources": [], "confidence": 0}

def render_login():
    apply_custom_css()
    _, col2, _ = st.columns([1, 1.5, 1])
    with col2:
        st.write("## ") 
        st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@900&display=swap');
    
    .cyber-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 55px;
        text-align: center;
        background: linear-gradient(to bottom, #fff, #6366f1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 2px 2px 10px rgba(99, 102, 241, 0.5);
        letter-spacing: 15px;
        font-weight: 900;
    }
    </style>
    <h1 class="cyber-title">ORACLE</h1>
    """, unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #94a3b8;'>Internal Knowledge Repository</p>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("Identity")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login", use_container_width=True)
            
            if submitted:
                login(username, password)

def render_sidebar():
    with st.sidebar:
        st.markdown("<h2 style='letter-spacing: 2px;'>SYSTEM</h2>", unsafe_allow_html=True)
        st.markdown(f"""
            <div style='padding: 15px; border-radius: 10px; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1);'>
                <p style='margin:0; font-size: 0.8rem; color: #94a3b8;'>USER</p>
                <p style='margin:0; font-weight: bold;'>{st.session_state.username}</p>
                <p style='margin-top:10px; font-size: 0.8rem; color: #94a3b8;'>CLEARANCE</p>
                <p style='margin:0; font-weight: bold; color: #818cf8;'>{st.session_state.role}</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.write("---")
        if st.button("Terminate Session", use_container_width=True):
            logout()

def render_chat():
    apply_custom_css()
    st.title("Knowledge Oracle")
    st.markdown("<p style='color: #94a3b8;'>Consult the internal archives of HR, Finance, and Engineering.</p>", unsafe_allow_html=True)

    # Display chat messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("sources"):
                with st.expander("📝 Source Metadata"):
                    st.caption(f"Confidence: {msg['confidence']:.2f}")
                    for src in msg["sources"]:
                        st.markdown(f"**{src['title']}** - {src['section']}")

    # Chat Input
    if query := st.chat_input("Ask your question..."):
        st.session_state.messages.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(query)
            
        with st.chat_message("assistant"):
            with st.spinner("Decrypting archives..."):
                response = get_response(query)
                if response:
                    answer = response.get("answer")
                    sources = response.get("sources", [])
                    conf = response.get("confidence", 0.0)
                    
                    st.markdown(answer)
                    if sources:
                        with st.expander("📝 Source Metadata"):
                            st.caption(f"Confidence: {conf}")
                            for src in sources:
                                st.markdown(f"**{src['title']}** - {src['section']}")
                    
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources,
                        "confidence": conf
                    })

def main():
    if not st.session_state.authenticated:
        render_login()
    else:
        render_sidebar()
        render_chat()

if __name__ == "__main__":
    main()


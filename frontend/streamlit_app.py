import streamlit as st
import requests

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Corporate Knowledge Bot",
    page_icon="🏢",
    layout="centered"
)

# --- CUSTOM CSS STYLING ---
st.markdown("""
    <style>
    .main-title {
        font-size: 3rem;
        color: #2E86C1;
        text-align: center;
        font-weight: bold;
    }
    .subtitle {
        font-size: 1.2rem;
        color: #555;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-box {
        border: 1px solid #ddd;
        padding: 15px;
        border-radius: 10px;
        background-color: #f9f9f9;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# --- CONFIG ---
API_URL = "http://127.0.0.1:8000"

# --- SESSION STATE INITIALIZATION ---
if "token" not in st.session_state:
    st.session_state.token = None
if "role" not in st.session_state:
    st.session_state.role = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- SIDEBAR (User Profile) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=100)
    st.title("Corporate Portal")
    
    if st.session_state.token:
        st.success(f"👤 Logged in as: **{st.session_state.role}**")
        if st.button("Logout", type="secondary"):
            st.session_state.token = None
            st.session_state.role = None
            st.session_state.messages = []
            st.rerun()
    else:
        st.info("Please log in to access secure documents.")

# --- LOGIN SCREEN ---
if not st.session_state.token:
    st.markdown('<div class="main-title">🔐 Secure Login</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Internal Corporate Access Only</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Access Portal", type="primary")

            if submit:
                try:
                    response = requests.post(
                        f"{API_URL}/token",
                        data={"username": username, "password": password}
                    )
                    if response.status_code == 200:
                        data = response.json()
                        st.session_state.token = data["access_token"]
                        st.session_state.role = data["role"]
                        st.toast("Login Successful!", icon="✅")
                        st.rerun()
                    else:
                        st.error("❌ Invalid Credentials")
                except Exception as e:
                    st.error(f"Connection Error: {e}")

# --- CHAT SCREEN ---
else:
    st.markdown('<div class="main-title">🤖 Knowledge Assistant</div>', unsafe_allow_html=True)
    st.caption(f"🔒 Secure Mode | Role: {st.session_state.role} | Access: {st.session_state.role} & General")

    # Display Chat History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat Input
    if prompt := st.chat_input("Ask about policies, data, or general queries..."):
        # 1. User Message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 2. Assistant Response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                headers = {"Authorization": f"Bearer {st.session_state.token}"}
                payload = {"question": prompt}
                
                try:
                    res = requests.post(f"{API_URL}/chat", json=payload, headers=headers)
                    if res.status_code == 200:
                        data = res.json()
                        answer = data["answer"]
                        sources = data["sources"]
                        
                        # Format Sources nicely
                        source_text = ""
                        if sources:
                            unique_sources = list(set(sources))
                            source_text = f"\n\n**📚 Sources:** `{', '.join(unique_sources)}`"
                        
                        full_response = answer + source_text
                        st.markdown(full_response)
                        
                        # Save to history
                        st.session_state.messages.append({"role": "assistant", "content": full_response})
                    
                    elif res.status_code == 401:
                        st.error("Session expired. Please logout and login again.")
                    else:
                        st.error(f"Error: {res.text}")
                        
                except Exception as e:
                    st.error(f"Server Connection Failed: {e}")
import streamlit as st
from auth_ui import login_ui
from chat_ui import chat_ui


# -------------------------------
# Page Configuration
# -------------------------------
st.set_page_config(
    page_title="Company RAG Chatbot",
    page_icon="💬",
    layout="centered"
)


# -------------------------------
# Load Custom CSS FIRST
# -------------------------------
def load_css():
    with open("frontend/styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()


# -------------------------------
# Main App Logic
# -------------------------------
if "token" not in st.session_state:
    login_ui()
else:
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("Logout"):
            st.session_state.clear()
            st.rerun()

    chat_ui()


# -------------------------------
# Footer (ALWAYS AT THE BOTTOM)
# -------------------------------
st.markdown(
    "<div class='footer'>Internal Company RAG Chatbot · Secure RBAC Enabled</div>",
    unsafe_allow_html=True
)

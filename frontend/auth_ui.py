import streamlit as st
from api_client import login

def login_ui():
    st.subheader("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        response = login(username, password)
        if response:
            st.session_state.token = response["access_token"]
            st.session_state.role = response["role"]
            st.session_state.username = username
            st.success("Login successful")
            st.rerun()
        else:
            st.error("Invalid credentials")

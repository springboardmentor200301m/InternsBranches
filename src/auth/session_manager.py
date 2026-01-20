import streamlit as st

# -------------------------------------------
# Initialize session state
# -------------------------------------------
def init_session():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "user" not in st.session_state:
        st.session_state.user = None


# -------------------------------------------
# Login user
# -------------------------------------------
def login_user(user: dict):
    st.session_state.logged_in = True
    st.session_state.user = user


# -------------------------------------------
# Logout user
# -------------------------------------------
def logout_user():
    st.session_state.logged_in = False
    st.session_state.user = None


# -------------------------------------------
# Check login status
# -------------------------------------------
def is_logged_in() -> bool:
    return st.session_state.get("logged_in", False)


# -------------------------------------------
# Get current user
# -------------------------------------------
def get_current_user():
    return st.session_state.get("user")

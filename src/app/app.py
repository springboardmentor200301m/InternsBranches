import sys
import os

# --------------------------------------------------
# Ensure project root is in PYTHONPATH
# --------------------------------------------------
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(PROJECT_ROOT)

import streamlit as st

# --------------------------------------------------
# Backend imports (FINAL, ALIGNED)
# --------------------------------------------------
from src.auth.login_handler import authenticate_user
from src.auth.session_manager import (
    init_session,
    login_user,
    logout_user,
    is_logged_in,
    get_current_user,
)
from src.search.semantic_search_role import role_based_search
from src.rag.task3_create_rag_prompt import create_rag_prompt
from src.rag.task4_call_llm import call_llm
from src.rag.task5_validate_answer import validate_answer

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Internal Company Chatbot",
    page_icon="🤖",
    layout="centered",
)

# --------------------------------------------------
# INIT SESSION STATE
# --------------------------------------------------
init_session()

# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.title("Internal Company Chatbot")
st.caption("Secure • Role-Based • RAG-Powered")
st.divider()

# ==================================================
# LOGIN VIEW
# ==================================================
if not is_logged_in():

    st.subheader("Login")
    st.write("Please authenticate to continue")

    username = st.text_input(
        "Username",
        placeholder="Enter your username"
    )

    role = st.selectbox(
        "Select Role",
        [
            "Finance",
            "HR",
            "Marketing",
            "Engineering",
            "Employee",
            "C-Level",
        ]
    )

    if st.button("Login", use_container_width=True):
        user, error = authenticate_user(username, role)

        if error:
            st.error(error)
        else:
            login_user(user)
            st.success("Login successful")
            st.rerun()

# ==================================================
# CHAT VIEW (POST LOGIN)
# ==================================================
else:
    user = get_current_user()

    st.success(
        f"Logged in as **{user['username']}** ({user['role']})"
    )

    if st.button("Logout"):
        logout_user()
        st.rerun()

    st.divider()

    # -------------------------------
    # QUERY INPUT
    # -------------------------------
    query = st.text_input(
        "Ask a question",
        placeholder="Type your question here..."
    )

    if st.button("Submit", use_container_width=True):

        if not query.strip():
            st.warning("Please enter a question.")
        else:
            with st.spinner("Processing your query..."):

                # --------------------------------
                # 1️⃣ ROLE-BASED SEMANTIC SEARCH
                # --------------------------------
                chunks = role_based_search(
                    query=query,
                    role=user["role"],
                    top_k=5
                )

                if not chunks:
                    st.error(
                        "No accessible documents found for your role."
                    )
                else:
                    # --------------------------------
                    # 2️⃣ CREATE RAG PROMPT
                    # --------------------------------
                    prompt = create_rag_prompt(
                        query=query,
                        retrieved_chunks=chunks,
                        role=user["role"]
                    )

                    # --------------------------------
                    # 3️⃣ CALL LLM
                    # --------------------------------
                    raw_answer = call_llm(prompt)

                    # --------------------------------
                    # 4️⃣ VALIDATE ANSWER
                    # --------------------------------
                    final_answer = validate_answer(
                        answer=raw_answer,
                        role=user["role"]
                    )

                    # --------------------------------
                    # DISPLAY ANSWER
                    # --------------------------------
                    st.subheader("Answer")
                    st.write(final_answer)

                    # --------------------------------
                    # DISPLAY SOURCES
                    # --------------------------------
                    with st.expander("Sources"):
                        for i, chunk in enumerate(chunks, start=1):
                            st.markdown(
                                f"**Source {i}:** {chunk.get('source', 'Unknown')}"
                            )
                            st.write(
                                chunk.get("content", "")[:500]
                            )

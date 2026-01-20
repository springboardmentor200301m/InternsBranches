import streamlit as st
import re
from api_client import chat_query


# --------------------------------
# UI-only markdown cleanup
# --------------------------------
def clean_answer(text: str) -> str:
    if not text:
        return ""

    text = text.replace("\u2022", " ")    # bullet
    text = text.replace("\u2013", "-")    # en-dash
    text = text.replace("\u2014", "-")    # em-dash

    # Remove markdown headers
    text = re.sub(r"\s*#+\s*", " ", text)

    # Remove table separators / horizontal rules
    text = re.sub(r"(?:\s*[-]\s*){3,}", " ", text)

    # Remove markdown emphasis
    text = re.sub(r"\*\*", "", text)
    text = re.sub(r"\*", "", text)

    # Normalize pipes
    text = re.sub(r"\s*\|\s*", " | ", text)
    text = re.sub(r"\|\s*\|", "|", text)

    # Normalize whitespace
    text = re.sub(r"\n{2,}", "\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)

    return text.strip()


def chat_ui():
    st.subheader("💬 Internal Company Chatbot")

    # Role badge
    st.markdown(
        f"<span class='role-badge role-{st.session_state.role}'>"
        f"{st.session_state.role.upper()}</span>",
        unsafe_allow_html=True
    )

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Chat input
    with st.form(key="chat_form"):
        query = st.text_input("Ask a question")
        submitted = st.form_submit_button("Send")

    if submitted and query.strip():
        response = chat_query(st.session_state.token, query)

        if response and "answer" in response:
            st.session_state.chat_history.append({
                "question": query,
                "answer": response["answer"],
                "sources": response.get("sources", []),
                "confidence": response.get("confidence", 0.0)
            })
        else:
            st.warning("No information available for your role.")

    # Render chat
    for chat in st.session_state.chat_history:

        # User message
        st.markdown(
            f"<div class='chat-user'><b>You:</b> {chat['question']}</div>",
            unsafe_allow_html=True
        )

        # Clean + sentence-based bullet formatting
        cleaned_answer = clean_answer(chat["answer"])
        sentences = [
        s.strip()
        for s in cleaned_answer.split(".")
        if len(s.strip()) > 3
        ]

# 🔒 Remove duplicate sentences while preserving order
        seen = set()
        unique_sentences = []
        for s in sentences:
            key = s.lower()
            if key not in seen:
                seen.add(key)
                unique_sentences.append(s)

        formatted_answer = "<br>• ".join(unique_sentences)


        st.markdown(
            f"""
            <div class='chat-bot'>
                <b>Bot:</b><br>
                • {formatted_answer}
            </div>
            """,
            unsafe_allow_html=True
        )

        # Deduplicated sources
        st.markdown("<div class='section-title'>Sources</div>", unsafe_allow_html=True)
        for src in sorted(set(chat["sources"])):
            st.markdown(
                f"<div class='source-box'>{src}</div>",
                unsafe_allow_html=True
            )

        # Confidence
        confidence = chat["confidence"]
        label = "Low" if confidence < 0.4 else "Medium" if confidence < 0.7 else "High"

        st.markdown(
            f"<div class='confidence'>Confidence: {confidence} ({label})</div>",
            unsafe_allow_html=True
        )

        st.caption(
            "ℹ️ Answer generated strictly from authorized internal documents using role-based access control."
        )

        st.markdown("<hr>", unsafe_allow_html=True)

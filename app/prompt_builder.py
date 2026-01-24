from typing import List, Dict


def build_user_prompt( user_query: str,    retrieved_chunks: List[Dict],) -> str:
    """
    LLM sees ONLY filtered chunks.
    No role info, no hidden metadata.
    """

    if not retrieved_chunks:
        return (
            "The user asked:\n"
            f"{user_query}\n\n"
            "There is no accessible information available.\n"
            "Respond politely that access is restricted."
        )

    context_blocks = []

    for i, chunk in enumerate(retrieved_chunks, start=1):
        context_blocks.append(
            f"[Context {i}]\n{chunk['text']}"
        )

    context_text = "\n\n".join(context_blocks)

    prompt = f"""
            You are a helpful assistant.

            Answer the user's question strictly using the provided context.
            If the answer is not present, say you do not have access.

            Context:
            {context_text}

            User Question:
            {user_query}

            Answer:
            """.strip()

    return prompt

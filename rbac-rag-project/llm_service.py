from openai import OpenAI
import os
from dotenv import load_dotenv
from prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE

# -------------------------------------------------
# Load environment variables
# -------------------------------------------------
load_dotenv()

# -------------------------------------------------
# Initialize OpenRouter client
# -------------------------------------------------
client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    default_headers={
        "HTTP-Referer": "http://localhost:8501",
        "X-Title": "Company Internal RBAC Chatbot"
    }
)

# -------------------------------------------------
# Prompt Builders (SAFE)
# -------------------------------------------------

def build_system_prompt(user_role: str) -> str:
    """
    Build RBAC-aware system prompt
    """
    return SYSTEM_PROMPT.format(user_role=user_role)


def build_user_prompt(context: str, query: str) -> str:
    """
    Build RAG user prompt.
    NOTE: Sources and confidence are NOT passed to LLM.
    """
    return USER_PROMPT_TEMPLATE.format(
        context=context,
        query=query
    )

# -------------------------------------------------
# LLM Query Function (FAILURE-SAFE)
# -------------------------------------------------

def query_llm(prompt: str, system_prompt: str) -> str:
    """
    Send prompt to LLM via OpenRouter and return response.
    Handles API failure gracefully.
    """
    try:
        response = client.chat.completions.create(
            model="meta-llama/llama-3.1-8b-instruct",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            max_tokens=512,
            temperature=0.3,
            top_p=0.9,
            timeout=30
        )

        return response.choices[0].message.content.strip()

    except Exception:
        return (
            "The system is temporarily unable to generate a response. "
            "Please try again later."
        )

# -------------------------------------------------
# Test Block (SAFE)
# -------------------------------------------------

if __name__ == "__main__":
    print("🔹 Testing LLM Service with Dummy Context (SAFE MODE)...\n")

    dummy_context = """
    RBAC ensures users can access only authorized documents.
    Retrieval Augmented Generation combines document retrieval with LLM-based generation.
    """

    user_query = "How does RAG work in an RBAC-based system?"
    user_role = "Employee"

    system_prompt = build_system_prompt(user_role)

    user_prompt = build_user_prompt(
        context=dummy_context,
        query=user_query
    )

    answer = query_llm(
        prompt=user_prompt,
        system_prompt=system_prompt
    )

    print("✅ LLM Answer:\n")
    print(answer)

    print("\n⚠️ Sources and confidence are intentionally NOT passed to the LLM.")

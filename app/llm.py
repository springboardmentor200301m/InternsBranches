import os
from typing import Literal
from dotenv import load_dotenv
from groq import AsyncGroq

load_dotenv()

# ======================================================
# CONFIG
# ======================================================

LLMProvider = Literal["groq", "none"]
LLM_PROVIDER: LLMProvider = os.getenv("LLM_PROVIDER", "groq")

SYSTEM_PROMPT = """
You are an internal company assistant.

STRICT RULES:
- Answer ONLY using the provided context.
- Do NOT use prior knowledge.
- Do NOT guess or hallucinate.
""".strip()


# ======================================================
# LLM CLIENT (ONLY WHAT MATTERS)
# ======================================================

class LLMClient:
    """
    Minimal async LLM client.
    Responsible ONLY for:
    - Initializing LLM
    - Generating responses
    """

    def __init__(self, provider: LLMProvider | None = None):
        self.provider = provider or LLM_PROVIDER

        if self.provider == "groq":
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise RuntimeError("GROQ_API_KEY is not set")

            self.client = AsyncGroq(api_key=api_key)
            self.model = os.getenv(
                "GROQ_MODEL",
                "llama-3.1-8b-instant"
            )
            return

        if self.provider == "none":
            return

        raise ValueError(f"Unsupported LLM provider: {self.provider}")

    async def generate(self, prompt: str) -> str:
        if self.provider == "none":
            return "LLM disabled."

        response = await self.client.chat.completions.create(
            model=self.model,
            temperature=0.1,
            messages=[
                {"role": "system", "content": "You are a company assistant. Only answer using provided context. Never hallucinate."},
                {"role": "user", "content": prompt},
            ],
        )

        return response.choices[0].message.content

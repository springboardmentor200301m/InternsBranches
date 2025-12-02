# app/llm_client.py

import os
from typing import Literal

from groq import AsyncGroq
from openai import AsyncOpenAI


LLMProvider = Literal["groq", "openai", "none"]

# Default provider = "none" (safe mode)
LLM_PROVIDER: LLMProvider = os.getenv("LLM_PROVIDER", "none")


class LLMClient:
    """
    Unified async LLM client for Groq, OpenAI, and stub mode.
    The goal is to keep the rest of the RAG pipeline simple.
    """

    def __init__(self, provider: LLMProvider | None = None):
        self.provider: LLMProvider = provider or LLM_PROVIDER

        # ---------------------------
        # GROQ support
        # ---------------------------
        if self.provider == "groq":
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise RuntimeError("GROQ_API_KEY not set in environment.")

            self.client = AsyncGroq(api_key=api_key)
            self.model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
            return

        # ---------------------------
        # OpenAI support
        # ---------------------------
        if self.provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise RuntimeError("OPENAI_API_KEY not set in environment.")

            self.client = AsyncOpenAI(api_key=api_key)
            self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            return

        # ---------------------------
        # Stub mode ("none")
        # ---------------------------
        if self.provider == "none":
            self.client = None
            self.model = None
            return

        raise ValueError(f"Unsupported LLM provider: {self.provider}")

    # ===================================================================
    # Public method to generate text
    # ===================================================================
    async def generate(self, prompt: str) -> str:
        """
        Unified async generate call.
        """

        if self.provider == "none":
            return (
                "RAG pipeline is configured, but no LLM provider is set. "
                "Set LLM_PROVIDER=groq or LLM_PROVIDER=openai to enable answer generation."
            )

        if self.provider == "groq":
            return await self._generate_groq(prompt)

        if self.provider == "openai":
            return await self._generate_openai(prompt)

        raise RuntimeError(f"Unknown provider: {self.provider}")

    # ===================================================================
    # GROQ backend
    # ===================================================================
    async def _generate_groq(self, prompt: str) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            temperature=0.1,
            messages=[
                {"role": "system",
                 "content": "You are a company assistant. Only answer using provided context. Never hallucinate."},
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content

    # ===================================================================
    # OpenAI backend
    # ===================================================================
    async def _generate_openai(self, prompt: str) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            temperature=0.1,
            messages=[
                {"role": "system",
                 "content": "You are a company assistant. Only answer using provided context. Never hallucinate."},
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message["content"]

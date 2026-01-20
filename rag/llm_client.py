from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
import threading
import os

MODEL_PATH = "models/flan-t5-small"

_lock = threading.Lock()
_llm = None


def get_llm():
    global _llm

    if _llm is None:
        with _lock:
            if _llm is None:
                print("🧠 Loading local LLM from disk (offline mode)...")

                tokenizer = AutoTokenizer.from_pretrained(
                    MODEL_PATH,
                    local_files_only=True
                )

                model = AutoModelForSeq2SeqLM.from_pretrained(
                    MODEL_PATH,
                    local_files_only=True
                )

                _llm = pipeline(
                    "text2text-generation",
                    model=model,
                    tokenizer=tokenizer,
                    device=-1  # CPU
                )

    return _llm


def call_llm(prompt: str) -> str:
    llm = get_llm()

    output = llm(
        prompt,
        max_length=150,
        do_sample=False
    )

    return output[0]["generated_text"]

# src/llm/llm_client.py

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from src.llm.prompt_templates import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE

# Load model once
MODEL_NAME = "google/flan-t5-base"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)


def generate_answer(context: str, question: str) -> str:
    """
    Combines system + user prompt and sends to LLM
    """

    full_prompt = SYSTEM_PROMPT + USER_PROMPT_TEMPLATE.format(
        context=context,
        question=question
    )

    inputs = tokenizer(full_prompt, return_tensors="pt")

    outputs = model.generate(
        **inputs,
        max_new_tokens=200
    )

    response = tokenizer.decode(outputs[0], skip_special_tokens=True)

    return response

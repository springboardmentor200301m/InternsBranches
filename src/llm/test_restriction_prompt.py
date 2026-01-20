# src/llm/test_restriction_prompt.py

from src.llm.llm_client import generate_answer

# Unauthorized / missing context
restricted_context = "No relevant documents found."

question = "What is the HR manager's salary?"

print("\n--- Restriction Test Output ---")
print(generate_answer(restricted_context, question))

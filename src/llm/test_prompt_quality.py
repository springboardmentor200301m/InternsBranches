# src/llm/test_prompt_quality.py

from src.llm.llm_client import generate_answer

# Poor prompt (no context)
poor_context = ""
question = "What is the leave policy?"

print("\n--- Poor Prompt Output ---")
print(generate_answer(poor_context, question))


# Improved prompt (with context)
good_context = """
Employees are entitled to 24 annual leaves per year.
Unused leaves can be carried forward to the next year.
"""

print("\n--- Improved Prompt Output ---")
print(generate_answer(good_context, question))

"""
Answer Validation Module – Milestone 4
Author: Anshuka Vashishtha
"""

def validate_answer(answer: str, role: str):
    """
    Final validation layer for LLM responses.
    """

    if not answer:
        return "No answer could be generated."

    return answer.strip()

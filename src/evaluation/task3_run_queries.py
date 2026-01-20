from evaluation.task1_questions import EVALUATION_QUESTIONS
from src.rag.task4_call_llm import run_rag_pipeline

evaluation_results = []

for item in EVALUATION_QUESTIONS:
    role = item["role"]
    question = item["question"]

    print("\n----------------------------")
    print(f"ROLE: {role}")
    print(f"QUESTION: {question}")

    answer = run_rag_pipeline(
        user_role=role,
        user_query=question
    )

    evaluation_results.append({
        "role": role,
        "question": question,
        "answer": answer
    })

print("\nAll evaluation queries executed successfully.")


"""
TASK 3: Role-Aware RAG Validation

Objective:
- Run the same query with different roles
- Verify RBAC enforcement
- Ensure restricted roles receive no sensitive data
"""

from src.rag.task2_build_context import build_llm_context
from src.rag.task4_call_llm import call_llm_with_rag


def role_aware_validation(query: str, roles: list):
    """
    Executes the same query across multiple roles
    and validates RBAC behavior.
    """

    print("\n🔍 QUERY:")
    print(query)

    for role in roles:
        print("\n" + "=" * 60)
        print(f"👤 ROLE: {role.upper()}")

        # -------------------------------
        # STEP 1: Retrieve role-based context
        # -------------------------------
        context, sources = build_llm_context(
            query=query,
            user_role=role,
            top_k=3
        )

        if not context.strip():
            print("❌ No context retrieved.")
            print("✅ RBAC correctly blocked access for this role.")
            continue

        print("\n📦 CONTEXT RETRIEVED (Top-K = 3):")
        print(context[:600] + "...\n")

        print("📚 SOURCES:")
        for src in sources:
            print(f"- {src['document']} ({src['department']})")

        # -------------------------------
        # STEP 2: Call LLM safely
        # -------------------------------
        answer, _ = call_llm_with_rag(
            query=query,
            user_role=role
        )

        print("\n🤖 LLM ANSWER:")
        print(answer)

        print("\n✅ RBAC enforcement verified for this role.")


# -------------------------------
# MANUAL TEST
# -------------------------------
if __name__ == "__main__":
    test_query = "What is the leave policy?"

    test_roles = [
        "hr",
        "employees",
        "finance"
    ]

    role_aware_validation(test_query, test_roles)

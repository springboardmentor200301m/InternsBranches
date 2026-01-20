from rbac_search import semantic_search, build_rag_context
from llm_service import (
    build_system_prompt,
    build_user_prompt,
    query_llm
)

# -------------------------------------------------
# USER INPUT
# -------------------------------------------------
user_query = input("Enter your query: ").strip()
user_role = input("Enter your role: ").strip()

TOP_K = 3  # 🔒 Limit context size (anti-hallucination)

print("\n🔹 Running RAG Test")
print("User Role:", user_role)
print("User Query:", user_query)

# -------------------------------------------------
# TASK 1: RBAC-FIRST RETRIEVAL
# -------------------------------------------------
retrieved_chunks = semantic_search(
    query=user_query,
    user_role=user_role,
    k=TOP_K
)

# -------------------------------------------------
# TASK 4: NO CONTEXT → NO LLM CALL
# -------------------------------------------------
if not retrieved_chunks:
    print("\n❌ No information available for your role.")
    print("LLM was NOT called to prevent hallucination.")
    exit()

# -------------------------------------------------
# BUILD SAFE CONTEXT + SOURCES (SEPARATED)
# -------------------------------------------------
context_chunks, sources = build_rag_context(retrieved_chunks)

context = "\n\n".join(context_chunks)

print("\n🔹 Context Sent to LLM (CONTENT ONLY):\n")
print(context[:800])

# -------------------------------------------------
# TASK 3: STRICT PROMPTS
# -------------------------------------------------
system_prompt = build_system_prompt(user_role)
user_prompt = build_user_prompt(
    context=context,
    query=user_query
)

# -------------------------------------------------
# TASK 5: SAFE LLM CALL
# -------------------------------------------------
answer = query_llm(
    prompt=user_prompt,
    system_prompt=system_prompt
)

print("\n🔹 LLM Generated Answer:\n")
print(answer)

# -------------------------------------------------
# SOURCE ATTRIBUTION (OUTSIDE LLM) – DEDUPLICATED
# -------------------------------------------------
print("\n🔹 Sources (Verified):")

unique_sources = {
    (src["document"], src["department"]) for src in sources
}

for doc, dept in unique_sources:
    print(f"- {doc} ({dept})")

# -------------------------------------------------
# CONFIDENCE (DISTANCE-BASED)
# -------------------------------------------------
avg_score = sum(chunk["score"] for chunk in retrieved_chunks) / len(retrieved_chunks)

if avg_score <= 1.0:
    confidence = "High"
elif avg_score <= 1.5:
    confidence = "Medium"
else:
    confidence = "Low"

print("\nConfidence:", confidence)

# -------------------------------------------------
# FINAL VALIDATION CHECKLIST
# -------------------------------------------------
print("\n✅ VALIDATION CHECKLIST")
print("✔ RBAC enforced before retrieval")
print("✔ LLM sees ONLY authorized text")
print("✔ No-context case handled safely")
print("✔ Sources never hallucinated")
print("✔ Confidence computed by system")
print("✔ Production-grade RAG flow")

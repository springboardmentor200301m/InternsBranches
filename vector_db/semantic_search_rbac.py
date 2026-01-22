'''from typing import List, Tuple

# -----------------------------
# ROLE MATCHING (FIXED)
# -----------------------------
def role_matches(doc_role: str, user_role: str) -> bool:
    doc_role = doc_role.lower().strip()
    user_role = user_role.lower().strip()

    # General docs allowed for everyone
    if doc_role == "general":
        return True

    return doc_role == user_role


# -----------------------------
# MOCK VECTOR SEARCH (REPLACE WITH CHROMA)
# -----------------------------
def semantic_search_rbac(
    query: str,
    user_role: str,
    top_k: int = 3
) -> Tuple[List[str], List[dict], List[float]]:

    # 🔹 Simulated vector DB results
    docs = [
        "2024 revenue increased by 18% compared to 2023.",
        "Employee leave policy updated in 2024.",
        "Quarterly profit margin improved due to cost reduction."
    ]

    metadatas = [
        {"role": "Finance", "document": "financial_summary.md", "department": "Finance"},
        {"role": "HR", "document": "employee_handbook.md", "department": "HR"},
        {"role": "Finance", "document": "quarterly_report.md", "department": "Finance"}
    ]

    distances = [0.12, 0.78, 0.20]

    filtered_docs = []
    filtered_sources = []
    filtered_distances = []

    for doc, meta, dist in zip(docs, metadatas, distances):
        if role_matches(meta["role"], user_role):
            filtered_docs.append(doc)
            filtered_sources.append(meta)
            filtered_distances.append(dist)

    return filtered_docs, filtered_sources, filtered_distances
'''





'''import os
import logging
from typing import List, Dict, Tuple
from datetime import datetime

from vector_db.chroma_client import get_chroma_collection
from vector_db.roles import ROLE_HIERARCHY

# -----------------------------
# Logging
# -----------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -----------------------------
# Business Domains (Optional Heuristic)
# -----------------------------
BUSINESS_DOMAINS = {
    "Finance": ["revenue", "profit", "budget", "tax", "investment"],
    "HR": ["employee", "policy", "leave", "salary", "benefit"],
    "Engineering": ["engineering", "api", "system", "software", "code"],
    "Marketing": ["campaign", "marketing", "brand", "customer"],
}

# -----------------------------
# Query Analysis
# -----------------------------
def analyze_query(query: str) -> Dict:
    query = query.strip()
    if len(query) < 2:
        return {"is_valid": False, "error": "Query too short"}

    q = query.lower()
    non_business = ["movie", "recipe", "fitness", "weather"]

    if any(k in q for k in non_business):
        return {
            "is_valid": True,
            "category": "non_business",
            "message": "Outside company scope"
        }

    for domain, keywords in BUSINESS_DOMAINS.items():
        if any(k in q for k in keywords):
            return {
                "is_valid": True,
                "category": "business",
                "domain": domain
            }

    return {"is_valid": True, "category": "ambiguous"}

# -----------------------------
# Secure Semantic Search (RBAC at DB level)
# -----------------------------
def semantic_search_rbac(
    query: str,
    user_role: str,
    top_k: int = 5
) -> Tuple[List[str], List[dict], List[float], Dict]:

    analysis = analyze_query(query)
    if not analysis["is_valid"]:
        return [], [], [], {"query_analysis": analysis, "search_performed": False}

    if analysis.get("category") == "non_business":
        return [], [], [], {
            "query_analysis": analysis,
            "search_performed": False
        }

    allowed_roles = ROLE_HIERARCHY.get(user_role)
    if not allowed_roles:
        return [], [], [], {"error": f"Invalid role: {user_role}"}

    collection = get_chroma_collection()
    if collection.count() == 0:
        return [], [], [], {"error": "Vector DB is empty"}

    results = collection.query(
        query_texts=[query],
        n_results=top_k,
        where={
            "roles": {"$in": allowed_roles}
        },
        include=["documents", "metadatas", "distances"]
    )

    return (
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
        {
            "query_analysis": analysis,
            "search_performed": True,
            "authorized_roles": allowed_roles
        }
    )

# -----------------------------
# Answer Generation (Extractive RAG)
# -----------------------------
def generate_answer(
    query: str,
    docs: List[str],
    metas: List[dict],
    dists: List[float],
    query_analysis: Dict
) -> Dict:

    if not docs:
        return {
            "answer": "No authorized documents found for your role.",
            "confidence": 0.1,
            "sources": [],
            "retrieved_docs": 0,
            "response_type": "empty"
        }

    answer_parts = []
    sources = []

    for doc, meta, dist in zip(docs[:3], metas[:3], dists[:3]):
        content = doc.split("[CONTENT]")[-1].strip()
        snippet = " ".join(content.split(".")[:2]).strip()

        answer_parts.append(snippet + ".")

        sources.append({
            "document": os.path.basename(meta.get("source", "unknown")),
            "department": meta.get("department", "Unknown"),
            "relevance_score": round(max(0.0, min(1.0, 1 - dist)), 3)
        })

    avg_dist = sum(dists[:3]) / len(dists[:3])
    confidence = round(max(0.1, min(0.95, 1 - avg_dist)), 2)

    return {
        "answer": " ".join(answer_parts),
        "confidence": confidence,
        "sources": sources,
        "retrieved_docs": len(docs),
        "response_type": "success"
    }

# -----------------------------
# Main API Entry Point
# -----------------------------
def query_with_rbac(
    question: str,
    user_role: str,
    top_k: int = 3
) -> Dict:

    start = datetime.now()

    docs, metas, dists, meta = semantic_search_rbac(
        question,
        user_role,
        top_k
    )

    result = generate_answer(
        question,
        docs,
        metas,
        dists,
        meta.get("query_analysis", {})
    )

    result.update({
        "query": question,
        "role_checked": user_role,
        "processing_time_seconds": round(
            (datetime.now() - start).total_seconds(), 2
        )
    })

    return result'''







'''import os
from typing import List, Tuple
from vector_db.chroma_client import get_chroma_collection
from llm.hf_tg_runner import HuggingFaceTextGenRunner

llm_runner = HuggingFaceTextGenRunner()

# -----------------------------
# Role matching
# -----------------------------
def role_matches(doc_role: str, user_role: str) -> bool:
    doc_role = doc_role.lower()
    user_role = user_role.lower()

    if doc_role == "general":
        return True

    return doc_role == user_role


# -----------------------------
# Semantic Search with RBAC
# -----------------------------
def semantic_search_rbac(
    query: str,
    user_role: str,
    top_k: int = 5
) -> Tuple[List[str], List[dict], List[float]]:

    collection = get_chroma_collection()

    if collection.count() == 0:
        return [], [], []

    results = collection.query(
        query_texts=[query],
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )

    docs, metas, dists = [], [], []

    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    ):
        if role_matches(meta.get("role", "General"), user_role):
            docs.append(doc)
            metas.append(meta)
            dists.append(dist)

    return docs, metas, dists


# -----------------------------
# Answer Generation
# -----------------------------
def generate_answer(
    query: str,
    docs: List[str],
    metas: List[dict],
    dists: List[float],
    user_role: str
) -> dict:

    # 🔹 Case 1: Documents exist → deterministic
    if docs:
        answer_sentences = []
        sources = []

        for doc, meta in zip(docs[:3], metas[:3]):
            content = doc.split("[CONTENT]")[-1].strip()
            sentence = content.split(".")[0].strip()
            if sentence:
                answer_sentences.append(sentence + ".")

            sources.append({
                "document": os.path.basename(meta.get("source", "unknown")),
                "department": meta.get("role", "General")
            })

        avg_dist = sum(dists[:3]) / len(dists[:3])
        confidence = round(max(0.3, 1 - avg_dist), 2)

        return {
            "answer": " ".join(answer_sentences),
            "confidence": confidence,
            "sources": sources,
            "message": "Answer from internal documents"
        }

    # 🔹 Case 2: No docs → LLM fallback
    prompt = f"""
You are a company knowledge assistant.
Answer the following question clearly and concisely:

Question: {query}
"""

    llm_answer = llm_runner.generate(prompt)

    return {
        "answer": llm_answer,
        "confidence": 0.25,
        "sources": [],
        "message": "Generated by LLM (no internal documents matched)"
    }
'''


import os
import re
import logging
from typing import List, Dict, Tuple
from datetime import datetime

from vector_db.chroma_client import get_chroma_collection
from vector_db.roles import ROLE_HIERARCHY
from llm.hf_tg_runner import HuggingFaceTextGenRunner

# =========================================================
# INITIALIZATION
# =========================================================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RBAC-RAG")

llm_runner = HuggingFaceTextGenRunner()

STOPWORDS = {
    "the", "is", "are", "was", "were", "what", "when", "why", "how",
    "a", "an", "of", "to", "for", "and", "or", "in", "on", "with"
}

BUSINESS_DOMAINS = {
    "Finance": ["revenue", "profit", "budget", "tax", "investment"],
    "HR": ["employee", "policy", "leave", "salary", "benefit"],
    "Engineering": ["engineering", "api", "system", "software", "code"],
    "Marketing": ["campaign", "marketing", "brand", "customer"],
}

# =========================================================
# UTILITIES
# =========================================================
def tokenize(text: str) -> List[str]:
    tokens = re.findall(r"\b[a-zA-Z]+\b", text.lower())
    return [t for t in tokens if t not in STOPWORDS]


def role_matches(doc_role: str, user_role: str) -> bool:
    """
    RBAC-safe role matching.
    - General docs are accessible to all
    - Exact role match otherwise
    """
    if not doc_role:
        return False

    doc_role = doc_role.lower().strip()
    user_role = user_role.lower().strip()

    if doc_role == "general":
        return True

    return doc_role == user_role


# =========================================================
# QUERY ANALYSIS
# =========================================================
def analyze_query(query: str) -> Dict:
    query = query.strip()
    if len(query) < 3:
        return {"is_valid": False, "error": "Query too short"}

    q = query.lower()

    non_business = ["movie", "recipe", "fitness", "weather"]
    if any(k in q for k in non_business):
        return {
            "is_valid": True,
            "category": "non_business",
            "message": "Outside company scope"
        }

    for domain, keywords in BUSINESS_DOMAINS.items():
        if any(k in q for k in keywords):
            return {
                "is_valid": True,
                "category": "business",
                "domain": domain
            }

    return {"is_valid": True, "category": "ambiguous"}


# =========================================================
# SEMANTIC SEARCH WITH RBAC
# =========================================================
def semantic_search_rbac(
    query: str,
    user_role: str,
    top_k: int = 5
) -> Tuple[List[str], List[dict], List[float], Dict]:

    analysis = analyze_query(query)

    if not analysis["is_valid"]:
        return [], [], [], {"analysis": analysis, "search_performed": False}

    if analysis.get("category") == "non_business":
        return [], [], [], {"analysis": analysis, "search_performed": False}

    allowed_roles = ROLE_HIERARCHY.get(user_role)
    if not allowed_roles:
        return [], [], [], {"error": f"Invalid role: {user_role}"}

    collection = get_chroma_collection()
    if collection.count() == 0:
        return [], [], [], {"error": "Vector DB empty"}

    results = collection.query(
        query_texts=[query],
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )

    docs, metas, dists = [], [], []

    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    ):
        if role_matches(meta.get("role", "General"), user_role):
            docs.append(doc)
            metas.append(meta)
            dists.append(dist)

    return docs, metas, dists, {
        "analysis": analysis,
        "authorized_roles": allowed_roles,
        "search_performed": True
    }


# =========================================================
# ANSWER GENERATION
# =========================================================
def generate_answer(
    query: str,
    docs: List[str],
    metas: List[dict],
    dists: List[float],
    meta_info: Dict
) -> Dict:

    # 🔹 Case 1: Authorized documents found
    if docs:
        answer_parts = []
        sources = []

        for doc, meta, dist in zip(docs[:3], metas[:3], dists[:3]):
            content = doc.split("[CONTENT]")[-1].strip()
            snippet = " ".join(content.split(".")[:2]).strip()

            if snippet:
                answer_parts.append(snippet + ".")

            sources.append({
                "document": os.path.basename(meta.get("source", "unknown")),
                "department": meta.get("department", meta.get("role", "General")),
                "relevance_score": round(max(0.0, 1 - dist), 3)
            })

        avg_dist = sum(dists[:3]) / len(dists[:3])
        confidence = round(max(0.3, min(0.95, 1 - avg_dist)), 2)

        return {
            "answer": " ".join(answer_parts),
            "confidence": confidence,
            "sources": sources,
            "retrieved_docs": len(docs),
            "response_type": "retrieval"
        }

    # 🔹 Case 2: LLM fallback (non-prioritized)
    prompt = f"""
You are a corporate knowledge assistant.
The user asked a question, but no authorized internal documents were found.

Answer conservatively and clearly.

Question:
{query}
"""

    llm_answer = llm_runner.generate(prompt)

    return {
        "answer": llm_answer,
        "confidence": 0.25,
        "sources": [],
        "retrieved_docs": 0,
        "response_type": "llm_fallback"
    }


# =========================================================
# MAIN ENTRY POINT
# =========================================================
def query_with_rbac(
    question: str,
    user_role: str,
    top_k: int = 3
) -> Dict:

    start = datetime.now()

    docs, metas, dists, meta = semantic_search_rbac(
        question,
        user_role,
        top_k
    )

    result = generate_answer(
        question,
        docs,
        metas,
        dists,
        meta
    )

    result.update({
        "query": question,
        "role_checked": user_role,
        "processing_time_seconds": round(
            (datetime.now() - start).total_seconds(), 2
        )
    })

    return result

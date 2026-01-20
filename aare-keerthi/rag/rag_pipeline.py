from fastapi import APIRouter, Depends
from pydantic import BaseModel
from auth.dependencies import get_current_user
from search.semantic_search import semantic_search
from rag.prompts import SYSTEM_PROMPT, user_prompt
from rag.context_builder import build_context
from rag.llm_client import call_llm
import re

router = APIRouter()


class QueryRequest(BaseModel):
    query: str


def clean_answer(text: str) -> str:
    text = re.sub(r"\*\*", "", text)
    text = re.sub(r"\*", "", text)
    text = re.sub(r"-{3,}", "", text)
    text = re.sub(r"\n{2,}", "\n", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()


@router.post("/query")
def rag_query(req: QueryRequest, user: dict = Depends(get_current_user)):
    query = req.query.strip()
    user_role = user.get("role")

    if not query:
        return {"message": "Query cannot be empty"}

    results = semantic_search(query, user_role)
    if not results:
        return {"message": "No information available for your role."}

    context, used_chunks = build_context(results)
    if not context:
        return {"message": "No information available for your role."}

    final_prompt = f"""
{SYSTEM_PROMPT}

Context:
{context}

{user_prompt(query)}
"""

    raw_answer = call_llm(final_prompt)
    answer = clean_answer(raw_answer)

    confidence = round(min(1.0, len(used_chunks) / 3), 2)

    return {
        "answer": answer,
        "sources": [c["source_file"] for c in used_chunks],
        "confidence": confidence
    }

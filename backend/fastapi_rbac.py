import json
import re
import torch
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
from sentence_transformers import util


EMBEDDING_MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"

LLM_MODEL_ID = "Qwen/Qwen2.5-1.5B-Instruct"

print(f"Loading Embedding Model: {EMBEDDING_MODEL_NAME}...")
embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)

print(f"Loading LLM: {LLM_MODEL_ID}...")
device = "cuda" if torch.cuda.is_available() else "cpu"

tokenizer = AutoTokenizer.from_pretrained(LLM_MODEL_ID)

llm_pipeline = pipeline(
    "text-generation",
    model=LLM_MODEL_ID,
    tokenizer=tokenizer,
    torch_dtype=torch.float16 if device == "cuda" else torch.float32,
    device_map="auto",
    max_new_tokens=500,
    trust_remote_code=True
)


client = chromadb.Client(Settings(persist_directory="./chroma_db"))
collection = client.get_or_create_collection(name="company_documents")

def clean_metadata(meta: dict):
    cleaned = {}
    for k, v in meta.items():
        if isinstance(v, list):
            cleaned[k] = ", ".join(map(str, v))
        elif v is None:
            continue
        else:
            cleaned[k] = v
    return cleaned

if collection.count() == 0:
    try:
        with open("chunks.json", "r", encoding="utf-8") as f:
            chunks = json.load(f)
        print(f"Indexing {len(chunks)} chunks...")
        batch_size = 64
        for i in tqdm(range(0, len(chunks), batch_size)):
            batch = chunks[i:i+batch_size]
            ids = [c["id"] for c in batch]
            docs = [c["text"] for c in batch]
            metas = [clean_metadata(c["meta"]) for c in batch]
            embeddings = embedding_model.encode(docs).tolist()
            collection.add(ids=ids, documents=docs, embeddings=embeddings, metadatas=metas)
        print("Indexing Complete.")
    except FileNotFoundError:
        print("Warning: chunks.json not found.")


ROLE_HIERARCHY = {
    "C-Level": ["engineering", "finance", "hr", "marketing", "general"],
    "HR": ["hr", "general"],
    "Finance": ["finance", "general"],
    "Engineering": ["engineering", "general"],
    "Marketing": ["marketing", "general"]
}

def normalize_query(query: str) -> str:
    return re.sub(r"[^a-z0-9\s]", "", query.lower()).strip()

def role_based_search(query, user_role, top_k=5):
    query_embedding = embedding_model.encode([normalize_query(query)]).tolist()
    if user_role not in ROLE_HIERARCHY:
        role_filter = {}
    else:
        role_filter = {"department": {"$in": ROLE_HIERARCHY[user_role]}}

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k,
        where=role_filter
    )
    return results

def format_prompt(query, context_texts):
    """
    Constructs a prompt using ChatML format (required for Qwen)
    """
    context_str = "\n\n---\n\n".join(context_texts)
    prompt = f"""<|im_start|>system
You are a helpful HR assistant. Answer the user's question using ONLY the context provided below.
If the answer is not in the context, strictly state: "I cannot find this information in the available documents."<|im_end|>
<|im_start|>user
CONTEXT:
{context_str}

QUESTION:
{query}<|im_end|>
<|im_start|>assistant
"""
    return prompt

def extract_answer(generated_text):
    if "<|im_start|>assistant" in generated_text:
        return generated_text.split("<|im_start|>assistant")[-1].replace("<|im_end|>", "").strip()
    return generated_text.strip()


def check_hallucination(answer, documents):
    answer_emb = embedding_model.encode(answer, convert_to_tensor=True)
    doc_embs = embedding_model.encode(documents, convert_to_tensor=True)
    scores = util.cos_sim(answer_emb, doc_embs)[0]
    top_score = torch.max(scores).item()
    return top_score

def rag_pipeline(query, user_role, top_k=4):
    results = role_based_search(query, user_role, top_k)
    
    if not results["documents"] or not results["documents"][0]:
        return {"answer": "No relevant documents found.", "sources": [], "confidence": 0, "is_hallucinated": False}

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    cleaned_docs = [re.sub(r'\s+', ' ', doc).strip() for doc in documents]
    
    prompt = format_prompt(query, cleaned_docs)
    
    response = llm_pipeline(
        prompt, 
        max_new_tokens=400, 
        do_sample=True, 
        temperature=0.1, 
        top_p=0.9,
        pad_token_id=tokenizer.eos_token_id 
    )
    
    raw_answer = response[0]["generated_text"]
    final_answer = extract_answer(raw_answer)

    grounding_score = check_hallucination(final_answer, cleaned_docs)
    is_hallucinated = grounding_score < 0.4
    
    if is_hallucinated:
        final_answer += "\n\n(⚠️ Warning: This answer may not be fully supported by sources.)"

    sources = []
    seen = set()
    for m in metadatas:
        identifier = f"{m.get('title')} - {m.get('section_heading')}"
        if identifier not in seen:
            sources.append({"title": m.get("title"), "section": m.get("section_heading"), "dept": m.get("department")})
            seen.add(identifier)

    return {
        "answer": final_answer,
        "sources": sources,
        "confidence": round(grounding_score, 2),
        "is_hallucinated": is_hallucinated
    }

from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta

app = FastAPI(title="Fast GPU RAG API")

SECRET_KEY = "supersecret"
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def create_token(data: dict):
    to_encode = data.copy()
    to_encode.update({"exp": datetime.utcnow() + timedelta(minutes=60)})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user_role(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("role")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

class LoginRequest(BaseModel):
    username: str
    password: str

class ChatRequest(BaseModel):
    query: str

@app.post("/login")
def login(data: LoginRequest):
    users = {
        "ceo": {"role": "C-Level", "pass": "ceo123"},
        "hr_user": {"role": "HR", "pass": "hr123"},
    }
    user = users.get(data.username)
    if not user or data.password != user["pass"]:
        raise HTTPException(400, "Invalid credentials")
    return {"access_token": create_token({"sub": data.username, "role": user["role"]})}

@app.post("/chat")
def chat_endpoint(request: ChatRequest, role: str = Depends(get_current_user_role)):
    return rag_pipeline(request.query, role)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


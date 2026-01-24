from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from app.db import Base, engine, SessionLocal, init_db, User
from app.auth import (
    get_password_hash,
    authenticate_user,
    create_access_token,
    get_current_user,
)
from app.semantic_search import semantic_search
from app.rag_pipeline import rag_answer

load_dotenv()

# ----------------------------- Lifespan / Startup -----------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(User).first() is None:
            seed_users = [
                ("alice_fin", "password123", "finance"),
                ("bob_mark", "password123", "marketing"),
                ("carol_hr", "password123", "hr"),
                ("dave_eng", "password123", "engineering"),
                ("erin_emp", "password123", "employee"),
                ("ceo", "password123", "c_level"),
            ]
            for username, password, role in seed_users:
                user = User(
                    username=username,
                    hashed_password=get_password_hash(password),
                    role=role,
                )
                db.add(user)
            db.commit()
    finally:
        db.close()
    yield

# ----------------------------- App -----------------------------
app = FastAPI(title="Company RBAC RAG Chatbot", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import time
@app.middleware("http")
async def add_process_time_header(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    print(f"Request: {request.url.path} | Time: {process_time:.4f}s")
    return response

# ----------------------------- Auth Endpoints -----------------------------
@app.post("/auth/register")
def register_user(user_in: dict, db: Session = Depends(init_db)):
    """
    user_in: {"username": str, "password": str, "role": str}
    """
    existing = db.query(User).filter(User.username == user_in["username"]).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")
    user = User(
        username=user_in["username"],
        hashed_password=get_password_hash(user_in["password"]),
        role=user_in["role"].lower(),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"username": user.username, "role": user.role}

@app.post("/auth/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(init_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/auth/me")
def read_users_me(current_user: User = Depends(get_current_user)):
    return {"username": current_user.username, "role": current_user.role}

# ----------------------------- Search Endpoint -----------------------------
@app.post("/search")
def search_endpoint(body: dict, current_user: User = Depends(get_current_user)):
    """
    body: {"query": str, "top_k": int}
    """
    top_k = body.get("top_k", 3)
    hits_raw = semantic_search(body.get("query", ""), user_role=current_user.role, top_k=top_k)
    hits = []
    for h in hits_raw:
        hits.append({
            "id": h["id"],
            "text": h["text"],
            "score": h["score"],
            "department": h["metadata"].get("department", ""),
            "source_file": h["metadata"].get("source_file", ""),
        })
    return {"hits": hits}

# ----------------------------- RAG Endpoint -----------------------------
@app.post("/rag")
async def rag_endpoint(body: dict, current_user: User = Depends(get_current_user)):
    """
    body: {"query": str, "top_k": int}
    """
    query = body.get("query", "").strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")
        
    top_k = body.get("top_k", 3)
    try:
        answer, sources = await rag_answer(
            query=query,
            user_role=current_user.role,
            top_k=top_k,
        )
        return {"answer": answer, "sources": sources}
    except Exception as e:
        print(f"RAG Error: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while processing your request.")

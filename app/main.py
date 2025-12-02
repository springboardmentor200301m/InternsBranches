# app/main.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
from fastapi.security import OAuth2PasswordRequestForm

from .db import get_db
from .auth import authenticate_user, create_access_token
from .schemas import Token

from .db import Base, engine, SessionLocal, get_db
from .models import User
from .auth import get_current_user, get_password_hash
from .schemas import (
    UserCreate,
    UserOut,
    Token,
    SearchRequest,
    SearchResponse,
    SearchHit,
    RagRequest,
    RagResponse,
)
from dotenv import load_dotenv
load_dotenv()

from .search import semantic_search
from .rag import generate_rag_answer
from contextlib import asynccontextmanager

from .auth import (
    get_password_hash,
    authenticate_user,
    create_access_token,
    get_current_user,
)
from .search import semantic_search

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup ---
    Base.metadata.create_all(bind=engine)

    # Seed DB if empty
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

    # Startup complete
    yield


app = FastAPI(
    title="Company RBAC RAG Chatbot",
    lifespan=lifespan
)


# CORS for Streamlit later
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/auth/register", response_model=UserOut)
def register_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
):
    # You might disable this in production and manage users separately
    existing = db.query(User).filter(User.username == user_in.username).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    user = User(
        username=user_in.username,
        hashed_password=get_password_hash(user_in.password),
        role=user_in.role.lower(),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@app.post("/auth/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    # OAuth2PasswordRequestForm gives you:
    # form_data.username, form_data.password, form_data.scopes (we don't use scopes here)
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
    )
    return Token(access_token=access_token)



@app.get("/auth/me", response_model=UserOut)
def read_users_me(
    current_user: User = Depends(get_current_user),
):
    return current_user


@app.post("/search", response_model=SearchResponse)
def search_endpoint(
    body: SearchRequest,
    current_user: User = Depends(get_current_user),
):
    hits_raw = semantic_search(body.query, user_role=current_user.role, top_k=body.top_k)

    hits = [
        SearchHit(
            id=h["id"],
            text=h["text"],
            score=h["score"],
            department=h["metadata"].get("department", ""),
            source_file=h["metadata"].get("source_file", ""),
        )
        for h in hits_raw
    ]

    return SearchResponse(hits=hits)



@app.post("/rag", response_model=RagResponse)
async def rag_endpoint(
    body: RagRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Full RAG answer:
    - Uses user's role to filter docs
    - Runs retrieval
    - Calls LLM
    - Returns answer + sources
    """
    answer, sources = await generate_rag_answer(
        query=body.query,
        user_role=current_user.role,
        top_k=body.top_k,
    )
    return RagResponse(answer=answer, sources=sources)

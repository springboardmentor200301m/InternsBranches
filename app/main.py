import os
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from dotenv import load_dotenv  

# --- LANGCHAIN COMMUNITY (Adapters) ---
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI

# --- LANGCHAIN CORE (New Logic) ---
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# --- LOCAL MODULES ---
from app.auth import Token, create_access_token, get_current_user, USERS_DB, UserData, verify_password

# Load environment variables
load_dotenv()

# --- CONFIGURATION ---
CHROMA_PATH = "chroma_db"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Initialize FastAPI
app = FastAPI(title="Internal Corporate Chatbot (RBAC)", version="1.0")

# --- DATABASE CONNECTION ---
embedding_function = SentenceTransformerEmbeddings(model_name=EMBEDDING_MODEL)
vector_db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

# --- LLM SETUP (GEMINI) ---
if not os.getenv("GOOGLE_API_KEY"):
    raise ValueError("GOOGLE_API_KEY not found in .env")


llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",  
    temperature=0.3
)
# --- DATA MODELS ---
class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str
    sources: List[str]

# --- HELPER: RBAC FILTER LOGIC ---
def get_role_filter(role: str):
    """
    Returns a ChromaDB 'where' filter based on the user's role.
    """
    if role == "C-Level":
        return None  # Access everything
    
    # Access own department OR 'General'
    return {
        "$or": [
            {"department": role},
            {"department": "General"}
        ]
    }

# --- API ENDPOINTS ---

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user_dict = USERS_DB.get(form_data.username)
    if not user_dict or not verify_password(form_data.password, user_dict["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={"sub": form_data.username, "role": user_dict["role"]}
    )
    return {"access_token": access_token, "token_type": "bearer", "role": user_dict["role"]}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, current_user: UserData = Depends(get_current_user)):
    print(f"User: {current_user.username} | Role: {current_user.role}")
    
    # Secure Retrieval
    rbac_filter = get_role_filter(current_user.role)
    results = vector_db.similarity_search(
        request.question,
        k=5,
        filter=rbac_filter
    )
    
    if not results:
        return {"answer": "I cannot find any information accessible to your role regarding this query.", "sources": []}

    # RAG Generation
    context_text = "\n\n".join([doc.page_content for doc in results])
    
    template = """You are a helpful internal corporate assistant. 
    Use the following pieces of retrieved context to answer the question. 
    If you don't know the answer, just say that you don't know. 
    
    Context:
    {context}
    
    Question: {question}
    
    Answer:"""
    
    prompt = PromptTemplate.from_template(template)
    chain = prompt | llm | StrOutputParser()
    
    answer = chain.invoke({"context": context_text, "question": request.question})
    
    # Extract Sources
    sources = list(set([doc.metadata.get("source", "Unknown") for doc in results]))
    
    return {"answer": answer, "sources": sources}

@app.get("/")
async def root():
    return {"message": "Chatbot API is running."}

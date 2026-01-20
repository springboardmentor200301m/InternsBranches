from fastapi import FastAPI
from auth.auth_routes import router as auth_router
from rag.rag_pipeline import router as rag_router

app = FastAPI(
    title="Company Internal RAG Chatbot",
    version="1.0.0"
)

@app.get("/")
def root():
    return {
        "message": "Company Internal RAG Chatbot API is running",
        "endpoints": {
            "login": "/auth/login",
            "chat": "/chat/query",
            "docs": "/docs"
        }
    }

app.include_router(auth_router, prefix="/auth")
app.include_router(rag_router, prefix="/chat")

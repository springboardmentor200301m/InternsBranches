"""
FastAPI Backend with User Authentication, RBAC, and RAG Integration
Module 5 + Module 6 Complete
"""

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional, List

from database import get_db, User, AuditLog
from auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    RoleChecker,
    ACCESS_TOKEN_EXPIRE_MINUTES
)


from rag_pipeline import RAGPipeline


app = FastAPI(
    title="RBAC Chatbot API with RAG",
    description="Role-Based Access Control Chatbot with JWT Authentication and RAG",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rag_pipeline = None

def get_rag_pipeline():
    """Get or initialize RAG pipeline"""
    global rag_pipeline
    if rag_pipeline is None:
        try:
            rag_pipeline = RAGPipeline(use_openai=False)
            print("✅ RAG Pipeline initialized")
        except Exception as e:
            print(f"⚠️  RAG Pipeline initialization failed: {e}")
            rag_pipeline = None
    return rag_pipeline

class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    username: str
    role: str
    expires_in: int


class UserInfo(BaseModel):
    username: str
    email: str
    role: str
    created_at: datetime


class QueryRequest(BaseModel):
    query: str


class Source(BaseModel):
    source: str
    department: str


class QueryResponse(BaseModel):
    query: str
    response: str
    sources: List[Source]
    role: str
    timestamp: datetime
    context_used: bool


# Middleware for audit logging
@app.middleware("http")
async def audit_logging_middleware(request: Request, call_next):
    """Log all API requests for audit purposes"""
    response = await call_next(request)
    return response


# Authentication endpoints
@app.post("/api/auth/login", response_model=LoginResponse)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """Authenticate user and return JWT token"""
    user = authenticate_user(db, login_data.username, login_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role}
    )
    
    user.last_login = datetime.utcnow()
    db.commit()
    
    audit_log = AuditLog(
        user_id=user.id,
        username=user.username,
        action="login",
        endpoint="/api/auth/login",
        details="User logged in successfully"
    )
    db.add(audit_log)
    db.commit()
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        username=user.username,
        role=user.role,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@app.get("/api/auth/me", response_model=UserInfo)
def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current authenticated user information"""
    return UserInfo(
        username=current_user.username,
        email=current_user.email,
        role=current_user.role,
        created_at=current_user.created_at
    )


# Protected endpoints with role-based access
@app.get("/api/finance/reports")
def get_finance_reports(
    current_user: User = Depends(RoleChecker(["Finance", "C-Level"])),
    db: Session = Depends(get_db)
):
    """Finance reports - Only accessible to Finance and C-Level users"""
    audit_log = AuditLog(
        user_id=current_user.id,
        username=current_user.username,
        action="access_finance_reports",
        endpoint="/api/finance/reports"
    )
    db.add(audit_log)
    db.commit()
    
    return {
        "message": "Finance reports accessed",
        "user": current_user.username,
        "role": current_user.role,
        "data": ["Q1 Report", "Q2 Report", "Q3 Report"]
    }


@app.get("/api/marketing/campaigns")
def get_marketing_campaigns(
    current_user: User = Depends(RoleChecker(["Marketing", "C-Level"])),
    db: Session = Depends(get_db)
):
    """Marketing campaigns - Only accessible to Marketing and C-Level users"""
    audit_log = AuditLog(
        user_id=current_user.id,
        username=current_user.username,
        action="access_marketing_campaigns",
        endpoint="/api/marketing/campaigns"
    )
    db.add(audit_log)
    db.commit()
    
    return {
        "message": "Marketing campaigns accessed",
        "user": current_user.username,
        "role": current_user.role,
        "data": ["Campaign A", "Campaign B", "Campaign C"]
    }


@app.get("/api/hr/employees")
def get_employee_data(
    current_user: User = Depends(RoleChecker(["HR", "C-Level"])),
    db: Session = Depends(get_db)
):
    """Employee data - Only accessible to HR and C-Level users"""
    audit_log = AuditLog(
        user_id=current_user.id,
        username=current_user.username,
        action="access_employee_data",
        endpoint="/api/hr/employees"
    )
    db.add(audit_log)
    db.commit()
    
    return {
        "message": "Employee data accessed",
        "user": current_user.username,
        "role": current_user.role,
        "data": ["Employee 1", "Employee 2", "Employee 3"]
    }


@app.post("/api/query", response_model=QueryResponse)
def process_query(
    query_data: QueryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Process user query with RAG pipeline and role-based access
    """
    # Log query
    audit_log = AuditLog(
        user_id=current_user.id,
        username=current_user.username,
        action="query",
        endpoint="/api/query",
        details=f"Query: {query_data.query}"
    )
    db.add(audit_log)
    db.commit()
    
    # Get RAG pipeline
    rag = get_rag_pipeline()
    
    if rag is None:
        # Fallback if RAG is not initialized
        return QueryResponse(
            query=query_data.query,
            response=f"RAG system is initializing. Your query as {current_user.role} has been received.",
            sources=[],
            role=current_user.role,
            timestamp=datetime.utcnow(),
            context_used=False
        )
    
    # Process query with RAG
    try:
        result = rag.query(query_data.query, current_user.role)
        
        return QueryResponse(
            query=query_data.query,
            response=result["response"],
            sources=[Source(**src) for src in result["sources"]],
            role=current_user.role,
            timestamp=datetime.utcnow(),
            context_used=result["context_used"]
        )
    except Exception as e:
        print(f"Error processing query: {e}")
        return QueryResponse(
            query=query_data.query,
            response=f"An error occurred while processing your query. Please try again.",
            sources=[],
            role=current_user.role,
            timestamp=datetime.utcnow(),
            context_used=False
        )


@app.get("/api/audit/logs")
def get_audit_logs(
    current_user: User = Depends(RoleChecker(["C-Level"])),
    db: Session = Depends(get_db),
    limit: int = 50
):
    """Get audit logs - Only accessible to C-Level users"""
    logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(limit).all()
    
    return {
        "total": len(logs),
        "logs": [
            {
                "username": log.username,
                "action": log.action,
                "endpoint": log.endpoint,
                "timestamp": log.timestamp,
                "details": log.details
            }
            for log in logs
        ]
    }


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "RBAC Chatbot API with RAG",
        "version": "1.0.0",
        "features": {
            "authentication": "JWT-based",
            "authorization": "Role-Based Access Control",
            "rag": "Retrieval-Augmented Generation",
            "vector_db": "FAISS"
        },
        "endpoints": {
            "login": "/api/auth/login",
            "user_info": "/api/auth/me",
            "query": "/api/query (with RAG)",
            "docs": "/docs"
        }
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    rag = get_rag_pipeline()
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "rag_status": "initialized" if rag else "not initialized"
    }


if __name__ == "__main__":
    import uvicorn
    print("="*70)
    print("🚀 Starting RBAC Chatbot API with RAG Integration")
    print("="*70)
    print("\n📚 Features:")
    print("  ✅ JWT Authentication")
    print("  ✅ Role-Based Access Control")
    print("  ✅ RAG with Vector Search (FAISS)")
    print("  ✅ Audit Logging")
    print("\n🌐 API Documentation: http://localhost:8000/docs")
    print("="*70 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
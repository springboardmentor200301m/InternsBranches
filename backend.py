from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import bcrypt
import os
from typing import Optional, List

app = FastAPI(title="RBAC RAG API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class LoginRequest(BaseModel):
    username: str
    password: str
    role: str

class QueryRequest(BaseModel):
    query: str
    role: str

class SourceInfo(BaseModel):
    document: str
    department: str
    role: str

class QueryResponse(BaseModel):
    answer: str
    confidence: float
    sources: List[SourceInfo]
    message: str

# ========== CONFIG ==========
USERS_FILE = "app/data/users.json"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        if hashed_password.startswith("$2"):
            return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())
        else:
            return plain_password == hashed_password
    except:
        return False

@app.post("/login")
def login(data: LoginRequest):
    try:
        with open(USERS_FILE, "r") as f:
            users = json.load(f)
        
        user_key = data.username.lower()
        if user_key not in users:
            return {"success": False, "error": "Invalid username or password"}
        
        user = users[user_key]
        
        if not verify_password(data.password, user["password"]):
            return {"success": False, "error": "Invalid username or password"}
        
        if user["role"].lower() != data.role.lower():
            return {
                "success": False, 
                "error": f"Wrong role. User is {user['role']}, not {data.role}"
            }
        
        return {
            "success": True,
            "username": user["username"],
            "role": user["role"],
            "message": f"Welcome {user['username']}!"
        }
    
    except FileNotFoundError:
        return {"success": False, "error": f"Users file not found at {USERS_FILE}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def build_context(docs):
    """Your context building function"""
    context_blocks = []
    total_chars = 0
    MAX_CONTEXT_CHARS = 1800

    for idx, doc in enumerate(docs, 1):
        cleaned_lines = []
        for line in doc.splitlines():
            line_strip = line.strip()
            if line_strip.startswith("[ROLE") or line_strip.startswith("[CONTEXT") or line_strip.startswith("[CONTENT]"):
                continue
            if line_strip.lower().startswith("## table of contents"):
                continue
            if line_strip.startswith("1. ["):
                continue
            cleaned_lines.append(line_strip)

        cleaned_text = "\n".join(cleaned_lines).strip()
        if not cleaned_text:
            continue

        block = f"[Document {idx}]\n{cleaned_text}"
        if total_chars + len(block) > MAX_CONTEXT_CHARS:
            break

        context_blocks.append(block)
        total_chars += len(block)

    if not context_blocks:
        context_blocks = [f"[Document {i+1}]\n{doc}" for i, doc in enumerate(docs)]

    return "\n\n--------------------\n\n".join(context_blocks)

def confidence_score(answer, context):
    """Your confidence scoring function"""
    if not answer:
        return 0.0

    answer_words = set(answer.lower().split())
    context_words = set(context.lower().split())

    overlap = answer_words & context_words

    if len(answer_words) < 3:
        return 0.0

    return round(len(overlap) / len(answer_words), 2)

@app.post("/ask", response_model=QueryResponse)
def ask_question(request: QueryRequest):
    try:
        # IMPORT YOUR ACTUAL MODULES HERE
        from vector_db.semantic_search_rbac import semantic_search_rbac
        from llm.hf_qa_runner import HuggingFaceQARunner
        
        print(f"\n🔍 Processing query: '{request.query}' for role: {request.role}")
        
        # Use your actual semantic search - IT RETURNS 4 VALUES!
        docs, sources, distances, _ = semantic_search_rbac(
            query=request.query,
            user_role=request.role,
            top_k=3
        )

        print(f"✅ Found {len(docs)} document chunks")
        print(f"✅ Found {len(sources)} sources")
        print(f"✅ Found {len(distances)} distances")
        
        if not docs:
            return QueryResponse(
                answer="No accessible information found for this role.",
                confidence=0.0,
                sources=[],
                message="No documents found"
            )
        
        # Build context
        context = build_context(docs)
        
        if not context.strip():
            return QueryResponse(
                answer="Could not extract information from documents.",
                confidence=0.0,
                sources=[],
                message="Empty context"
            )
        
        # Try deterministic extraction first
        filtered = [
            (d, m, dist)
            for d, m, dist in zip(docs, sources, distances)
            if dist < 0.55
        ]

        if filtered:
            print("✅ Using deterministic extraction")
            sentences = []
            filtered_sources = []

            for doc, meta, dist in filtered[:3]:
                clean = doc.split("[CONTENT]")[-1].strip() if "[CONTENT]" in doc else doc.strip()
                sentences.append(clean.split(".")[0] + ".")
                
                # Handle the metadata format from your semantic_search_rbac
                document_name = "Unknown"
                department = "General"
                role = "General"
                
                if meta and isinstance(meta, dict):
                    # Get filename from source
                    source_path = meta.get("source", "")
                    if source_path:
                        document_name = os.path.basename(source_path)
                    department = meta.get("department", meta.get("role", "General"))
                    role = meta.get("role", "General")
                elif meta and isinstance(meta, str):
                    document_name = meta
                
                filtered_sources.append(SourceInfo(
                    document=document_name,
                    department=department,
                    role=role
                ))

            confidence = round(1 - sum(d[2] for d in filtered) / len(filtered), 2)
            
            return QueryResponse(
                answer=" ".join(sentences),
                confidence=confidence,
                sources=filtered_sources,
                message="Success"
            )

        # LLM FALLBACK
        print("🤖 Using LLM fallback")
        llm = HuggingFaceQARunner()
        answer = llm.generate(request.query, context)
        
        if not answer or len(answer.strip()) < 5:
            return QueryResponse(
                answer="Information not available in the provided documents.",
                confidence=0.0,
                sources=[],
                message="LLM could not generate answer"
            )
        
        confidence = confidence_score(answer, context)
        
        # Prepare sources for LLM response
        llm_sources = []
        for meta in sources[:2]:
            document_name = "Unknown"
            department = "General"
            role = "General"
            
            if meta and isinstance(meta, dict):
                source_path = meta.get("source", "")
                if source_path:
                    document_name = os.path.basename(source_path)
                department = meta.get("department", meta.get("role", "General"))
                role = meta.get("role", "General")
            
            llm_sources.append(SourceInfo(
                document=document_name,
                department=department,
                role=role
            ))
        
        return QueryResponse(
            answer=answer,
            confidence=confidence,
            sources=llm_sources,
            message="Generated via LLM analysis"
        )
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return QueryResponse(
            answer="Error: Could not import RAG modules. Check your imports.",
            confidence=0.0,
            sources=[],
            message=f"Import error: {str(e)}"
        )
    except Exception as e:
        print(f"❌ Processing error: {e}")
        import traceback
        traceback.print_exc()  # This will show the full error trace
        return QueryResponse(
            answer=f"Error processing your query: {str(e)[:100]}",
            confidence=0.0,
            sources=[],
            message=f"Processing error: {str(e)[:100]}"
        )

@app.get("/demo-users")
def get_demo_users():
    try:
        with open(USERS_FILE, "r") as f:
            users = json.load(f)
        
        demo_list = []
        for user in users.values():
            demo_list.append({
                "username": user["username"],
                "role": user["role"],
                "password_hint": "Use simple passwords from terminal"
            })
        
        return {"demo_users": demo_list}
    except Exception as e:
        return {"demo_users": [], "error": str(e)}

@app.get("/health")
def health():
    return {"status": "ok", "users_file": USERS_FILE}

@app.get("/test-imports")
def test_imports():
    """Test if your modules can be imported"""
    try:
        from vector_db.semantic_search_rbac import semantic_search_rbac
        from llm.hf_qa_runner import HuggingFaceQARunner
        return {
            "success": True,
            "message": "All modules imported successfully",
            "vector_db": "✓ Loaded",
            "llm": "✓ Loaded"
        }
    except ImportError as e:
        return {
            "success": False,
            "message": f"Import error: {e}",
            "error": str(e)
        }

@app.get("/debug-search")
def debug_search(query: str = "test revenue", role: str = "Finance"):
    """Debug endpoint to see what semantic_search_rbac returns"""
    try:
        from vector_db.semantic_search_rbac import semantic_search_rbac
        
        docs, sources, distances, meta_info = semantic_search_rbac(
            query=query,
            user_role=role,
            top_k=2
        )
        
        return {
            "success": True,
            "query": query,
            "role": role,
            "docs_count": len(docs),
            "sources_count": len(sources),
            "distances_count": len(distances),
            "meta_info": meta_info,
            "first_doc_preview": docs[0][:200] if docs else None,
            "first_source": sources[0] if sources else None,
            "first_distance": distances[0] if distances else None,
            "source_types": [type(s).__name__ for s in sources[:3]] if sources else []
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "traceback": str(e.__traceback__)
        }

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 70)
    print("🔐 RBAC RAG API - DEBUG VERSION")
    print("=" * 70)
    print(f"📡 Server URL: http://localhost:8000")
    print(f"📚 API Docs: http://localhost:8000/docs")
    
    # Test imports
    try:
        from vector_db.semantic_search_rbac import semantic_search_rbac
        from llm.hf_qa_runner import HuggingFaceQARunner
        print("✅ Successfully imported your RAG modules")
        
        # Quick test
        print("\n📝 Quick test of semantic_search_rbac...")
        docs, sources, distances, meta = semantic_search_rbac(
            query="test revenue",
            user_role="Finance",
            top_k=1
        )
        print(f"   Returned: {len(docs)} docs, {len(sources)} sources, {len(distances)} distances")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure your modules are in the right location")
    
    # Check users
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r") as f:
                users = json.load(f)
            print(f"\n✅ Loaded {len(users)} users from {USERS_FILE}")
        except Exception as e:
            print(f"\n❌ Error loading users: {e}")
    else:
        print(f"\n⚠️  Users file not found: {USERS_FILE}")
    
    print("\n🔗 Test endpoints:")
    print("   • GET  /debug-search?query=revenue&role=Finance - Debug search")
    print("   • POST /ask       - Ask question")
    print("   • GET  /test-imports - Check if modules load")
    print("\n📝 Sample curl command:")
    print('   curl -X POST "http://localhost:8000/ask" \\')
    print('     -H "Content-Type: application/json" \\')
    print('     -d \'{"query": "What was the revenue increase", "role": "Finance"}\'')
    print("=" * 70)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
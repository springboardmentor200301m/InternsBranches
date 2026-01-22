"""
Module 6: RAG Pipeline using FAISS - Query Processing with Role-Based Access
FIXED VERSION with proper RBAC enforcement
"""

from sentence_transformers import SentenceTransformer
import faiss
import pickle
import numpy as np
from typing import List, Dict
import os

# Import role mapping
ROLE_DOCUMENT_MAP = {
    "Finance": ["finance"],
    "Marketing": ["marketing"],
    "HR": ["hr"],
    "Engineering": ["engineering"],
    "Employees": ["general"],
    "C-Level": ["finance", "marketing", "hr", "engineering", "general"]
}

class RAGPipeline:
    def __init__(self, use_openai=False):
        """Initialize RAG pipeline with embedding model and FAISS index"""
        
        print("🔧 Initializing RAG Pipeline...")
        
        # Load embedding model
        self.embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        
        # Load FAISS index
        self.index = faiss.read_index("./vector_db/faiss_index.bin")
        
        # Load metadata
        with open("./vector_db/metadata.pkl", "rb") as f:
            data = pickle.load(f)
            self.chunks = data["chunks"]
            self.metadata = data["metadata"]
        
        print(f"✅ Loaded {len(self.chunks)} document chunks")
        
        # LLM setup
        self.use_openai = use_openai
        if use_openai:
            try:
                from openai import OpenAI
                self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                print("✅ OpenAI initialized")
            except:
                print("⚠️  OpenAI not available, using template responses")
                self.use_openai = False
        
        print("✅ RAG Pipeline ready\n")
    
    def check_access_permission(self, query: str, user_role: str) -> Dict:
        """
        Check if user is trying to access restricted information
        Returns access status and appropriate message
        """
        # Keywords that indicate department-specific queries
        dept_keywords = {
            "Finance": ["salary", "budget", "revenue", "financial", "q1", "q2", "q3", "q4", "finance"],
            "HR": ["employee", "hr", "hiring", "pto", "benefits", "policy", "human resources"],
            "Marketing": ["campaign", "marketing", "customer", "market share", "advertisement"],
            "Engineering": ["technical", "architecture", "deployment", "engineering", "system"]
        }
        
        query_lower = query.lower()
        
        # Check which department the query is about
        detected_dept = None
        for dept, keywords in dept_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                detected_dept = dept
                break
        
        if detected_dept:
            # Check if user has access to this department
            allowed_depts_for_role = ROLE_DOCUMENT_MAP.get(user_role, [])
            
            if detected_dept.lower() not in allowed_depts_for_role:
                allowed_list = "\n".join([f"✅ {dept.capitalize()}" for dept in allowed_depts_for_role])
                return {
                    "has_access": False,
                    "message": f"""⛔ **Access Denied**

Your **{user_role}** role does not have permission to access **{detected_dept}** department information.

**🔒 Your Accessible Departments:**
{allowed_list}

Please ask questions only about the departments you have access to."""
                }
        
        return {"has_access": True, "message": ""}
    
    def search_documents(self, query: str, user_role: str, top_k: int = 5) -> List[Dict]:
        """
        Search for relevant documents based on query and user role
        """
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query])
        query_embedding = np.array(query_embedding).astype('float32')
        
        # Search in FAISS index (get more results to filter by role)
        distances, indices = self.index.search(query_embedding, top_k * 3)
        
        # Filter by role permissions
        filtered_results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.metadata):
                meta = self.metadata[idx]
                
                # ✅ CRITICAL: Check if user role has access to this document
                if user_role in meta['accessible_roles']:
                    filtered_results.append({
                        'content': self.chunks[idx],
                        'source': meta['source'],
                        'department': meta['department'],
                        'distance': float(distances[0][i])
                    })
                    
                    if len(filtered_results) >= top_k:
                        break
        
        return filtered_results
    
    def generate_response(self, query: str, context_docs: List[Dict], user_role: str) -> Dict:
        """
        Generate response using retrieved context
        """
        if not context_docs:
            # Get allowed departments for better error message
            allowed_depts = ROLE_DOCUMENT_MAP.get(user_role, [])
            allowed_list = ", ".join([dept.capitalize() for dept in allowed_depts])
            
            return {
                "response": f"""⛔ **No Accessible Information Found**

I couldn't find any relevant information in the documents accessible to your **{user_role}** role.

**Your Access:** {allowed_list}

Please try asking about topics within your accessible departments.""",
                "sources": [],
                "context_used": False
            }
        
        # Prepare context
        context = "\n\n".join([
            f"[{doc['department'].upper()} - {doc['source']}]\n{doc['content']}"
            for doc in context_docs
        ])
        
        # Generate response
        if self.use_openai:
            response_text = self._generate_openai_response(query, context, user_role)
        else:
            response_text = self._generate_template_response(query, context_docs, user_role)
        
        # Prepare sources
        sources = [
            {
                "source": doc['source'],
                "department": doc['department']
            }
            for doc in context_docs
        ]
        
        return {
            "response": response_text,
            "sources": sources,
            "context_used": True,
            "num_sources": len(sources)
        }
    
    def _generate_openai_response(self, query: str, context: str, user_role: str) -> str:
        """Generate response using OpenAI"""
        try:
            system_prompt = f"""You are a helpful assistant for a company's internal chatbot system. 
The user has the role: {user_role}. 
Use the provided context to answer their question accurately and concisely.
If the context doesn't contain relevant information, say so clearly.
Always cite the sources you used.

IMPORTANT: Only provide information from the context given. If asked about departments 
the user doesn't have access to, inform them of the access restriction."""

            user_prompt = f"""Context from company documents:

{context}

Question: {query}

Please provide a clear and accurate answer based on the context above."""

            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            print(f"OpenAI error: {e}")
            return self._generate_template_response(query, [], user_role)
    
    def _generate_template_response(self, query: str, context_docs: List[Dict], user_role: str) -> str:
        """Generate template response when OpenAI is not available - WITH RBAC ENFORCEMENT"""
        
        if not context_docs:
            allowed_depts = ROLE_DOCUMENT_MAP.get(user_role, [])
            return f"""⛔ **Access Denied or No Information Found**

Your **{user_role}** role does not have permission to access information about this topic, 
or no relevant documents were found.

**Your Accessible Departments:** {', '.join([d.capitalize() for d in allowed_depts])}"""
        
        # Extract key information from accessible documents
        sources_info = ", ".join([f"{doc['source']} ({doc['department'].capitalize()})" for doc in context_docs[:3]])
        
        # Get snippet from first document
        snippet = context_docs[0]['content'][:400].strip()
        
        response = f"""✅ **Information from {user_role} Accessible Documents**

**Sources:** {sources_info}

**Answer:**
{snippet}...

---
📁 **Department:** {context_docs[0]['department'].upper()}
🔒 **Your Role:** {user_role}
📄 **Sources Used:** {len(context_docs)}

💡 *This information is from documents you have permission to access.*"""
        
        return response
    
    def query(self, query: str, user_role: str) -> Dict:
        """
        Main query method - combines search and generation with RBAC enforcement
        """
        # ✅ NEW: Check access permissions BEFORE searching
        access_check = self.check_access_permission(query, user_role)
        
        if not access_check["has_access"]:
            return {
                "response": access_check["message"],
                "sources": [],
                "context_used": False,
                "num_sources": 0
            }
        
        # Step 1: Search for relevant documents (role-filtered)
        relevant_docs = self.search_documents(query, user_role)
        
        # Step 2: Generate response
        result = self.generate_response(query, relevant_docs, user_role)
        
        return result


def test_rag_pipeline():
    """Test the RAG pipeline with sample queries"""
    print("="*70)
    print("TESTING RAG PIPELINE WITH RBAC")
    print("="*70 + "\n")
    
    try:
        # Initialize pipeline
        rag = RAGPipeline(use_openai=False)
        
        # Test queries for different roles
        test_cases = [
            {
                "query": "What are the Q3 financial results?",
                "role": "Finance",
                "expected": "Should show finance data"
            },
            {
                "query": "What are the salary details for HR?",
                "role": "Finance",
                "expected": "Should DENY - Finance user asking about HR"
            },
            {
                "query": "What marketing campaigns are running?",
                "role": "Marketing",
                "expected": "Should show marketing data"
            },
            {
                "query": "What are the employee policies?",
                "role": "HR",
                "expected": "Should show HR data"
            },
            {
                "query": "What are the Q3 financial results?",
                "role": "Employees",
                "expected": "Should DENY - Employees don't have finance access"
            },
            {
                "query": "What are the HR salary details?",
                "role": "C-Level",
                "expected": "Should show - C-Level has all access"
            }
        ]
        
        for test in test_cases:
            print(f"\n{'='*70}")
            print(f"Query: {test['query']}")
            print(f"Role: {test['role']}")
            print(f"Expected: {test['expected']}")
            print("-"*70)
            
            result = rag.query(test['query'], test['role'])
            
            print(f"\nResponse: {result['response'][:400]}...")
            print(f"\n✅ Sources used: {len(result['sources'])}")
            for source in result['sources'][:3]:
                print(f"  - {source['source']} ({source['department']})")
        
        print(f"\n{'='*70}")
        print("✅ RAG PIPELINE RBAC TESTING COMPLETE")
        print("="*70)
        
    except FileNotFoundError:
        print("❌ Vector database not found!")
        print("Please run 'python generate_embeddings.py' first to create the vector database.")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_rag_pipeline()
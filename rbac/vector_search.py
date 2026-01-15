"""
Module 3 & 4: Vector Database Search with Role-Based Access Control
Implements semantic search with role-based filtering
"""

import json
from typing import List, Dict, Any
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
INDEX_DIR = "faiss_index"
CHUNKS_FILE = "document_chunks.json"

ROLE_HIERARCHY = {
    "C-Level": 5,
    "Finance": 4,
    "Marketing": 4,
    "HR": 4,
    "Engineering": 4,
    "Employees": 1
}


class RoleBasedVectorSearch:
    """Vector search with role-based access control"""
    
    def __init__(self, index_dir: str = INDEX_DIR, chunks_file: str = CHUNKS_FILE):
        """
        Initialize the vector search system
        
        Args:
            index_dir: Path to FAISS index directory
            chunks_file: Path to document chunks JSON file
        """
        print("🔧 Initializing Vector Search System...")
        
        # Load embeddings model
        print("📥 Loading embedding model...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        # Load FAISS index
        print("📂 Loading FAISS vector index...")
        self.vector_store = FAISS.load_local(
            index_dir, 
            self.embeddings,
            allow_dangerous_deserialization=True
        )
        
        # Load document chunks with metadata
        print("📄 Loading document chunks...")
        with open(chunks_file, 'r', encoding='utf-8') as f:
            self.chunks = json.load(f)
        
        print(f"✅ Loaded {len(self.chunks)} document chunks")
        print("✅ Vector Search System Ready!\n")
    
    def preprocess_query(self, query: str) -> str:
        """
        Preprocess and normalize user query
        
        Args:
            query: Raw user query
            
        Returns:
            Cleaned query
        """
        
        query = " ".join(query.split())
        
        query = query.lower()
        
        return query
    
    def check_role_access(self, user_role: str, chunk_roles: List[str]) -> bool:
        """
        Check if user role has access to chunk
        
        Args:
            user_role: User's role
            chunk_roles: List of roles that can access the chunk
            
        Returns:
            True if user has access, False otherwise
        """
        return user_role in chunk_roles
    
    def filter_by_role(self, chunks_with_scores: List[tuple], user_role: str) -> List[Dict]:
        """
        Filter search results by role-based access
        
        Args:
            chunks_with_scores: List of (chunk_index, score) tuples
            user_role: User's role
            
        Returns:
            Filtered list of accessible chunks with metadata
        """
        accessible_results = []
        
        for idx, score in chunks_with_scores:
            chunk = self.chunks[idx]
            
            # Check if user has access to this chunk
            if self.check_role_access(user_role, chunk.get('accessible_roles', [])):
                result = {
                    "content": chunk["chunk"],
                    "source": chunk["file_name"],
                    "chunk_id": chunk["chunk_id"],
                    "role": chunk["role"],
                    "accessible_roles": chunk["accessible_roles"],
                    "relevance_score": float(score),
                    "file_type": chunk.get("file_type", "unknown")
                }
                accessible_results.append(result)
        
        return accessible_results
    
    def search(
        self, 
        query: str, 
        user_role: str, 
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Perform role-based semantic search
        
        Args:
            query: Search query
            user_role: User's role for access control
            top_k: Number of top results to return
            
        Returns:
            List of relevant document chunks with metadata
        """
        # Validate user role
        if user_role not in ROLE_HIERARCHY:
            raise ValueError(f"Invalid role: {user_role}")
        
        # Preprocess query
        processed_query = self.preprocess_query(query)
        
        # Perform similarity search (get more results for filtering)
        search_results = self.vector_store.similarity_search_with_score(
            processed_query, 
            k=top_k * 3  # Get more results to account for role filtering
        )
        
        # Extract chunk indices and scores
        chunks_with_scores = []
        for doc, score in search_results:
            # Find matching chunk by content
            for idx, chunk in enumerate(self.chunks):
                if chunk["chunk"] == doc.page_content:
                    chunks_with_scores.append((idx, score))
                    break
        
        # Filter by role access
        accessible_results = self.filter_by_role(chunks_with_scores, user_role)
        
        # Return top_k results after filtering
        return accessible_results[:top_k]
    
    def get_search_statistics(self, results: List[Dict]) -> Dict[str, Any]:
        """
        Get statistics about search results
        
        Args:
            results: Search results
            
        Returns:
            Statistics dictionary
        """
        if not results:
            return {
                "total_results": 0,
                "sources": [],
                "departments": [],
                "avg_relevance": 0.0
            }
        
        sources = list(set(r["source"] for r in results))
        departments = list(set(r["role"] for r in results))
        avg_relevance = sum(r["relevance_score"] for r in results) / len(results)
        
        return {
            "total_results": len(results),
            "sources": sources,
            "departments": departments,
            "avg_relevance": avg_relevance
        }


def test_search_system():
    """Test the vector search system with sample queries"""
    
    print("="*70)
    print("MODULE 3 & 4: VECTOR SEARCH WITH ROLE-BASED ACCESS CONTROL")
    print("="*70)
    
    # Initialize search system
    search = RoleBasedVectorSearch()
    
    # Test queries for different roles
    test_cases = [
        {
            "query": "What is our quarterly revenue?",
            "role": "Finance",
            "description": "Finance user querying financial data"
        },
        {
            "query": "What is our quarterly revenue?",
            "role": "Marketing",
            "description": "Marketing user querying financial data (should have limited access)"
        },
        {
            "query": "Tell me about our marketing campaigns",
            "role": "Marketing",
            "description": "Marketing user querying marketing data"
        },
        {
            "query": "What are the employee benefits?",
            "role": "HR",
            "description": "HR user querying HR data"
        },
        {
            "query": "What are the employee benefits?",
            "role": "Employees",
            "description": "Employee querying HR data"
        },
        {
            "query": "technical architecture details",
            "role": "Engineering",
            "description": "Engineering user querying technical docs"
        },
        {
            "query": "company overview and policies",
            "role": "C-Level",
            "description": "C-Level accessing all documents"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*70}")
        print(f"TEST CASE {i}: {test['description']}")
        print(f"{'='*70}")
        print(f"Query: \"{test['query']}\"")
        print(f"User Role: {test['role']}")
        print(f"{'-'*70}")
        
        try:
            results = search.search(
                query=test['query'],
                user_role=test['role'],
                top_k=3
            )
            
            stats = search.get_search_statistics(results)
            
            print(f"\n📊 Search Statistics:")
            print(f"   Total Results: {stats['total_results']}")
            print(f"   Average Relevance: {stats['avg_relevance']:.4f}")
            print(f"   Sources: {', '.join(stats['sources'][:3])}")
            print(f"   Departments: {', '.join(stats['departments'])}")
            
            print(f"\n📄 Top Results:")
            for j, result in enumerate(results, 1):
                print(f"\n   Result #{j}:")
                print(f"   Source: {result['source']}")
                print(f"   Department: {result['role']}")
                print(f"   Relevance: {result['relevance_score']:.4f}")
                print(f"   Accessible to: {', '.join(result['accessible_roles'])}")
                print(f"   Content Preview: {result['content'][:200]}...")
            
            if not results:
                print("\n   ⚠️  No accessible results found for this role")
        
        except Exception as e:
            print(f"\n❌ Error: {e}")
    
    # Test role-based access validation
    print(f"\n{'='*70}")
    print("ROLE-BASED ACCESS VALIDATION")
    print(f"{'='*70}")
    
    validation_query = "financial information"
    
    for role in ["C-Level", "Finance", "Marketing", "Employees"]:
        results = search.search(validation_query, role, top_k=5)
        print(f"\n{role}: Can access {len(results)} financial documents")
    
    print(f"\n{'='*70}")
    print("✅ MODULE 3 & 4 COMPLETE!")
    print(f"{'='*70}")
    print("\n📋 Deliverables Completed:")
    print("   ✅ Vector database with semantic search")
    print("   ✅ Role-based access control filtering")
    print("   ✅ Query preprocessing and normalization")
    print("   ✅ Relevance scoring and ranking")
    print("   ✅ Access validation and testing")
    print("\n🎯 Next Step: Module 5 - User Authentication & RBAC Middleware")


if __name__ == "__main__":
    test_search_system()
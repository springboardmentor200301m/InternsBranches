"""
Streamlit Frontend for RBAC Chatbot
Module 7 - Interactive Chat Interface with Authentication
"""

import streamlit as st
import requests
from datetime import datetime
import json

# Configuration
API_BASE_URL = "http://localhost:8000"

# Page configuration
st.set_page_config(
    page_title="RBAC Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .role-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        background-color: #1f77b4;
        color: white;
        border-radius: 20px;
        font-weight: bold;
    }
    .source-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin-top: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        color: #000000;
    }
    .user-message {
        background-color: #e3f2fd;
        text-align: right;
        color: #000000;
    }
    .bot-message {
        background-color: #f5f5f5;
        color: #000000;
    }
    .login-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 2rem;
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'token' not in st.session_state:
    st.session_state.token = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'role' not in st.session_state:
    st.session_state.role = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Helper functions
def login(username, password):
    """Authenticate user with backend API"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/auth/login",
            json={"username": username, "password": password},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return True, data
        else:
            return False, {"error": "Invalid credentials"}
    except Exception as e:
        return False, {"error": str(e)}

def query_chatbot(query, token):
    """Send query to RAG-powered chatbot"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(
            f"{API_BASE_URL}/api/query",
            json={"query": query},
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, {"error": f"Error: {response.status_code}"}
    except Exception as e:
        return False, {"error": str(e)}

def logout():
    """Clear session and logout"""
    st.session_state.logged_in = False
    st.session_state.token = None
    st.session_state.username = None
    st.session_state.role = None
    st.session_state.chat_history = []

# Main Application
def main():
    # Header
    st.markdown('<h1 class="main-header">🤖 RBAC Chatbot System</h1>', unsafe_allow_html=True)
    
    # Check if user is logged in
    if not st.session_state.logged_in:
        show_login_page()
    else:
        show_chat_page()

def show_login_page():
    """Display login interface"""
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 🔐 Login to Access Company Chatbot")
        st.markdown("---")
        
        # Login form
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            submitted = st.form_submit_button("🚀 Login", use_container_width=True)
            
            if submitted:
                if username and password:
                    with st.spinner("Authenticating..."):
                        success, data = login(username, password)
                    
                    if success:
                        st.session_state.logged_in = True
                        st.session_state.token = data['access_token']
                        st.session_state.username = data['username']
                        st.session_state.role = data['role']
                        st.success(f"✅ Welcome, {data['username']}!")
                        st.rerun()
                    else:
                        st.error(f"❌ Login failed: {data.get('error', 'Invalid credentials')}")
                else:
                    st.warning("⚠️ Please enter both username and password")
        
        # Test credentials info
        with st.expander("📋 Test Credentials"):
            st.markdown("""
            **Available Test Accounts:**
            
            | Username | Password | Role |
            |----------|----------|------|
            | finance_user | finance123 | Finance |
            | marketing_user | marketing123 | Marketing |
            | hr_user | hr123 | HR |
            | engineering_user | engineering123 | Engineering |
            | employee_user | employee123 | Employees |
            | clevel_user | clevel123 | C-Level |
            """)

def show_chat_page():
    """Display main chat interface"""
    
    # Sidebar with user info
    with st.sidebar:
        st.markdown("### 👤 User Information")
        st.markdown(f"**Username:** {st.session_state.username}")
        st.markdown(f'<div class="role-badge">{st.session_state.role}</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.markdown("### 📚 Your Access")
        
        # Show accessible departments based on role
        role_access = {
            "Finance": ["💰 Finance Reports", "📊 Financial Data"],
            "Marketing": ["📢 Marketing Campaigns", "📈 Market Analysis"],
            "HR": ["👥 Employee Data", "📋 HR Policies"],
            "Engineering": ["⚙️ Technical Docs", "🔧 Engineering Resources"],
            "C-Level": ["💰 Finance", "📢 Marketing", "👥 HR", "⚙️ Engineering", "📚 All Documents"],
            "Employees": ["📚 General Handbook", "📋 Company Policies"]
        }
        
        access_list = role_access.get(st.session_state.role, [])
        for item in access_list:
            st.markdown(f"✅ {item}")
        
        st.markdown("---")
        
        # Clear chat button
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()
        
        # Logout button
        if st.button("🚪 Logout", use_container_width=True):
            logout()
            st.rerun()
        
        st.markdown("---")
        st.markdown("### ℹ️ About")
        st.markdown("""
        This chatbot uses **RAG (Retrieval-Augmented Generation)** to answer questions based on company documents.
        
        **Features:**
        - 🔒 Role-based access control
        - 🔍 Semantic search
        - 📝 Source attribution
        - 🔐 Secure authentication
        """)
    
    # Main chat area
    st.markdown("### 💬 Chat with Company Assistant")
    st.markdown(f"Ask questions about documents you have access to as a **{st.session_state.role}** user.")
    st.markdown("---")
    
    # Display chat history
    chat_container = st.container()
    with chat_container:
        for i, message in enumerate(st.session_state.chat_history):
            if message['type'] == 'user':
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>You:</strong> {message['content']}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message bot-message">
                    <strong>🤖 Assistant:</strong><br>{message['content']}
                </div>
                """, unsafe_allow_html=True)
                
                # Show sources if available
                if 'sources' in message and message['sources']:
                    with st.expander("📚 View Sources"):
                        for source in message['sources']:
                            st.markdown(f"""
                            <div class="source-box">
                                <strong>📄 {source['source']}</strong><br>
                                <small>Department: {source['department'].upper()}</small>
                            </div>
                            """, unsafe_allow_html=True)
    
    # Query input
    st.markdown("---")
    
    with st.form("query_form", clear_on_submit=True):
        col1, col2 = st.columns([5, 1])
        
        with col1:
            user_query = st.text_input(
                "Your Question:",
                placeholder="Ask me anything about company documents...",
                label_visibility="collapsed"
            )
        
        with col2:
            submitted = st.form_submit_button("📤 Send", use_container_width=True)
        
        if submitted and user_query:
            # Add user message to history
            st.session_state.chat_history.append({
                'type': 'user',
                'content': user_query,
                'timestamp': datetime.now()
            })
            
            # Query the chatbot
            with st.spinner("🤔 Thinking..."):
                success, response = query_chatbot(user_query, st.session_state.token)
            
            if success:
                # Add bot response to history
                st.session_state.chat_history.append({
                    'type': 'bot',
                    'content': response['response'],
                    'sources': response.get('sources', []),
                    'timestamp': datetime.now()
                })
            else:
                st.session_state.chat_history.append({
                    'type': 'bot',
                    'content': f"❌ Error: {response.get('error', 'Failed to get response')}",
                    'sources': [],
                    'timestamp': datetime.now()
                })
            
            st.rerun()
    
    # Example queries
    with st.expander("💡 Example Questions"):
        role_examples = {
            "Finance": [
                "What are the Q3 financial results?",
                "What is our annual budget allocation?",
                "Show me the revenue breakdown by segment"
            ],
            "Marketing": [
                "What marketing campaigns are currently running?",
                "What is our market share?",
                "Tell me about customer acquisition strategies"
            ],
            "HR": [
                "What is the PTO policy?",
                "How many open positions do we have?",
                "What are the employee benefits?"
            ],
            "Engineering": [
                "What is our system architecture?",
                "What technologies do we use?",
                "Explain our deployment process"
            ],
            "C-Level": [
                "Give me an overview of all departments",
                "What are the company-wide initiatives?",
                "Show me audit logs"
            ],
            "Employees": [
                "What is the company mission?",
                "What are the work-from-home policies?",
                "How do I submit a vacation request?"
            ]
        }
        
        examples = role_examples.get(st.session_state.role, [])
        for example in examples:
            st.markdown(f"• {example}")

if __name__ == "__main__":
    main()
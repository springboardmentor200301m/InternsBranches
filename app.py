# streamlit_app.py
"""
RBAC RAG System - Frontend Application
Milestone 4: Frontend & Deployment (Weeks 7-8)
Module 7: Streamlit Frontend Development
Module 8: System Integration, Testing & Deployment
"""

import streamlit as st
import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path

# ========== CONFIGURATION ==========
BACKEND_URL = "http://localhost:8000"
APP_VERSION = "1.0.0"
APP_TITLE = "🔐 RBAC RAG System"
APP_DESCRIPTION = "Role-Based Access Control with Retrieval-Augmented Generation"

# ========== SESSION STATE INITIALIZATION ==========
def init_session_state():
    """Initialize all session state variables"""
    defaults = {
        "logged_in": False,
        "username": None,
        "role": None,
        "department": None,
        "chat_history": [],
        "query_count": 0,
        "total_response_time": 0,
        "demo_mode": False,
        "current_conversation_id": None,
        "conversations": {},
        "system_status": "unknown",
        "api_connected": False,
        "show_help": False,
        "dark_mode": False
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# ========== API CLIENT ==========
class BackendAPIClient:
    """API client for backend communication"""
    
    def __init__(self, base_url: str = BACKEND_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.timeout = 30
    
    def check_health(self) -> Dict:
        """Check backend health"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            return {"status": "healthy" if response.status_code == 200 else "unhealthy", "response": response.json()}
        except:
            return {"status": "offline", "response": None}
    
    def login(self, username: str, password: str, role: str) -> Dict:
        """Login to backend"""
        try:
            response = self.session.post(
                f"{self.base_url}/login",
                json={"username": username, "password": password, "role": role},
                timeout=10
            )
            return response.json()
        except Exception as e:
            return {"success": False, "error": f"Connection error: {str(e)}"}
    
    def ask_question(self, query: str, role: str) -> Dict:
        """Ask question to backend"""
        try:
            start_time = time.time()
            response = self.session.post(
                f"{self.base_url}/ask",
                json={"query": query, "role": role},
                timeout=30
            )
            response_time = time.time() - start_time
            
            result = response.json()
            result["response_time"] = response_time
            
            return result
        except Exception as e:
            return {"answer": f"Error: {str(e)}", "confidence": 0, "sources": [], "message": "API Error"}
    
    def get_demo_users(self) -> List[Dict]:
        """Get demo users from backend"""
        try:
            response = self.session.get(f"{self.base_url}/demo-users", timeout=5)
            data = response.json()
            return data.get("demo_users", [])
        except:
            return []
    
    def get_roles(self) -> Dict:
        """Get available roles"""
        try:
            response = self.session.get(f"{self.base_url}/roles", timeout=5)
            return response.json()
        except:
            return {"available_roles": ["Admin", "Finance", "HR", "Engineering", "Marketing", "General"]}
    
    def test_imports(self) -> Dict:
        """Test backend module imports"""
        try:
            response = self.session.get(f"{self.base_url}/test-imports", timeout=5)
            return response.json()
        except:
            return {"success": False, "error": "Backend unavailable"}

# ========== UI COMPONENTS ==========
class UIComponents:
    """Reusable UI components"""
    
    @staticmethod
    def role_badge(role: str) -> str:
        """Create HTML badge for role"""
        colors = {
            "Admin": "#FF6B6B",
            "Finance": "#4ECDC4",
            "HR": "#FFD166",
            "Engineering": "#06D6A0",
            "Marketing": "#9C27B0",
            "General": "#118AB2"
        }
        color = colors.get(role, "#666666")
        
        return f"""
        <div style="
            background-color: {color};
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
            display: inline-block;
            margin: 2px;
        ">
            {role}
        </div>
        """
    
    @staticmethod
    def confidence_indicator(confidence: float) -> Tuple[str, str]:
        """Get confidence indicator color and icon"""
        if confidence >= 0.7:
            return ("#4CAF50", "🟢", "High")
        elif confidence >= 0.4:
            return ("#FF9800", "🟡", "Medium")
        else:
            return ("#F44336", "🔴", "Low")
    
    @staticmethod
    def department_icon(department: str) -> str:
        """Get icon for department"""
        icons = {
            "Finance": "💰",
            "HR": "👥",
            "Engineering": "⚙️",
            "Marketing": "📢",
            "General": "🏢",
            "Admin": "👑"
        }
        return icons.get(department, "📄")
    
    @staticmethod
    def create_chat_message(sender: str, message: str, timestamp: datetime, 
                          role: str = None, confidence: float = None, 
                          sources: List[Dict] = None):
        """Create styled chat message"""
        if sender == "user":
            return f"""
            <div style="
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 15px;
                border-radius: 15px;
                margin: 10px 0;
                max-width: 80%;
                margin-left: auto;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            ">
                <div style="font-weight: bold; margin-bottom: 5px;">👤 You</div>
                <div style="margin-bottom: 8px;">{message}</div>
                <div style="font-size: 0.8em; opacity: 0.9; text-align: right;">
                    {timestamp.strftime('%H:%M:%S')}
                    {f'<span style="margin-left: 10px;">{UIComponents.role_badge(role)}</span>' if role else ''}
                </div>
            </div>
            """
        else:  # bot
            color, icon, level = UIComponents.confidence_indicator(confidence) if confidence else ("#666", "", "")
            
            sources_html = ""
            if sources:
                sources_html = f"""
                <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid rgba(255,255,255,0.2);">
                    <div style="font-size: 0.9em; margin-bottom: 8px; opacity: 0.9;">📚 Sources ({len(sources)}):</div>
                    <div style="font-size: 0.85em;">
                """
                for i, source in enumerate(sources, 1):
                    sources_html += f"""
                        <div style="margin: 5px 0; padding: 5px; background: rgba(255,255,255,0.1); border-radius: 5px;">
                            <div style="display: flex; align-items: center; gap: 8px;">
                                <span>{UIComponents.department_icon(source.get('department', ''))}</span>
                                <span style="font-weight: bold;">{source.get('document', 'Unknown')}</span>
                            </div>
                            <div style="font-size: 0.9em; opacity: 0.8; margin-left: 28px;">
                                {source.get('department', '')} • {source.get('role', '')}
                            </div>
                        </div>
                    """
                sources_html += "</div></div>"
            
            return f"""
            <div style="
                background: linear-gradient(135deg, #434343 0%, #000000 100%);
                color: white;
                padding: 15px;
                border-radius: 15px;
                margin: 10px 0;
                max-width: 80%;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            ">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <div style="font-weight: bold;">🤖 Assistant</div>
                    {f'<div style="display: flex; align-items: center; gap: 8px; font-size: 0.9em;"><span>{icon}</span><span>Confidence: {confidence*100:.0f}% ({level})</span></div>' if confidence else ''}
                </div>
                <div style="margin-bottom: 10px; line-height: 1.5;">{message}</div>
                {sources_html}
                <div style="font-size: 0.8em; opacity: 0.9; text-align: right; margin-top: 10px;">
                    {timestamp.strftime('%H:%M:%S')}
                </div>
            </div>
            """

# ========== MAIN APPLICATION ==========
class RBACRAGApp:
    """Main application class"""
    
    def __init__(self):
        self.api = BackendAPIClient()
        self.ui = UIComponents()
        init_session_state()
        self.setup_page_config()
    
    def setup_page_config(self):
        """Configure Streamlit page settings"""
        st.set_page_config(
            page_title="RBAC RAG System",
            page_icon="🔐",
            layout="wide",
            initial_sidebar_state="expanded",
            menu_items={
                'Get Help': 'https://github.com/yourusername/rbac-rag-system',
                'Report a bug': "https://github.com/yourusername/rbac-rag-system/issues",
                'About': f"# RBAC RAG System v{APP_VERSION}\nSecure Role-Based Document Access with AI"
            }
        )
    
    def apply_custom_styles(self):
        """Apply custom CSS styles"""
        st.markdown("""
        <style>
        /* Main styles */
        .main-header {
            font-size: 2.8rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            margin-bottom: 1rem;
        }
        
        .sub-header {
            font-size: 1.4rem;
            color: #4a5568;
            margin: 1.5rem 0 1rem 0;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #e2e8f0;
        }
        
        /* Card styles */
        .info-card {
            background: linear-gradient(135deg, #f6f9fc 0%, #e9ecef 100%);
            padding: 1.5rem;
            border-radius: 10px;
            border-left: 5px solid #4299e1;
            margin: 1rem 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        }
        
        .success-card {
            background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
            padding: 1rem;
            border-radius: 10px;
            border-left: 5px solid #28a745;
            margin: 1rem 0;
        }
        
        .warning-card {
            background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
            padding: 1rem;
            border-radius: 10px;
            border-left: 5px solid #ffc107;
            margin: 1rem 0;
        }
        
        /* Button styles */
        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        }
        
        /* Metric cards */
        .metric-card {
            background: white;
            padding: 1rem;
            border-radius: 10px;
            border: 1px solid #e2e8f0;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }
        
        /* Chat container */
        .chat-container {
            max-height: 500px;
            overflow-y: auto;
            padding: 1rem;
            background: #f8f9fa;
            border-radius: 10px;
            border: 1px solid #e2e8f0;
        }
        
        /* Custom scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
        }
        </style>
        """, unsafe_allow_html=True)
    
    def render_header(self):
        """Render application header"""
        st.markdown(f'<h1 class="main-header">{APP_TITLE}</h1>', unsafe_allow_html=True)
        st.markdown(f'<p style="text-align: center; color: #718096; font-size: 1.1rem;">{APP_DESCRIPTION}</p>', unsafe_allow_html=True)
        
        # System status indicator
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            status = self.api.check_health()
            if status["status"] == "healthy":
                st.success("✅ Backend Connected")
            elif status["status"] == "unhealthy":
                st.warning("⚠️ Backend Issues")
            else:
                st.error("❌ Backend Offline")
    
    def render_login_section(self):
        """Render login interface"""
        st.markdown('<div class="sub-header">🔐 Authentication</div>', unsafe_allow_html=True)
        
        with st.container():
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                with st.form("login_form"):
                    username = st.text_input("Username", placeholder="Enter your username")
                    password = st.text_input("Password", type="password", placeholder="Enter your password")
                    role = st.selectbox("Role", ["Admin", "Finance", "HR", "Engineering", "Marketing", "General"])
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        login_btn = st.form_submit_button("🔑 Login", use_container_width=True)
                    with col_b:
                        demo_btn = st.form_submit_button("🧪 Demo Mode", use_container_width=True)
                
                if login_btn and username and password:
                    with st.spinner("Authenticating..."):
                        result = self.api.login(username, password, role)
                        if result.get("success"):
                            st.session_state.logged_in = True
                            st.session_state.username = result["username"]
                            st.session_state.role = result["role"]
                            st.session_state.department = result["role"]
                            st.success(f"✅ Welcome {result['username']}!")
                            st.rerun()
                        else:
                            st.error(f"❌ {result.get('error', 'Login failed')}")
                
                if demo_btn:
                    st.session_state.demo_mode = True
                    st.session_state.logged_in = True
                    st.session_state.username = "demo_user"
                    st.session_state.role = "Admin"
                    st.session_state.department = "Admin"
                    st.success("🧪 Demo mode activated!")
                    st.rerun()
                
                # Quick login buttons
                st.markdown("---")
                st.markdown("### ⚡ Quick Login")
                
                demo_users = self.api.get_demo_users()
                if demo_users:
                    cols = st.columns(min(3, len(demo_users)))
                    for idx, user in enumerate(demo_users[:6]):
                        with cols[idx % 3]:
                            if st.button(f"👤 {user['username']}", key=f"quick_{user['username']}"):
                                st.session_state.logged_in = True
                                st.session_state.username = user['username']
                                st.session_state.role = user['role']
                                st.session_state.department = user['role']
                                st.success(f"✅ Logged in as {user['username']} ({user['role']})")
                                st.rerun()
    
    def render_user_dashboard(self):
        """Render user dashboard after login"""
        col1, col2, col3 = st.columns([3, 2, 1])
        
        with col1:
            st.markdown(f"### 👋 Welcome back, {st.session_state.username}!")
        
        with col2:
            st.markdown(self.ui.role_badge(st.session_state.role), unsafe_allow_html=True)
        
        with col3:
            if st.button("🚪 Logout"):
                self.logout()
        
        # User metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Queries", st.session_state.query_count)
        with col2:
            avg_time = st.session_state.total_response_time / max(st.session_state.query_count, 1)
            st.metric("Avg Response Time", f"{avg_time:.2f}s")
        with col3:
            st.metric("Role", st.session_state.role)
        with col4:
            st.metric("Conversations", len(st.session_state.conversations))
    
    def render_chat_interface(self):
        """Render chat interface"""
        st.markdown('<div class="sub-header">💬 Ask Questions</div>', unsafe_allow_html=True)
        
        # Query input
        with st.form("query_form", clear_on_submit=True):
            query = st.text_area(
                "Your Question:",
                placeholder=f"Ask about {st.session_state.role} documents...",
                height=100,
                help="Enter your question here. The system will search documents based on your role."
            )
            
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                advanced = st.checkbox("Show Advanced Options")
            with col2:
                submit = st.form_submit_button("🚀 Submit", use_container_width=True)
            with col3:
                clear = st.form_submit_button("🗑️ Clear Chat", use_container_width=True)
            
            if advanced:
                col_a, col_b = st.columns(2)
                with col_a:
                    min_confidence = st.slider("Minimum Confidence", 0.0, 1.0, 0.3, 0.05)
                with col_b:
                    max_sources = st.slider("Max Sources to Show", 1, 10, 3)
        
        if clear:
            st.session_state.chat_history = []
            st.rerun()
        
        if submit and query:
            self.process_query(query, min_confidence if advanced else 0.3)
        
        # Chat history
        self.render_chat_history()
    
    def process_query(self, query: str, min_confidence: float):
        """Process user query"""
        with st.spinner("🔍 Searching documents..."):
            # Add user message
            user_msg = {
                "type": "user",
                "content": query,
                "timestamp": datetime.now(),
                "role": st.session_state.role
            }
            st.session_state.chat_history.append(user_msg)
            
            # Get response from backend
            start_time = time.time()
            response = self.api.ask_question(query, st.session_state.role)
            response_time = time.time() - start_time
            
            # Update metrics
            st.session_state.query_count += 1
            st.session_state.total_response_time += response_time
            
            # Add bot response
            bot_msg = {
                "type": "bot",
                "content": response.get("answer", "No answer received"),
                "confidence": response.get("confidence", 0),
                "sources": response.get("sources", []),
                "timestamp": datetime.now(),
                "message": response.get("message", ""),
                "response_time": response_time
            }
            st.session_state.chat_history.append(bot_msg)
            
            # Store conversation
            conv_id = f"conv_{len(st.session_state.conversations) + 1}"
            st.session_state.conversations[conv_id] = {
                "query": query,
                "response": response,
                "timestamp": datetime.now(),
                "role": st.session_state.role
            }
            
            st.rerun()
    
    def render_chat_history(self):
        """Render chat history"""
        if st.session_state.chat_history:
            st.markdown('<div class="sub-header">📜 Conversation History</div>', unsafe_allow_html=True)
            
            with st.container():
                chat_html = ""
                for msg in st.session_state.chat_history[-20:]:  # Show last 20 messages
                    if msg["type"] == "user":
                        chat_html += self.ui.create_chat_message(
                            "user", msg["content"], msg["timestamp"], msg.get("role")
                        )
                    else:
                        chat_html += self.ui.create_chat_message(
                            "bot", msg["content"], msg["timestamp"], 
                            confidence=msg.get("confidence"),
                            sources=msg.get("sources", [])
                        )
                
                st.markdown(f'<div class="chat-container">{chat_html}</div>', unsafe_allow_html=True)
                
                # Export conversation button
                if st.button("📥 Export Conversation"):
                    self.export_conversation()
    
    def render_source_documents(self):
        """Render source documents section"""
        st.markdown('<div class="sub-header">📚 Source Documents</div>', unsafe_allow_html=True)
        
        # Get all sources from chat history
        all_sources = []
        for msg in st.session_state.chat_history:
            if msg["type"] == "bot" and msg.get("sources"):
                all_sources.extend(msg["sources"])
        
        if all_sources:
            # Create DataFrame for display
            df_data = []
            for source in all_sources:
                df_data.append({
                    "Document": source.get("document", "Unknown"),
                    "Department": source.get("department", "General"),
                    "Role": source.get("role", "General"),
                    "Icon": self.ui.department_icon(source.get("department", ""))
                })
            
            df = pd.DataFrame(df_data)
            
            # Display statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Sources", len(all_sources))
            with col2:
                unique_docs = df["Document"].nunique()
                st.metric("Unique Documents", unique_docs)
            with col3:
                departments = df["Department"].unique()
                st.metric("Departments", len(departments))
            
            # Display table
            with st.expander("📋 View All Sources", expanded=True):
                st.dataframe(
                    df,
                    column_config={
                        "Icon": st.column_config.TextColumn("", width="small"),
                        "Document": st.column_config.TextColumn("Document", width="large"),
                        "Department": st.column_config.TextColumn("Department"),
                        "Role": st.column_config.TextColumn("Role")
                    },
                    hide_index=True,
                    use_container_width=True
                )
            
            # Create visualization
            fig = px.sunburst(
                df, 
                path=['Department', 'Document'],
                title="Document Access Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No source documents have been retrieved yet. Ask some questions to see sources here!")
    
    def render_role_guide(self):
        """Render role guide section"""
        st.markdown('<div class="sub-header">📖 Role Guide & Sample Questions</div>', unsafe_allow_html=True)
        
        role_guides = {
            "Admin": {
                "description": "Full access to all company documents and information.",
                "sample_questions": [
                    "Show me all company financial reports",
                    "What are the employee statistics?",
                    "What technologies are we using?",
                    "Show marketing campaign results",
                    "Give me a company overview"
                ],
                "access": "All documents"
            },
            "Finance": {
                "description": "Access to financial documents and general company information.",
                "sample_questions": [
                    "What was the revenue increase last quarter?",
                    "Show me profit margins for Q3",
                    "What are the budget allocations?",
                    "Show me financial projections",
                    "What are our major expenses?"
                ],
                "access": "Finance + General documents"
            },
            "HR": {
                "description": "Access to HR documents, employee data, and general information.",
                "sample_questions": [
                    "What are the employee benefits?",
                    "Show me the remote work policy",
                    "What is the leave policy?",
                    "How many employees do we have?",
                    "What are the performance review guidelines?"
                ],
                "access": "HR + General documents"
            },
            "Engineering": {
                "description": "Access to technical documentation and general company information.",
                "sample_questions": [
                    "What is our tech stack?",
                    "Show me the system architecture",
                    "What are the coding standards?",
                    "What APIs do we have?",
                    "What development tools do we use?"
                ],
                "access": "Engineering + General documents"
            },
            "Marketing": {
                "description": "Access to marketing documents and general company information.",
                "sample_questions": [
                    "Show me recent campaign results",
                    "What is our brand positioning?",
                    "What are the marketing strategies?",
                    "Show customer engagement metrics",
                    "What social media platforms do we use?"
                ],
                "access": "Marketing + General documents"
            },
            "General": {
                "description": "Access to general company information only.",
                "sample_questions": [
                    "What does the company do?",
                    "When was the company founded?",
                    "What is our mission statement?",
                    "Show me company locations",
                    "What are the office hours?"
                ],
                "access": "General documents only"
            }
        }
        
        guide = role_guides.get(st.session_state.role, role_guides["General"])
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("### 📋 Access Level")
            st.markdown(f'<div class="info-card">{guide["access"]}</div>', unsafe_allow_html=True)
            
            st.markdown("### 🎯 Quick Actions")
            for question in guide["sample_questions"][:3]:
                if st.button(f"❓ {question[:40]}...", key=f"sample_{hash(question)}"):
                    self.process_query(question, 0.3)
        
        with col2:
            st.markdown("### 📝 Description")
            st.markdown(f'<div class="info-card">{guide["description"]}</div>', unsafe_allow_html=True)
            
            st.markdown("### 💡 Sample Questions")
            for question in guide["sample_questions"]:
                st.markdown(f"- {question}")
    
    def render_system_info(self):
        """Render system information section"""
        st.markdown('<div class="sub-header">⚙️ System Information</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Performance Metrics")
            metrics_data = {
                "Metric": ["Total Queries", "Avg Response Time", "Chat Messages", "Sources Retrieved"],
                "Value": [
                    st.session_state.query_count,
                    f"{st.session_state.total_response_time / max(st.session_state.query_count, 1):.2f}s",
                    len(st.session_state.chat_history),
                    sum(len(msg.get('sources', [])) for msg in st.session_state.chat_history if msg['type'] == 'bot')
                ]
            }
            st.table(pd.DataFrame(metrics_data))
        
        with col2:
            st.markdown("### 🔧 System Status")
            
            # Test backend modules
            import_result = self.api.test_imports()
            if import_result.get("success"):
                st.success("✅ All modules loaded")
            else:
                st.warning("⚠️ Module issues")
            
            # Get roles
            roles_data = self.api.get_roles()
            st.info(f"📋 {len(roles_data.get('available_roles', []))} roles available")
            
            # Health check
            health = self.api.check_health()
            if health["status"] == "healthy":
                st.success("✅ Backend healthy")
            else:
                st.error("❌ Backend issues")
    
    def export_conversation(self):
        """Export conversation to JSON"""
        export_data = {
            "user": st.session_state.username,
            "role": st.session_state.role,
            "timestamp": datetime.now().isoformat(),
            "conversation": st.session_state.chat_history[-10:]  # Last 10 messages
        }
        
        # Create downloadable file
        json_str = json.dumps(export_data, indent=2, default=str)
        st.download_button(
            label="📥 Download Conversation",
            data=json_str,
            file_name=f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    
    def logout(self):
        """Logout user"""
        for key in ["logged_in", "username", "role", "department", "chat_history", 
                   "query_count", "total_response_time", "demo_mode"]:
            if key in st.session_state:
                st.session_state[key] = False if key == "logged_in" else None if key in ["username", "role", "department"] else [] if key == "chat_history" else 0 if key in ["query_count", "total_response_time"] else False
        st.success("✅ Logged out successfully!")
        st.rerun()
    
    def render_sidebar(self):
        """Render sidebar content"""
        with st.sidebar:
            st.image("https://img.icons8.com/color/96/000000/security-checked.png", width=80)
            st.markdown(f"### {APP_TITLE}")
            st.markdown(f"*Version {APP_VERSION}*")
            
            st.markdown("---")
            
            if st.session_state.logged_in:
                st.markdown(f"**User:** {st.session_state.username}")
                st.markdown(f"**Role:** {st.session_state.role}")
                st.markdown(f"**Department:** {st.session_state.department}")
                
                st.markdown("---")
                
                # Navigation
                st.markdown("### 🧭 Navigation")
                page = st.radio(
                    "Go to:",
                    ["💬 Chat", "📚 Sources", "📖 Guide", "⚙️ System"],
                    index=0
                )
                
                st.session_state.current_page = page
                
                st.markdown("---")
                
                # Quick actions
                st.markdown("### ⚡ Quick Actions")
                if st.button("🔄 Refresh", use_container_width=True):
                    st.rerun()
                
                if st.button("📋 New Conversation", use_container_width=True):
                    st.session_state.chat_history = []
                    st.rerun()
                
                st.markdown("---")
                
                # Documentation links
                st.markdown("### 📚 Documentation")
                st.markdown("[User Guide](https://github.com/yourusername/rbac-rag-system/wiki/User-Guide)")
                st.markdown("[API Documentation](https://github.com/yourusername/rbac-rag-system/wiki/API-Docs)")
                st.markdown("[Role Guide](https://github.com/yourusername/rbac-rag-system/wiki/Role-Guide)")
            
            else:
                st.markdown("### ℹ️ Getting Started")
                st.markdown("""
                1. **Select your role** from dropdown
                2. **Enter credentials** or use demo mode
                3. **Ask questions** based on your role
                4. **View sources** and confidence scores
                
                **Demo Credentials:**
                - Admin: admin / admin123
                - Finance: finance / finance123
                - HR: hr / hr123
                """)
    
    def run(self):
        """Run the main application"""
        self.apply_custom_styles()
        self.render_header()
        self.render_sidebar()
        
        if not st.session_state.logged_in:
            self.render_login_section()
            
            # Show features preview
            st.markdown('<div class="sub-header">🚀 System Features</div>', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("""
                ### 🔐 Secure RBAC
                - Role-based document access
                - Secure authentication
                - Data isolation by role
                """)
            with col2:
                st.markdown("""
                ### 🤖 AI-Powered
                - Semantic search
                - Intelligent answers
                - Confidence scoring
                """)
            with col3:
                st.markdown("""
                ### 📊 Professional UI
                - Chat interface
                - Source tracking
                - Performance metrics
                """)
        else:
            # Main application pages
            page = st.session_state.get("current_page", "💬 Chat")
            
            if page == "💬 Chat":
                self.render_user_dashboard()
                self.render_chat_interface()
            elif page == "📚 Sources":
                self.render_user_dashboard()
                self.render_source_documents()
            elif page == "📖 Guide":
                self.render_user_dashboard()
                self.render_role_guide()
            elif page == "⚙️ System":
                self.render_user_dashboard()
                self.render_system_info()

# ========== RUN APPLICATION ==========
if __name__ == "__main__":
    app = RBACRAGApp()
    app.run()
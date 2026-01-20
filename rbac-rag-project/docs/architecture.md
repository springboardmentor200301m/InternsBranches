# System Architecture – Company Internal RBAC Chatbot

## Overview
This project implements a secure internal chatbot using Retrieval Augmented Generation (RAG) combined with Role-Based Access Control (RBAC). The system ensures users can only access documents authorized for their role.

## High-Level Flow
User → Streamlit Frontend → Authentication → RBAC Filtering → Vector Database Search → RAG Pipeline → LLM → Response

## Components
- **Frontend**: Streamlit (login + chat interface)
- **Authentication**: Session-based role identification
- **RBAC Engine**: Role hierarchy filtering before retrieval
- **Vector Database**: ChromaDB
- **Embedding Model**: all-MiniLM-L6-v2
- **LLM**: LLaMA 3 (OpenRouter)

## Security Enforcement
- Role is identified at login
- Unauthorized documents are filtered before retrieval
- LLM receives only role-approved context
- Sources are displayed outside LLM responses

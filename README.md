# 🤖 Corporate Internal RAG Chatbot with RBAC

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Framework](https://img.shields.io/badge/Framework-LangChain-green)
![Security](https://img.shields.io/badge/Security-RBAC%20%2B%20JWT-red)

## 📌 Project Overview
This project is an internal **Question-Answering Bot** designed for secure corporate environments. It uses **Retrieval-Augmented Generation (RAG)** to answer employee queries based on internal documents and enforces role-based access restrictions.

Crucially, it implements **Role-Based Access Control (RBAC)** to ensure employees only access data permitted for their department. For example, a Finance user can access financial reports, but cannot access HR documents.

---

## 🚀 Key Features
* **📚 RAG Pipeline:** Ingests and indexes internal documents for accurate, context-aware answers.
* **🔐 Zero-Trust Security:** Every query is filtered based on the user's role (Finance, HR, Engineering, Marketing).
* **🧠 Hybrid Intelligence:** Uses internal docs for specific questions and switches to General AI for general knowledge.
* **🔑 JWT Authentication:** Secure login system with hashed passwords and session management.
* **⚡ Modern Stack:** Built with FastAPI (Backend), Streamlit (Frontend), and ChromaDB (Vector Store).

---

## 🛠️ Tech Stack
* **Frontend:** Streamlit
* **Backend:** FastAPI
* **LLM:** Google Gemini Pro (`gemini-pro-latest`)
* **Vector DB:** ChromaDB (Local Persistence)
* **Orchestration:** LangChain
* **Auth:** OAuth2 + JWT (HS256) + Bcrypt

---

## 🔐 Authentication Design (Milestone 4)
We implemented a secure **Role-Based Access Control** system.

### 1. User Roles & Scope
| Username | Role | Access Scope |
| :--- | :--- | :--- |
| `finance_user` | **Finance** | `resources/Finance/` + `resources/General/` |
| `hr_user` | **HR** | `resources/HR/` + `resources/General/` |
| `eng_user` | **Engineering** | `resources/Engineering/` + `resources/General/` |
| `marketing_user`| **Marketing** | `resources/Marketing/` + `resources/General/` |

### 2. Login Flow
1.  **Login:** User enters credentials in the Streamlit UI.
2.  **Verify:** Backend checks the hash against the secure registry.
3.  **Token:** If valid, the server issues a **JWT Token** containing the user's Role.
4.  **Query:** Every chat message includes this token. The backend extracts the role and applies a **Strict Filter** to the Vector Database search.

---

## 📂 Project Structure
```bash
rag-chatbot/
├── app/
│   ├── main.py          # FastAPI Backend (Routes & Logic)
│   ├── auth.py          # Authentication (Hashing & JWT)
│   ├── ingest.py        # ETL Pipeline (Load -> Chunk -> Vectorize)
│   └── models.py        # Pydantic Data Schemas
├── frontend/
│   └── streamlit_app.py # User Interface
├── resources/           # Document Knowledge Base
│   ├── Finance/         # (Restricted)
│   ├── HR/              # (Restricted)
│   ├── Marketing/       # (Restricted)
│   ├── Engineering/     # (Restricted)
│   └── General/         # (Public - Accessible by all)
├── chroma_db/           # Local Vector Database
├── requirements.txt     # Dependencies
└── README.md            # Documentation
```

---

## 🏃‍♂️ Installation & Setup

1. Clone the Repository
```bash
git clone https://github.com/balaji-pulivarthi/RAG-chatbot.git
cd RAG-chatbot
```

2. Set Up Virtual Environment
```bash
# Create venv
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate
```

3. Install Dependencies
```bash
pip install -r requirements.txt
```

4. Configure Environment Variables  
Create a `.env` file in the root directory and add your API keys and secrets:
```env
GOOGLE_API_KEY="your_google_api_key_here"
SECRET_KEY="your_secret_key_for_jwt_signing"
ALGORITHM="HS256"
```

5. Ingest Data (Build the Brain)  
Process the documents in the `resources/` folder and build the ChromaDB vector store:
```bash
python -m app.ingest
```

---

## 💻 Usage Guide

1. Start the Backend Server  
In your first terminal (with the venv activated):
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
Server will be available at: http://127.0.0.1:8000

2. Start the Frontend UI  
In a second terminal (activate venv if needed):
```bash
streamlit run frontend/streamlit_app.py
```

3. Log in with Demo Credentials  
The system includes pre-defined users for demonstration:

| Username       | Role         | Access Scope                       |
| -------------- | ------------ | ---------------------------------- |
| finance_user   | Finance      | Finance/ + General/                |
| hr_user        | HR           | HR/ + General/                     |
| eng_user       | Engineering  | Engineering/ + General/            |
| marketing_user | Marketing    | Marketing/ + General/              |

(Note: Passwords are defined/hashed in `app/auth.py` for the demo users.)

---

## 🧠 Technical Implementation Details

### 🔹 1. Security Architecture (RBAC)
We implemented a Metadata Filtering strategy.

When documents are ingested, they are tagged with metadata: `{'department': 'HR'}`.  
When a user queries, the backend extracts their role from the JWT token.  
A mandatory filter is applied to the ChromaDB query:

```python
filter = {
    "$or": [
        {"department": user_role},
        {"department": "General"}
    ]
}
```

Result: It is mathematically impossible for the database to return a chunk from a restricted department.

### 🔹 2. RAG Pipeline Optimization
* Chunking: Documents are split into 500-character chunks with 50-character overlap to preserve context.
* Embeddings: We use `all-MiniLM-L6-v2` which maps text to a 384-dimensional vector space.
* Hybrid Search: The system first checks internal documents. If the similarity score is low (indicating the answer isn't in the docs), it instructs the LLM to use its general knowledge.

---

## 🔧 Troubleshooting

1. 404 Not Found (Gemini Model)  
Issue: The API cannot find the specific model version.  
Fix: Open `app/main.py` and ensure `model="gemini-pro"` is used instead of `"gemini-1.5-flash"`.

2. 429 Resource Exhausted  
Issue: You hit the Google Free Tier rate limit.  
Fix: Wait 60 seconds and try again, or upgrade quota / add retry/backoff logic.

3. ModuleNotFoundError  
Issue: Python cannot find installed libraries.  
Fix: Ensure your virtual environment is active. You should see `(venv)` in your terminal prompt.

---

## 🔮 Future Roadmap
- [ ] Voice Interaction: Add speech-to-text for hands-free querying.
- [ ] Slack Integration: Deploy as a bot within enterprise chat tools.
- [ ] Admin Dashboard: UI for uploading documents without using Python scripts.
- [ ] Multi-Language Support: Allow querying in Hindi, Spanish, etc.

---


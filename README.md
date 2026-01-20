# 🤖 Corporate Internal RAG Chatbot with RBAC

## 📌 Project Overview
This project is an internal Question-Answering bot designed for corporate environments. It uses **Retrieval-Augmented Generation (RAG)** to answer employee queries based on internal documents (PDFs, Markdown, CSVs). 

Crucially, it implements **Role-Based Access Control (RBAC)** to ensure employees only access data permitted for their department (e.g., Finance users cannot see HR salary data).

## 🛠️ Tech Stack
* **Frontend:** Streamlit (Python)
* **Backend:** FastAPI (Python)
* **LLM:** Google Gemini Pro (`gemini-pro-latest`)
* **Vector Database:** ChromaDB (Local Persistence)
* **Framework:** LangChain
* **Authentication:** JWT (JSON Web Tokens) with Bcrypt hashing

---

## 🔐 Authentication Design (Milestone 4)

We implemented a **Zero-Trust Security Model** where every query is validated against the user's role before searching the database.

### 1. Authentication Strategy
* **Method:** Static Configuration (Username + Hashed Password).
* **Reasoning:** For this internal prototype, we utilize a secure dictionary registry. This mimics a centralized LDAP/Active Directory without the overhead of an external SQL database, allowing for easier auditing and rapid deployment.
* **Token Standard:** We use **JWT (HS256)** to maintain session state securely.

### 2. User-Role Schema
| Username | Role | Access Scope |
| :--- | :--- | :--- |
| `finance_user` | **Finance** | `resources/Finance`, `resources/General` |
| `hr_user` | **HR** | `resources/HR`, `resources/General` |
| `eng_user` | **Engineering** | `resources/Engineering`, `resources/General` |

### 3. Login & Query Flow Diagram

```mermaid
graph TD
    User[User] -->|1. Enter Credentials| UI[Streamlit UI]
    UI -->|2. POST /token| API[FastAPI Backend]
    API -->|3. Verify Hash| Auth[Auth Module]
    Auth -->|4. Return JWT| UI
    
    User -->|5. Ask Question| UI
    UI -->|6. Send Query + JWT| API
    API -->|7. Decode Role| Middleware[Security Middleware]
    Middleware -->|8. Apply Filter {dept: role}| VDB[(ChromaDB)]
    VDB -->|9. Retrieve Allowed Chunks| LLM[Gemini LLM]
    LLM -->|10. Generate Answer| User



    🚀 Setup & Installation
1. Prerequisites
Python 3.10+

Google API Key (for Gemini)

2. Installation
Bash

# Clone the repository
git clone <repo-url>
cd rag-chatbot

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate  # Windows

# Install dependencies
pip install -r requirements.txt
3. Environment Configuration
Create a .env file in the root directory:

Code snippet

GOOGLE_API_KEY="your_google_api_key_here"
SECRET_KEY="my_secret_key_for_jwt"
ALGORITHM="HS256"
🏃‍♂️ Usage Guide
Step 1: Ingest Data
Process the documents in the resources/ folder and populate the vector database.

Bash

python -m app.ingest
Output: ✅ Found X documents... 💾 Saved chunks to ChromaDB.

Step 2: Start the Backend Server
Launch the FastAPI server to handle logic and authentication.

Bash

uvicorn app.main:app --reload
Runs on: http://127.0.0.1:8000

Step 3: Launch the Frontend
Open the user interface in your browser.

Bash

streamlit run frontend/streamlit_app.py
Opens: http://localhost:8501


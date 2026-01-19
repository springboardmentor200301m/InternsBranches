# 🤖 AI Company Internal Chatbot with Role-Based Access Control (RBAC)

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.25+-FF4B4B?logo=streamlit&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_DB-blue)

A secure internal chatbot system that utilizes **Retrieval-Augmented Generation (RAG)** to provide department-specific information while strictly enforcing **Role-Based Access Control (RBAC)**. This ensures that users only retrieve documents they are authorized to see based on their organizational role.

---

## 🚀 Key Features

- **RBAC-Aware Retrieval**: Implements metadata filtering in ChromaDB to restrict document access by role (Finance, HR, Engineering, etc.).
- **High-Performance SLM**: Optimized with `Qwen2.5-1.5B-Instruct` for fast local inference with a target response time of under 3 seconds.
- **Source Attribution**: Provides clear citations including document titles, sections, and department tags for every response.
- **Hallucination Protection**: Active grounding checks using cosine similarity to ensure generated answers are supported by the retrieved context.
- **Secure Authentication**: JWT-based login system with role-persistent sessions.

---

## 🛠️ Technical Stack

| Component | Technology |
| :--- | :--- |
| **Backend** | FastAPI, Python 3.8+ |
| **Frontend** | Streamlit |
| **Vector DB** | ChromaDB |
| **LLM** | Qwen2.5-1.5B-Instruct (via HuggingFace) |
| **Embeddings** | Sentence Transformers (`all-mpnet-base-v2`) |
| **Database** | SQLite (User & Role Management) |

---

## 📂 Project Structure

```text
📂 company-internal-chatbot
├── 📁 .github               # GitHub Actions templates
├── 📁 chroma_db             # Persistent vector database storage
├── 📁 data                  # Raw Markdown/CSV source files
├── app.py                   # Streamlit Frontend UI
├── main.py                  # FastAPI Backend & RAG pipeline
├── data_ingestion.py        # Document parsing & indexing script
├── chunks.json              # Intermediate document fragments
├── requirements.txt         # Project dependencies
└── README.md                # Project documentation
```
⚙️ Installation & Setup
-----------------------

### 1\. Clone the Repository

Bash

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   git clone [YOUR_GITHUB_LINK]  cd company-internal-chatbot   `

### 2\. Environment Setup

Bash

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   python -m venv venv  source venv/bin/activate  # Windows: venv\Scripts\activate  pip install -r requirements.txt   `

### 3\. Data Ingestion

Run the ingestion script to parse raw files and build the vector index:

Bash

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   python data_ingestion.py   `

### 4\. Run the Application

Start the Backend:

Bash

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   uvicorn main:app --port 8000   `

Start the Frontend:

Bash

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   streamlit run app.py   `

🔐 Role Hierarchy & Access
--------------------------

Access is strictly governed by the following permission mapping:

**RolePermitted DepartmentsC-Level**Finance, HR, Engineering, Marketing, General**HR**HR, General**Finance**Finance, General**Engineering**Engineering, General**Employee**General

📊 Performance Metrics
----------------------

**MetricTargetDocument Parsing**100% Accuracy**Retrieval Latency**< 500ms**End-to-End Response**< 3 seconds

📄 License
----------

This project is licensed under the MIT License.


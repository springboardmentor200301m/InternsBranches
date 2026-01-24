
# Milestone 1: Data Preparation & Vector DB (Weeks 1–2)

---

## Module 1: Environment Setup & Data Exploration (Week 1)

### Objective
Set up the development environment, explore all company documents (Markdown + CSV), and create a clear mapping between user roles and document types.

---

### Tasks Completed
1. **Set up Python virtual environment**
   - Created a Python virtual environment
   - Installed required dependencies:
     - FastAPI
     - Streamlit
     - LangChain
     - sentence-transformers
     - pandas
     - chromadb / qdrant-client
   - Verified installation by running sample imports
2. **Cloned the GitHub Repository**
   - Cloned the repository containing all company RAG documents
   - Observed folder structure and document organization
3. **Explored All Documents**
   - Opened and inspected every `.md` and `.csv` file
   - Understood structure, formatting, and content patterns
   - Identified noise (HTML tags, markdown headers, spacing issues)
4. **Created Role-to-Document Mapping**
   - Based on company hierarchy:

| Role        | Allowed Documents           |
|-------------|----------------------------|
| Finance     | finance reports            |
| Marketing   | marketing content          |
| HR          | employee-related docs      |
| Engineering | technical documents        |
| C-Level     | all documents              |
| Employees   | general handbook           |

This mapping is used later to enforce RBAC at the chunk level.

---

## Module 2: Document Preprocessing & Metadata Tagging (Week 2)

### Objective
Parse all documents, clean the text thoroughly, split them into small chunks, and assign role-based metadata to each chunk for vector DB ingestion.

---

### Tasks Completed
1. **Parsed Markdown and CSV Documents**
   - Implemented a loader to read:
     - `.md` files as plain text
     - `.csv` files using pandas, removing empty rows and filling missing values
   - Converted CSV tables into plain text format for embedding
2. **Cleaned and Normalized Text**
   - Implemented a full cleaning pipeline:
     - Removed HTML tags
     - Removed Markdown symbols (`#`, `##`, etc.)
     - Removed extra spaces
     - Removed URLs, emails, copyright lines
     - Normalized whitespace
     - Converted text to lowercase
     - Standardized bullet points
3. **Handled Encoding and Formatting Issues**
   - Fixed inconsistent line breaks
   - Removed unnecessary symbols
   - Ensured all documents produce clean UTF-8 text
4. **Chunked Documents**
   - Split processed text into chunks of max 500 words
   - Ensured chunks are clean and non-empty
   - Prepared them for embedding and vector storage
5. **Assigned Role-Based Metadata**
   - Every chunk received:
     - Unique ID
     - Cleaned text
     - Source document name
     - Department (derived from folder path)
     - allowed roles (based on role-to-document mapping)




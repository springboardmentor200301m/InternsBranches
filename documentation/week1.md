# 📘 Week 1 Documentation

## Environment Setup & Data Exploration

**Project:** Company Internal Chatbot with Role-Based Access Control (RBAC) and Retrieval-Augmented Generation (RAG)

---

## 1. Overview

Week 1 focuses on establishing the **foundational infrastructure** for the project. The objective is to set up a stable development environment, explore the provided company documents, understand their structure and sensitivity, and define a **clear role-to-document access strategy**.

This week does **not** involve any machine learning or LLM integration. Instead, it ensures that all subsequent components (vector database, RBAC, RAG, and frontend) are built on **well-understood and well-organized data**.

---

## 2. Objectives

The primary objectives of Week 1 are:

* Set up a reproducible Python development environment
* Clone and organize company documents locally
* Explore and understand document formats and content
* Identify sensitive vs non-sensitive data
* Define role-based document access rules
* Establish a clear data directory structure for the project

---

## 3. Development Environment Setup

### 3.1 Python Environment

A dedicated Python virtual environment is created to isolate dependencies and ensure reproducibility.

* **Python Version:** 3.8+
* **Virtual Environment Tool:** `venv`

```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

---

### 3.2 Dependency Installation

Core libraries required for data exploration and later stages are installed.

```bash
pip install fastapi streamlit langchain
pip install sentence-transformers chromadb
pip install pandas numpy
pip install python-dotenv
```

These dependencies support:

* Backend API development
* Frontend UI development
* Embedding generation
* Vector database operations
* CSV and text document processing

---

## 4. Project Directory Structure

A clean and scalable directory structure is established early to avoid refactoring later.

```
company-chatbot/
│
├── app/                    # Backend application (FastAPI)
├── frontend/               # Streamlit frontend
├── data/
│   ├── raw/                # Original documents (markdown, csv)
│   └── processed/          # Chunked and cleaned documents
├── scripts/                # Data exploration and preprocessing scripts
├── venv/                   # Virtual environment
├── .env                    # Environment variables
└── README.md
```

This separation ensures:

* Raw data remains untouched
* Processed data is reproducible
* Backend and frontend remain decoupled

---

## 5. Data Source Exploration

### 5.1 Document Types

The provided dataset contains **department-specific company documents**, organized into folders.

| Department  | Format   | Description                            |
| ----------- | -------- | -------------------------------------- |
| Finance     | Markdown | Financial summaries, quarterly reports |
| Marketing   | Markdown | Campaign and market analysis reports   |
| Engineering | Markdown | Technical architecture and processes   |
| HR          | CSV      | Employee records and HR data           |
| General     | Markdown | Employee handbook and policies         |

---

### 5.2 Markdown Documents

Markdown files are semi-structured and include:

* Headings (`#`, `##`)
* Tables
* Bullet points
* Sections with contextual meaning

These are suitable for:

* Chunk-based semantic retrieval
* Contextual RAG usage

---

### 5.3 HR CSV Dataset (Sensitive Data)

The HR dataset contains **highly sensitive fields**, including:

* Employee salary
* Performance ratings
* Attendance
* Personal identifiers

Because of this:

* Row-level access control is required
* Only authorized roles (HR, C-Level) should access this data
* Raw CSV rows must never be exposed directly to unauthorized users

---

## 6. Data Exploration Script

A custom exploration script is implemented to:

* Traverse all data directories
* Identify file types
* Preview content safely
* Count files per department

### Purpose:

* Validate dataset completeness
* Detect inconsistencies early
* Understand chunking requirements

Example output includes:

* Department-wise file counts
* Column names for CSV
* Content previews for markdown files

---

## 7. Role-Based Access Mapping

A **strict role-to-document mapping** is defined during Week 1.

### 7.1 Defined Roles

* Employee
* Finance
* Marketing
* HR
* Engineering
* C-Level

---

### 7.2 Role-to-Document Access Rules

| Role        | Allowed Documents         |
| ----------- | ------------------------- |
| Employee    | General employee handbook |
| Finance     | Finance + General         |
| Marketing   | Marketing + General       |
| Engineering | Engineering + General     |
| HR          | HR + General              |
| C-Level     | All documents             |

Key design decision:

> **Access rules are strict by default**, with flexibility to expand permissions later if required.

---

## 8. Key Design Decisions (Week 1)

1. **Strict RBAC Model**

   * Prevents accidental data leakage
   * Easier to relax later than tighten

2. **Separation of Raw and Processed Data**

   * Enables reproducibility
   * Prevents corruption of original documents

3. **HR CSV Treated as Sensitive Source**

   * Requires special handling in later stages
   * Influences chunking and filtering logic

4. **No LLM Dependency in Early Stage**

   * Focus on correctness before intelligence

---

## 9. Validation & Checks

The following validations are completed in Week 1:

* All departments detected correctly
* All files readable without encoding errors
* HR CSV schema verified
* No missing or malformed documents
* Role-to-document mapping reviewed and approved

---

## 10. Deliverables (Week 1)

* Configured Python environment
* Organized project directory structure
* Data exploration script
* Document inventory summary
* Role-based access mapping definition
* Week 1 documentation

---

## 11. Outcome of Week 1

At the end of Week 1:

* The data landscape is fully understood
* Security boundaries are clearly defined
* The project is ready for preprocessing, chunking, and vectorization

This foundation enables **safe and scalable development** in subsequent weeks.
---

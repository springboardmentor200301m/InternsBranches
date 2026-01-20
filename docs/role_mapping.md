# Role → Document Mapping

This document defines how company documents from the Fintech-data repository are mapped to user roles for Role-Based Access Control (RBAC) and Retrieval-Augmented Generation (RAG).

This mapping follows the project specifications from Milestone 1.

---

## 1. Department Classification Rules

Documents are assigned to departments based on their content and purpose.

### **Finance**
Includes documents related to:
- quarterly or annual reports  
- financial summaries  
- balance sheets  
- income statements  
- revenue or cashflow data  

### **Marketing**
Includes documents related to:
- marketing strategy  
- market research  
- customer segmentation  
- brand performance  
- campaign reports  

### **HR (Human Resources)**
Includes documents related to:
- employee handbook  
- HR policies  
- salary/payroll structure  
- recruitment/hiring processes  
- employee-related data  

### **Engineering**
Includes documents related to:
- technical architecture  
- API documentation  
- engineering workflows  
- deployment guides  
- system design or processes  

### **General / Employees**
Includes company-wide documents such as:
- general policies  
- company handbook  
- security guidelines  
- code of conduct  
- company overview  

### **C-Level**
Has access to **all documents** across all departments.

---

## 2. Role Access Rules

| Role          | Allowed Access                                         |
|---------------|---------------------------------------------------------|
| Finance       | Finance + General documents                             |
| Marketing     | Marketing + General documents                           |
| HR            | HR + General documents                                  |
| Engineering   | Engineering + General documents                         |
| Employees     | General documents only                                  |
| C-Level       | All departments                                         |

These rules will be applied during vector database search and RAG retrieval in later milestones.

---

## 3. Folder-to-Role Mapping (High-Level)

| Folder / Category in Repository | Assigned Role      |
|---------------------------------|--------------------|
| `Finance/`                      | Finance            |
| `Marketing/`                    | Marketing          |
| `HR/`                           | HR                 |
| `Engineering/`                  | Engineering        |
| `General/`                      | Employees / General |
| *All folders*                   | C-Level (full access) |

This mapping is used during preprocessing to attach metadata to each document chunk.

---

## 4. Override Notes

If any document’s **content** does not match the department indicated by its **folder name**, it should be reassigned to the correct department here.



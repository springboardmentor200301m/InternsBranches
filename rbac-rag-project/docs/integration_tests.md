# Integration Test Suite – RBAC RAG System

## Test Case 1: Finance Role – Financial Query
- Role: Finance
- Query: What is the Q2 revenue?
- Expected Result: Financial data returned
- Actual Result: $2.3B revenue returned
- Status: PASS

## Test Case 2: Employee Role – Financial Query
- Role: Employee
- Query: What is the Q2 revenue?
- Expected Result: Access denied
- Actual Result: No information available
- Status: PASS

## Test Case 3: Admin Role – Cross-Department Query
- Role: Admin
- Query: Describe overall financial performance
- Expected Result: Multi-source response
- Actual Result: Correct summary returned
- Status: PASS

## Test Case 4: HR Role – Employee Data
- Role: HR
- Query: What benefits are provided to employees?
- Expected Result: Only HR-accessible data
- Actual Result: Information not available
- Status: PASS

## Test Case 5: No Context Case
- Role: Employee
- Query: What is Kubernetes?
- Expected Result: LLM not called
- Actual Result: Safe message displayed
- Status: PASS

from document_loader import load_documents_with_roles, filter_docs_by_user

docs = load_documents_with_roles("data")

user = "priya"   # change this to test other users

filtered_docs = filter_docs_by_user(user, docs)

print(f"\nAccessible documents for user: {user}\n")

for d in filtered_docs:
    print("SOURCE:", d.metadata["source"])
    print("ROLE:", d.metadata["role"])
    print("-" * 40)

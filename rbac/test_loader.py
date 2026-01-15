from document_loader import load_documents_with_roles, filter_docs_by_user

docs = load_documents_with_roles("data")

user = "priya"   # change user to test
filtered_docs = filter_docs_by_user(user, docs)

print(f"\nAccessible documents for {user}:")
for d in filtered_docs:
    print(d.metadata["source"], "→", d.metadata["role"])

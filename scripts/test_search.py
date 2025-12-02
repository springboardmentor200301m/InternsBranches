from app.search import semantic_search

TEST_QUERIES = [
    ("Show me information about employee salaries", "finance"),
    ("Show me information about employee salaries", "employee"),
    ("What are the marketing results for Q4 2024?", "marketing"),
    ("Explain our engineering architecture", "engineering"),
    ("Summarize HR performance ratings", "hr"),
    ("Summarize HR performance ratings", "employee"),
    ("Give me an overview of company policies", "employee"),
    ("Give me an overview of company policies", "c_level"),
]


def print_results(query: str, role: str):
    print("=" * 80)
    print(f"Query: {query}")
    print(f"Role:  {role}")
    print("-" * 80)

    hits = semantic_search(query, role, top_k=3)

    if not hits:
        print("No results (possibly blocked by RBAC).")
        return

    for i, hit in enumerate(hits, start=1):
        meta = hit["metadata"]
        print(f"[{i}] score={hit['score']:.4f}")
        print(f"    id:        {hit['id']}")
        print(f"    department:{meta.get('department')}")
        print(f"    source:    {meta.get('source_file')}")
        print(f"    roles:     {meta.get('allowed_roles')}")
        snippet = hit["text"][:200].replace("\n", " ")
        print(f"    text:      {snippet}...")
        print()


if __name__ == "__main__":
    for q, r in TEST_QUERIES:
        print_results(q, r)

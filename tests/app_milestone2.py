from search.semantic_search import semantic_search


def print_results(results):
    if isinstance(results, dict):
        print(results.get("message") or results.get("error"))
        return

    for i, r in enumerate(results, start=1):
        print(f"\nResult {i}")
        print(f"Source     : {r['source']}")
        print(f"Department : {r['department']}")
        print("Content:")
        print(r["text"][:500] + ("..." if len(r["text"]) > 500 else ""))


if __name__ == "__main__":
    query = input("Enter query: ")
    role = input(
        "Enter role (finance/hr/engineering/marketing/employees/c_level): "
    )

    results = semantic_search(query, role)
    print_results(results)

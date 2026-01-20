from search.semantic_search import semantic_search

def test_finance_access():
    res = semantic_search("salary policy", "finance")
    assert all("hr" not in r["department"] for r in res)

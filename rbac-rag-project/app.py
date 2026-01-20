import json
from pathlib import Path
import streamlit as st


BASE_DIR = Path(__file__).parent
PROCESSED_DIR = BASE_DIR / "processed"


def load_jsonl(path: Path, limit: int | None = None):
    items = []
    if not path.exists():
        return items
    with path.open("r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            try:
                obj = json.loads(line)
                items.append(obj)
            except json.JSONDecodeError:
                continue
            if limit and i + 1 >= limit:
                break
    return items


def load_json(path: Path):
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def main():
    st.set_page_config(page_title="RBAC RAG Viewer", layout="wide")
    st.title("RBAC RAG Project — Streamlit Viewer")

    st.sidebar.header("Data Sources")
    chunks_file = PROCESSED_DIR / "chunks.jsonl"
    tagged_file = PROCESSED_DIR / "chunks_tagged.jsonl"
    qa_summary_file = PROCESSED_DIR / "qa_summary.json"

    data_choice = st.sidebar.selectbox(
        "Select dataset",
        (
            "Chunks",
            "Chunks (Tagged)",
            "QA Summary",
        ),
    )

    st.sidebar.markdown("---")
    limit = st.sidebar.number_input("Row limit (preview)", min_value=10, value=200, step=10)
    search_query = st.sidebar.text_input("Filter by text")

    if data_choice == "Chunks":
        st.subheader("Processed Chunks")
        rows = load_jsonl(chunks_file, limit=limit)
        if search_query:
            q = search_query.lower()
            rows = [r for r in rows if q in json.dumps(r).lower()]
        st.write(f"Showing {len(rows)} rows from {chunks_file.name}")
        for r in rows:
            with st.expander(r.get("source", "(unknown source)")):
                st.markdown(f"**Document:** {r.get('document_path', '')}")
                st.markdown(f"**Chunk ID:** {r.get('chunk_id', '')}")
                st.code(r.get("content", ""))

    elif data_choice == "Chunks (Tagged)":
        st.subheader("Tagged Chunks")
        rows = load_jsonl(tagged_file, limit=limit)
        if search_query:
            q = search_query.lower()
            rows = [r for r in rows if q in json.dumps(r).lower()]
        st.write(f"Showing {len(rows)} rows from {tagged_file.name}")
        for r in rows:
            with st.expander(r.get("source", "(unknown source)")):
                st.markdown(f"**Tags:** {', '.join(r.get('tags', []))}")
                st.markdown(f"**Document:** {r.get('document_path', '')}")
                st.markdown(f"**Chunk ID:** {r.get('chunk_id', '')}")
                st.code(r.get("content", ""))

    else:
        st.subheader("QA Summary")
        qa = load_json(qa_summary_file)
        if not qa:
            st.info("No QA summary found.")
            return

        items = qa if isinstance(qa, list) else qa.get("items", [])
        if search_query:
            q = search_query.lower()
            items = [r for r in items if q in json.dumps(r).lower()]
        st.write(f"Showing {len(items)} entries from {qa_summary_file.name}")

        for i, entry in enumerate(items, start=1):
            question = entry.get("question", f"Question {i}")
            with st.expander(question):
                st.markdown(f"**Answer:**\n\n{entry.get('answer', '')}")
                meta = entry.get("metadata", {})
                if meta:
                    st.markdown("**Metadata:**")
                    st.json(meta)


if __name__ == "__main__":
    main()

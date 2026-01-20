import re


def clean_context_text(text: str) -> str:
    lines = text.splitlines()
    cleaned = []

    for line in lines:
        l = line.strip()

        # Skip empty lines
        if not l:
            continue

        # Skip table separator rows
        if set(l) <= {"-", "|"}:
            continue

        # ❌ REMOVE table header rows COMPLETELY
        if "|" in l and any(word in l.lower() for word in ["benefit", "component", "details"]):
            continue

        # Remove markdown headers
        l = re.sub(r"^#+\s*", "", l)

        # Remove markdown emphasis
        l = re.sub(r"\*\*", "", l)
        l = re.sub(r"\*", "", l)

        cleaned.append(l)

    return "\n".join(cleaned).strip()
def build_context(chunks, top_k=3):
    context_parts = []
    selected = []

    for c in chunks:
        cleaned_text = clean_context_text(c["text"][:800])

        # ❗ Skip chunks that have no real content
        if len(cleaned_text.split()) < 8:
            continue

        context_parts.append(
            f"[Source: {c['source_file']}]\n{cleaned_text}"
        )
        selected.append(c)

        if len(selected) >= top_k:
            break

    return "\n\n".join(context_parts), selected


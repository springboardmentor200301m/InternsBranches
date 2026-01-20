"""
Task 5: Define RAG Input and Output

This file defines the INPUT and OUTPUT contract for a
Retrieval-Augmented Generation (RAG) system.

✔ No real LLM is called here
✔ RBAC-safe (only authorized context is passed)
✔ Used later during Milestone-3 LLM integration
"""

from typing import List, Dict


class RAGInput:
    """
    Represents the input sent to the LLM in a RAG pipeline.
    """

    def __init__(self, query: str, context_chunks: List[str], sources: List[Dict]):
        self.query = query
        self.context_chunks = context_chunks
        self.sources = sources

    def to_prompt(self) -> str:
        """
        Builds the final prompt to be sent to the LLM.
        """
        context_text = "\n\n".join(self.context_chunks)

        prompt = f"""
You are an assistant answering questions strictly using company documents.

QUESTION:
{self.query}

CONTEXT:
{context_text}

Answer the question using ONLY the above context.
"""
        return prompt.strip()


class RAGOutput:
    """
    Represents the final response produced by the LLM.
    """

    def __init__(self, answer: str, sources: List[Dict]):
        self.answer = answer
        self.sources = sources

    def display(self):
        """
        Displays the answer along with source attribution.
        """
        print("\n🧠 Answer:\n")
        print(self.answer)

        print("\n📚 Sources:")
        for src in self.sources:
            print(
                f"- {src.get('document_name')} "
                f"(Department: {src.get('department')})"
            )


# --------------------------------------------------
# Demo Run (for verification of Task 5)
# --------------------------------------------------
if __name__ == "__main__":
    # Sample query
    query = "What is the leave policy?"

    # Retrieved & RBAC-filtered document chunks
    context_chunks = [
        "Employees are entitled to 24 annual leaves per year.",
        "Unused leaves can be carried forward to the next year."
    ]

    # Source metadata
    sources = [
        {"document_name": "employee_handbook.md", "department": "General"}
    ]

    # Create RAG input
    rag_input = RAGInput(
        query=query,
        context_chunks=context_chunks,
        sources=sources
    )

    print("\n📥 RAG INPUT PROMPT:\n")
    print(rag_input.to_prompt())

    # Mock RAG output (LLM response)
    rag_output = RAGOutput(
        answer=(
            "Employees are entitled to 24 annual leaves per year. "
            "Unused leaves can be carried forward as per company policy."
        ),
        sources=sources
    )

    print("\n📤 RAG OUTPUT:\n")
    rag_output.display()

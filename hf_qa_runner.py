'''
from transformers import pipeline


class HuggingFaceQARunner:
    def __init__(self):
        self.qa = pipeline(
            "question-answering",
            model="deepset/roberta-base-squad2"
        )

    def generate(self, question, context):
        result = self.qa(
            question=question,
            context=context
        )
        return result.get("answer")
'''















from transformers import pipeline

class HuggingFaceQARunner:
    def __init__(self):
        self.qa = pipeline(
            task="question-answering",
            model="deepset/roberta-base-squad2",
            tokenizer="deepset/roberta-base-squad2"
        )

    def generate(self, question: str, context: str) -> str:
        if not context.strip():
            return "No relevant information available in the provided context."

        result = self.qa(
            question=question,
            context=context
        )

        answer = result.get("answer", "").strip()

        if not answer:
            return "The answer is not available in the provided context."

        return answer

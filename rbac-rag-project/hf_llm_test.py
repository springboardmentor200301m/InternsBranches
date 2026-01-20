from transformers import pipeline

# Correct pipeline for FLAN-T5
generator = pipeline(
    "text2text-generation",
    model="google/flan-t5-small",
    max_new_tokens=120
)

prompt = "Answer in 3–4 lines.\n" "Answer clearly: What is Retrieval Augmented Generation?"


result = generator(prompt)

print(result[0]["generated_text"])

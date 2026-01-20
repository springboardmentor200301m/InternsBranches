from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# Load tokenizer and model
model_name = "google/flan-t5-base"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

# Simple prompt
prompt = "Answer only if you are sure using company documents: What is the leave policy?"

# Tokenize
inputs = tokenizer(prompt, return_tensors="pt")

# Generate output
outputs = model.generate(
    **inputs,
    max_new_tokens=100
)
 
# Decode and print
response = tokenizer.decode(outputs[0], skip_special_tokens=True)

print("\n🔹 Prompt:")
print(prompt)

print("\n🔹 LLM Response:")
print(response)

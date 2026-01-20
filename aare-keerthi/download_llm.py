from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import os

model_name = "google/flan-t5-small"
save_path = os.path.join("models", "flan-t5-small")

os.makedirs(save_path, exist_ok=True)

print("⬇️ Downloading model...")

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

tokenizer.save_pretrained(save_path)
model.save_pretrained(save_path)

print("✅ Model downloaded to:", save_path)

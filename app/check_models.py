import os
import google.generativeai as genai
from dotenv import load_dotenv

# 1. Load the API Key
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ Error: GOOGLE_API_KEY not found in .env file.")
    exit()

# 2. Configure Google AI
genai.configure(api_key=api_key)

print(f"✅ Authenticated with API Key. Fetching available models...\n")

# 3. List all models
try:
    print(f"{'MODEL NAME':<30} | {'SUPPORTED METHODS'}")
    print("-" * 60)
    
    for m in genai.list_models():
        # We only care about models that can "generateContent" (Chat)
        if 'generateContent' in m.supported_generation_methods:
            print(f"{m.name:<30} | {m.supported_generation_methods}")

except Exception as e:
    print(f"❌ Error fetching models: {e}")
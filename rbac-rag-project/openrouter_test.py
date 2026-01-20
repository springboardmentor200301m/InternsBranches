from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize client
client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    default_headers={
        "HTTP-Referer": "http://localhost:8501",  # Or your Streamlit URL if deployed
        "X-Title": "Company Internal RBAC Chatbot"
    }
)

def query_llm(prompt: str, system_prompt: str = "You are a helpful and accurate assistant.") -> str:
    """
    Send a query to the LLM via OpenRouter and return the response.
    """
    try:
        response = client.chat.completions.create(
            model="meta-llama/llama-3.1-8b-instruct",  # Or try "meta-llama/llama-3.1-70b-instruct" if you want even better!
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.3,  # Keep low for reliable answers
            top_p=0.9
        )
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        return f"Error: {str(e)}"

# Test it
if __name__ == "__main__":
    print("Sending test request to OpenRouter...\n")
    
    answer = query_llm("Explain Retrieval Augmented Generation in simple words.")
    
    print("Final Answer:\n", answer)
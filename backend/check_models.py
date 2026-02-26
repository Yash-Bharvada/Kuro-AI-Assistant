import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("Error: GOOGLE_API_KEY not found in environment")
    exit(1)

genai.configure(api_key=api_key)

print("Listing available models...")
with open("models.txt", "w") as f:
    try:
        for m in genai.list_models():
            if 'embedContent' in m.supported_generation_methods:
                f.write(f"Embedding Model: {m.name}\n")
            elif 'generateContent' in m.supported_generation_methods:
                f.write(f"Generative Model: {m.name}\n")
    except Exception as e:
        f.write(f"Error listing models: {e}\n")

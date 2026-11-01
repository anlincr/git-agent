import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

candidates = [
    "gemini-3.8-flash",
    "gemini-3.8-pro",
    "gemini-3.5-flash",
    "gemini-flash-latest",
    "gemini-2.5-flash-lite",
]

for name in candidates:
    try:
        r = client.models.generate_content(model=name, contents="Say hi in 3 words.")
        print(f"WORKS: {name} -> {r.text.strip()}")
    except Exception as e:
        print(f"FAIL:  {name} -> {str(e)[:100]}")
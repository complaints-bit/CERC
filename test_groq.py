import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
print(f"API Key found: {api_key[:5]}...{api_key[-5:] if api_key else 'None'}")

if not api_key:
    print("❌ No API Key found in .env")
    exit()

try:
    client = Groq(api_key=api_key)
    print("✅ Client initialized")

    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "user", "content": "Hello, is this working?"}
        ],
        model="llama-3.3-70b-versatile",
    )

    print("✅ Response received:")
    print(chat_completion.choices[0].message.content)

except Exception as e:
    print(f"❌ Error caught: {e}")
    import traceback
    traceback.print_exc()

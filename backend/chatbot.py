import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

# Initialize Gemini client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def generate_response(query: str, context: str) -> str:
    prompt = f"""
You are a helpful assistant. Use the following context from a website to answer the user's query.
If the answer is not present in the context, use your own general knowledge.

Context:
\"\"\"{context}\"\"\"

User: {query}
Assistant:
"""

    contents = [
        types.Content(
            role="user",
            parts=[types.Part(text=prompt)],  # ✅ FIXED
        )
    ]

    config = types.GenerateContentConfig(response_mime_type="text/plain")

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=contents,
            config=config,
        )
        return response.candidates[0].content.parts[0].text.strip()
    except Exception as e:
        return f"Error generating response: {str(e)}"

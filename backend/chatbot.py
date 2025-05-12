# backend/chatbot.py

import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def generate_response(query: str, context: str) -> str:
    prompt = f"""
    You are a helpful assistant. Use the following context to answer the user's query.

    Context:
    {context}

    User: {query}
    Assistant:
    """

    model = "gemini-2.0-flash-lite"
    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=prompt)],
        )
    ]

    config = types.GenerateContentConfig(response_mime_type="text/plain")
    response = client.models.generate_content(model=model, contents=contents, config=config)

    return response.text.strip()

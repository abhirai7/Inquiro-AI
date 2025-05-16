import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

# Initialize Gemini client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def generate_response(query: str, context: str) -> str:
    """
    Uses direct prompting with Gemini API to answer the query based on full context.

    Args:
        query (str): The user's question.
        context (str): The full content text from the website.

    Returns:
        str: Assistant's response.
    """
    prompt = f"""
You are a helpful assistant. Use the following context from a website to answer the user's query.

Context:
{context}

User: {query}
Assistant:
"""

    model = "gemini-2.0-flash"  # You can update this as needed
    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=prompt)],
        )
    ]

    config = types.GenerateContentConfig(response_mime_type="text/plain")

    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=config,
    )

    return response.text.strip()

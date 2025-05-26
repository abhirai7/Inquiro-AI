import os
from dotenv import load_dotenv
from google.genai import Client
from google.genai import types

load_dotenv()

# Initialize Gemini client
client = Client(api_key=os.getenv("GEMINI_API_KEY"))


def generate_response(context: str, query: str, history: list = None) -> str:
    history_text = ""
    if history:
        for h in history[-5:]:  # Last 5 interactions
            history_text += f"User: {h['query']}\nAssistant: {h['response']}\n"
    prompt = f"""
You are a helpful assistant. Use the following context from a website to answer the user's query.
If the answer is not present in the context, use your own general knowledge.
The context is the scraped data from url. Use this to answer the user's queries.
Determine the main topic, important points, and any relevant details from the context.
Context:
\"\"\"{context}\"\"\"


Recent conversation history:
\"\"\"{history_text}\"\"\"

User: {query}
Assistant:
"""

    contents = [
        types.Content(role="user", parts=[types.Part(text=prompt)])
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

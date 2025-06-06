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
You can also use the conversation history to provide a more relevant answer.
You may look up the website if needed, if the context is not sufficient.
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


def clean_text(text: str) -> str:
    """
    Cleans the text by removing excessive whitespace and ensuring proper formatting.
    """
    prompt = f"""
Please clean the following text by removing excessive whitespace, ensuring proper formatting, and making it more readable and make it suitable for use in a chatbot response.
Example: Make it more readable, remove unnecessary spaces, and ensure it is well-structured. Headings should be clear, paragraphs should be well-formed, and the text should be concise.
Heading
    -content
    -subheading
        -content
        -sub-subheading
            content

            <sub-subheading>
                content
            </sub-subheading>
    Also, generate other valuable content that is relevant to the topic even if it is not present in the text.
    Get All the neccessary details about the topic and everything mentioned in the text.
\"\"\"{text}\"\"\" 
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
        return f"Error cleaning text: {str(e)}"
    
    
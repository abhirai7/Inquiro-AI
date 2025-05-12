### backend/embedder.py

import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

# Initialize Gemini client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def generate_embeddings(text: str):
    model = "models/embedding-001"  # Gemini embedding model

    response = client.embeddings.generate(
        model=model,
        content=text
    )

    return response.embedding.values

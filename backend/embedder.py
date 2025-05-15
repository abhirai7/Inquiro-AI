from sentence_transformers import SentenceTransformer
import numpy as np

# Load the pre-trained SentenceTransformer model
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def generate_embeddings(text: str) -> np.ndarray:
    """
    Generate a 384-dimensional embedding for the given text using the all-MiniLM-L6-v2 model.

    Args:
        text (str): The input text to be embedded.

    Returns:
        np.ndarray: The embedding vector representing the input text.
    """
    # Encode the text into an embedding
    embedding = model.encode(text)
    return embedding

import os
import numpy as np
import pickle
from sklearn.metrics.pairwise import cosine_similarity

# Directory to store vector data
VECTOR_DIR = "data/vectors"
os.makedirs(VECTOR_DIR, exist_ok=True)


def save_embeddings(domain: str, embedding: np.ndarray, text: str):
    """
    Saves the embedding and associated text to disk.

    Args:
        domain (str): The website domain.
        embedding (np.ndarray): The vector embedding.
        text (str): The associated content text.
    """
    domain_name = domain.split("//")[-1].split("/")[0]
    vector_path = os.path.join(VECTOR_DIR, f"{domain_name}_embedding.npy")
    text_path = os.path.join(VECTOR_DIR, f"{domain_name}_text.pkl")

    np.save(vector_path, embedding)

    with open(text_path, "wb") as f:
        pickle.dump(text, f)


def search_embeddings(domain: str, query_embedding: np.ndarray, top_k: int = 1):
    """
    Searches for the most similar document using cosine similarity.

    Args:
        domain (str): The website domain.
        query_embedding (np.ndarray): The embedding for the user's query.
        top_k (int): Number of top results to return.

    Returns:
        list: Most similar text(s).
    """
    domain_name = domain.split("//")[-1].split("/")[0]
    vector_path = os.path.join(VECTOR_DIR, f"{domain_name}_embedding.npy")
    text_path = os.path.join(VECTOR_DIR, f"{domain_name}_text.pkl")

    if not os.path.exists(vector_path) or not os.path.exists(text_path):
        return []

    stored_embedding = np.load(vector_path)
    similarity = cosine_similarity([query_embedding], [stored_embedding])[0][0]

    with open(text_path, "rb") as f:
        text = pickle.load(f)

    return [text] if similarity > 0 else []

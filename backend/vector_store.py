### backend/vector_store.py

import faiss
import os
import numpy as np
import pickle

# Directory to store vector data
VECTOR_DIR = "data/vectors"
os.makedirs(VECTOR_DIR, exist_ok=True)

def save_embeddings(domain: str, embeddings: list, text: str):
    domain_name = domain.split("//")[-1].split("/")[0]
    vector_path = os.path.join(VECTOR_DIR, f"{domain_name}_index.faiss")
    text_path = os.path.join(VECTOR_DIR, f"{domain_name}_texts.pkl")

    # Create FAISS index
    dim = len(embeddings)
    index = faiss.IndexFlatL2(dim)
    index.add(np.array([embeddings], dtype="float32"))
    faiss.write_index(index, vector_path)

    # Save associated text
    with open(text_path, "wb") as f:
        pickle.dump([text], f)


def search_embeddings(domain: str, query_embedding: list, top_k: int = 1):
    domain_name = domain.split("//")[-1].split("/")[0]
    vector_path = os.path.join(VECTOR_DIR, f"{domain_name}_index.faiss")
    text_path = os.path.join(VECTOR_DIR, f"{domain_name}_texts.pkl")

    if not os.path.exists(vector_path) or not os.path.exists(text_path):
        return []

    index = faiss.read_index(vector_path)
    D, I = index.search(np.array([query_embedding], dtype="float32"), top_k)

    with open(text_path, "rb") as f:
        texts = pickle.load(f)

    return [texts[i] for i in I[0] if i < len(texts)]

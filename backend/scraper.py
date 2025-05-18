# backend/scraper.py
import requests
from bs4 import BeautifulSoup
import numpy as np
from sentence_transformers import SentenceTransformer
from urllib.parse import urlparse

from .vector_store import save_embeddings

model = SentenceTransformer("all-MiniLM-L6-v2")

def scrape_website(url: str):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        for tag in soup(['script', 'style', 'noscript']):
            tag.decompose()

        text = soup.get_text(separator=' ', strip=True)
    
        return text

        # Extract main text content
        paragraphs = soup.find_all("p")
        content = "\n".join(p.get_text() for p in paragraphs).strip()

        if not content:
            raise ValueError("No content extracted from website.")

        # Generate embedding
        embedding = model.encode(content)

        # Save to vector store
        domain = urlparse(url).netloc
        save_embeddings(domain, np.array(embedding), content)

        
        return True

    except Exception as e:
        print(f"[Scraper Error] {e}")
        return ""

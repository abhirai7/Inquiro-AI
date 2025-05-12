# backend/scraper.py

import requests
from bs4 import BeautifulSoup

def scrape_website(url: str) -> str:
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Remove script and style elements
        for tag in soup(['script', 'style', 'noscript']):
            tag.decompose()
        # Get visible text
        text = soup.get_text(separator=' ', strip=True)
        return text

    except requests.RequestException as e:
        print(f"Error scraping {url}: {e}")
        return ""

# backend/scraper.py
from playwright.sync_api import sync_playwright
import re

from .vector_store import save_embeddings


def scrape_website(url: str) -> str:
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=60000, wait_until="networkidle")  # Wait for JS to load

            # Get full rendered page content
            html = page.content()
            browser.close()

        # Use BeautifulSoup to clean up the rendered HTML
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")

        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        text = soup.get_text(separator=" ", strip=True)

        # Optional: clean up multiple spaces
        text = re.sub(r"\s+", " ", text)

        return text

    except Exception as e:
        print(f"[Playwright Scraper Error] {e}")
        return ""

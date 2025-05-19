# backend/scraper.py

import os
import re
import hashlib
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

from .vector_store import save_embeddings


async def scrape_website(url: str) -> bool:
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, timeout=60000, wait_until="networkidle")
            html = await page.content()
            await browser.close()

        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        text = soup.get_text(separator=" ", strip=True)
        text = re.sub(r"\s+", " ", text)

        # Save cleaned text
        hashed = hashlib.md5(url.encode()).hexdigest()
        os.makedirs("data/texts", exist_ok=True)
        with open(f"data/texts/{hashed}.txt", "w", encoding="utf-8") as f:
            f.write(text)

        # Save embeddings
        save_embeddings(text, url)

        print(f"[Scraper] Text saved for {url}")
        return True

    except Exception as e:
        print(f"[Scraper Error] {e}")
        return False

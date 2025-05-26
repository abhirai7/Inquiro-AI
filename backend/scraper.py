# backend/scraper.py

import os
import re
import hashlib
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
import requests
from .vector_store import save_embeddings



def scrape_with_bs4(url: str) -> bool:
    try:
        print(f"[Fallback Scraper] Scraping with bs4: {url}")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            print(f"[Fallback Scraper Error] Failed to fetch page: Status code {response.status_code}")
            return False

        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        text = soup.get_text(separator=" ", strip=True)
        text = re.sub(r"\s+", " ", text)

        print(f"[Fallback Scraper] Text length: {len(text)}")
        print(f"[Fallback Preview] {text[:500]}...")

        # Save text
        hashed = hashlib.md5(url.encode()).hexdigest()
        os.makedirs("data/texts", exist_ok=True)
        with open(f"data/texts/{hashed}.txt", "w", encoding="utf-8") as f:
            f.write(text)

        # Save embeddings
        save_embeddings(text, url)

        print(f"[Fallback Scraper] Text and embeddings saved for {url}")
        return True

    except Exception as e:
        print(f"[Fallback Scraper Error] {e}")
        return False

async def scrape_website(url: str) -> bool:
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, timeout=60000, wait_until="networkidle")

            # Optional: Wait additional time for JavaScript content
            await page.wait_for_timeout(3000)

            # Optional: Scroll to trigger lazy loading (LeetCode uses this)
            for _ in range(3):
                await page.evaluate("window.scrollBy(0, window.innerHeight);")
                await page.wait_for_timeout(1000)

            html = await page.content()
            await browser.close()

        # Clean and parse HTML
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        text = soup.get_text(separator=" ", strip=True)
        text = re.sub(r"\s+", " ", text)

        # Debug info
        print(f"[Scraper] Text length: {len(text)}")
        print(f"[Scraper Preview] {text[:500]}...")  # Preview scraped content

        # Save text
        hashed = hashlib.md5(url.encode()).hexdigest()
        os.makedirs("data/texts", exist_ok=True)
        with open(f"data/texts/{hashed}.txt", "w", encoding="utf-8") as f:
            f.write(text)

        # Save embeddings
        save_embeddings(text, url)

        print(f"[Scraper] Text and embeddings saved for {url}")
        return True

    except Exception as e:
        print(f"[Scraper Error] {e}")
        print("[Scraper] Trying fallback with BeautifulSoup...")
        return scrape_with_bs4(url)


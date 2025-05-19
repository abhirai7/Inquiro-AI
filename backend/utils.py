# backend/utils.py (or inline in main if preferred)
import os
import hashlib

def load_scraped_text(url: str) -> str:
    hashed = hashlib.md5(url.encode()).hexdigest()
    path = f"data/texts/{hashed}.txt"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

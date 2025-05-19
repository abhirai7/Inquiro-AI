# backend/chat_history.py

import json
import os
from datetime import datetime

HISTORY_FILE = "data/chat_history.json"

def save_to_history(query: str, context: str, response: str):
    os.makedirs("data", exist_ok=True)

    history = []
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            history = json.load(f)

    history.append({
        "timestamp": datetime.now().isoformat(),
        "query": query,
        "context_snippet": context[:300],
        "response": response
    })

    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

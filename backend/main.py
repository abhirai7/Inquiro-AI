# backend/main.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.scraper  import scrape_website
from backend.chatbot import generate_response
import os

app = FastAPI()

from fastapi.responses import FileResponse
@app.get("/")
def read_root():
    return FileResponse("frontend/index.html")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class URLRequest(BaseModel):
    url: str

class QueryRequest(BaseModel):
    url: str
    query: str

@app.post("/scrape")
def scrape_and_save(data: URLRequest):
    text = scrape_website(data.url)
    if not text:
        raise HTTPException(status_code=400, detail="Failed to scrape content")

    # Save text to a file
    os.makedirs("data/scraped", exist_ok=True)
    domain = data.url.split("//")[-1].split("/")[0]
    filepath = f"data/scraped/{domain}.txt"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(text)

    return {"message": "Content scraped and saved successfully."}

@app.post("/ask")
def ask_bot(data: QueryRequest):
    filepath = f"data/scraped/{data.url.split('//')[-1].split('/')[0]}.txt"
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Scraped content not found")

    with open(filepath, "r", encoding="utf-8") as f:
        context = f.read()

    answer = generate_response(data.query, context)
    return {"response": answer}

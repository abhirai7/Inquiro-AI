from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, HttpUrl, ValidationError
from urllib.parse import urlparse
import logging
import hashlib
import os
import shutil

from .scraper import scrape_website
from .chatbot import generate_response as get_bot_response

app = FastAPI()

# Serve static files for widget
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging
logging.basicConfig(level=logging.INFO)

# Schemas
class ScrapeRequest(BaseModel):
    url: HttpUrl

class AskRequest(BaseModel):
    url: HttpUrl
    query: str

# Utility functions
def get_url_hash(url):
    return hashlib.md5(url.encode()).hexdigest()

def get_data_path(url):
    return f"data/vectors/{get_url_hash(url)}.pkl"

def already_scraped(url):
    return os.path.exists(get_data_path(url))

# Routes

@app.get("/")
async def root():
    # Serve the actual HTML file as the root response
    return FileResponse("frontend/index.html", media_type="text/html")

@app.post("/scrape")
async def scrape(request: Request):
    try:
        body = await request.json()
        data = ScrapeRequest(**body)
        logging.info(f"Scraping: {data.url}")

        if already_scraped(str(data.url)):
            return {"message": f"Already scraped: {data.url}"}

        success = scrape_website(str(data.url))
        print(f"Scraping result: {success}")
        if not success:
            return JSONResponse(status_code=500, content={"error": "Scraping or embedding failed."})

        return {"message": f"Scraping completed for {data.url}"}
    except ValidationError:
        return JSONResponse(status_code=400, content={"error": "Invalid URL."})
    except Exception as e:
        logging.error(f"Scrape error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/ask")
async def ask(request: Request):
    try:
        body = await request.json()
        data = AskRequest(**body)
        logging.info(f"Query: '{data.query}' for {data.url}")

        response = get_bot_response(data.url, data.query)
        return {"response": response}
    except ValidationError:
        return JSONResponse(status_code=400, content={"error": "Invalid input."})
    except Exception as e:
        logging.error(f"Ask error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

# Endpoint to serve the chatbot widget JS
@app.get("/widget.js")
def serve_widget_js():
    return FileResponse("frontend/static/widget.js", media_type="application/javascript")

# Endpoint to serve embedded widget HTML (for iframe method)
@app.get("/embed")
def serve_embed_widget():
    with open("frontend/static/embed.html", "r", encoding="utf-8") as f:
        content = f.read()
    return HTMLResponse(content)

@app.post("/save-bot")
async def save_bot(request: Request):
    try:
        body = await request.json()
        url = body.get("url")
        if not url:
            return JSONResponse(status_code=400, content={"error": "Missing URL"})

        parsed_url = urlparse(url)
        domain = parsed_url.netloc

        embedding_path = f"data/vectors/{domain}_embedding.npy"
        text_path = f"data/vectors/{domain}_text.pkl"

        if not os.path.exists(embedding_path):
            return JSONResponse(
                status_code=404,
                content={"error": f"Missing embedding file: {embedding_path}"}
            )

        if not os.path.exists(text_path):
            return JSONResponse(
                status_code=404,
                content={"error": f"Missing text file: {text_path}"}
            )

        bot_dir = f"bots/{domain}"
        os.makedirs(bot_dir, exist_ok=True)

        shutil.copy(embedding_path, f"{bot_dir}/embedding.npy")
        shutil.copy(text_path, f"{bot_dir}/text.pkl")

        return {"message": f"Bot successfully saved to {bot_dir}"}
    except Exception as e:
        logging.error(f"Bot saving failed: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

from .vector_store import save_embeddings, generate_embeddings
import os
import re
import hashlib

from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from urllib.parse import urlparse, parse_qs
from .scraper import scrape_website



def is_youtube_video_url(url: str) -> bool:
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    if "youtube.com" in domain or "youtu.be" in domain:
        if "watch" in parsed.path and "v" in parse_qs(parsed.query):
            return True
        if "youtu.be" in domain and parsed.path.strip("/"):
            return True
    return False

def extract_video_id(url: str) -> str:
    parsed_url = urlparse(url)
    if "youtube.com" in parsed_url.netloc:
        return parse_qs(parsed_url.query).get("v", [""])[0]
    elif "youtu.be" in parsed_url.netloc:
        return parsed_url.path.lstrip("/")
    return ""

def get_youtube_transcript(url: str) -> str:
    try:
        video_id = extract_video_id(url)
        if not video_id:
            raise ValueError("Invalid YouTube URL")

        # Fetch transcript
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)

        # Combine transcript
        transcript = " ".join([entry["text"] for entry in transcript_list])
        transcript = re.sub(r"\s+", " ", transcript).strip()

        # Save raw transcript text
        hashed = hashlib.md5(url.encode()).hexdigest()
        os.makedirs("data/texts", exist_ok=True)
        with open(f"data/texts/{hashed}.txt", "w", encoding="utf-8") as f:
            f.write(transcript)

        # Generate and save embeddings
        embedding = generate_embeddings(transcript)
        save_embeddings(domain=url, embedding=embedding, text=transcript)

        return transcript

    except TranscriptsDisabled:
        print(f"[YouTube Transcript] Transcripts disabled for {url}")
    except NoTranscriptFound:
        print(f"[YouTube Transcript] No transcript found for {url}")
    except Exception as e:
        print(f"[YouTube Transcript Error] {e}")

    return ""

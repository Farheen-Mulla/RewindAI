import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
CHUNK_WINDOW_SECONDS = int(os.environ.get("CHUNK_WINDOW_SECONDS", "45"))
TOP_K = int(os.environ.get("TOP_K", "5"))

# Chroma uses L2 distance over MiniLM's normalized embeddings (~0-2 range).
# Retrieved chunks above this are treated as "not actually relevant" for the guardrail.
# Tune against your own playlist if the guardrail fires too often or not enough.
MAX_DISTANCE = float(os.environ.get("MAX_DISTANCE", "1.2"))

BACKEND_DIR = Path(__file__).resolve().parent.parent
STARTER_DIR = BACKEND_DIR.parent
DATA_DIR = STARTER_DIR / "data"
TRANSCRIPTS_PATH = Path(os.environ.get("TRANSCRIPTS_PATH", str(DATA_DIR / "transcripts.json")))
CHROMA_DIR = str(DATA_DIR / "chroma_db")
COLLECTION_NAME = "lecture_chunks"

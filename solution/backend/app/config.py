import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
CHUNK_WINDOW_SECONDS = int(os.environ.get("CHUNK_WINDOW_SECONDS", "45"))
CHUNK_OVERLAP_SECONDS = int(os.environ.get("CHUNK_OVERLAP_SECONDS", "10"))
TOP_K = int(os.environ.get("TOP_K", "5"))

# v2 retrieval: how many candidates to pull before reranking/MMR narrow it down to TOP_K.
RETRIEVE_CANDIDATES = int(os.environ.get("RETRIEVE_CANDIDATES", "15"))
RERANK_MODEL = os.environ.get("RERANK_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")
MMR_LAMBDA = float(os.environ.get("MMR_LAMBDA", "0.7"))

# Chroma uses L2 distance over MiniLM's normalized embeddings (~0-2 range).
# Retrieved chunks above this are treated as "not actually relevant" for the guardrail.
# Tune against your own playlist if the guardrail fires too often or not enough.
MAX_DISTANCE = float(os.environ.get("MAX_DISTANCE", "1.2"))

BACKEND_DIR = Path(__file__).resolve().parent.parent
SOLUTION_DIR = BACKEND_DIR.parent
DATA_DIR = SOLUTION_DIR / "data"
TRANSCRIPTS_PATH = Path(os.environ.get("TRANSCRIPTS_PATH", str(DATA_DIR / "transcripts.json")))
CHROMA_DIR = str(DATA_DIR / "chroma_db")
COLLECTION_NAME = "lecture_chunks"

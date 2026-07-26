# RAG 2.0

Build a deployed RAG app that answers questions from your own lecture YouTube playlist — with citations that seek the video to the exact minute. Live, from an empty folder to a public URL.

2-day workshop — Aug 1–2, 2026. Day 1: theory. Day 2: hands-on build + deploy.

## Structure

- **`starter/`** — scaffolding to code along with during the workshop. Folder layout and configs match `solution/` exactly; implementations are TODO-marked stubs.
- **`solution/`** — fully working reference app.
- **`architecture.md`** — system architecture diagram.

## Stack

| Layer | Choice |
|---|---|
| Backend | FastAPI (Python) |
| Embeddings | local, `sentence-transformers` (no API key) |
| Vector store | ChromaDB (embedded, rebuilt from `data/transcripts.json` on every startup) |
| LLM | Groq API (fast inference, swappable models) |
| Transcripts | `youtube-transcript-api` (YouTube playlist primary; local video + Whisper as fallback) |
| Frontend | Plain HTML/CSS/JS — no framework, no build step |
| Deploy | Render (free tier) |

## Why transcripts are rebuilt on startup

Render's free tier disk is ephemeral — wiped on every restart/redeploy. Instead of persisting a Chroma directory, the app commits a pre-processed `data/transcripts.json` (chunked text + timestamp metadata, no embeddings, no secrets) and rebuilds the Chroma index from it at container startup. Deploys stay stateless and reproducible.

## Quickstart (solution/)

```bash
cd solution/backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in GROQ_API_KEY
python -m app.ingest --playlist "<youtube playlist URL>"   # builds data/transcripts.json
uvicorn app.main:app --reload
```

Open `solution/frontend/index.html` (served by the backend at `/`) and start asking questions.

## Deploying

See `solution/render.yaml` and `architecture.md` for the deploy walkthrough.

## Stretch goals

`solution/` runs a sharper retrieval pipeline than what `starter/` teaches in the core
build — hybrid vector+keyword search, cross-encoder reranking, diversity filtering, and an
evaluation harness for measuring retrieval quality on your own playlist. Not part of the
required Day 2 path; see `architecture.md` and `solution/backend/app/retrieval.py`.

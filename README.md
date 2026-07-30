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

The repo **ships with a ready-made `data/transcripts.json`** (a 3Blue1Brown "Essence of calculus"
playlist), so it runs out of the box — no YouTube ingest needed. One command on a fresh machine,
no Python required. The script installs [`uv`](https://astral.sh/uv) if missing, uv fetches
Python 3.11, then it creates the venv, installs deps, sets up `.env`, and starts the server:

```bash
# macOS / Linux
./setup.sh

# Windows (PowerShell)
.\setup.ps1
```

It prompts only for your `GROQ_API_KEY`. Open the served page and ask about calculus.

**To use your own playlist instead**, pass a URL — that re-ingests and overwrites
`transcripts.json`:

```bash
./setup.sh "<youtube playlist URL>"          # PowerShell: .\setup.ps1 "<url>"
```

> **YouTube may IP-block ingest.** Transcript fetching happens only at ingest time (offline,
> one-time) — the deployed app never calls YouTube. If ingest fails with an `IpBlocked` error,
> you're on a blocked IP: cloud IPs are blanket-blocked, and a home IP can get rate-limited after
> many requests. Ingest already **falls back to yt-dlp automatically** when the primary fetch is
> blocked. Further fixes, simplest first: run from a **residential IP** (home wifi, or a phone
> hotspot — a different IP often clears it); set `YTDLP_COOKIES_FROM_BROWSER=chrome` in `.env` so
> the yt-dlp fallback uses your logged-in cookies (best free lever on a soft-blocked home IP); or,
> last resort for a hard block, set `WEBSHARE_PROXY_USERNAME` / `WEBSHARE_PROXY_PASSWORD` to route
> through a residential proxy. You only need one successful ingest — commit the resulting
> `transcripts.json`.

Flags: `--no-serve`, `--force-ingest` (PowerShell: `-NoServe`, `-ForceIngest`).

Manual equivalent:

```bash
cd solution/backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in GROQ_API_KEY
# transcripts.json already ships; to use your own playlist:
# python -m app.ingest --playlist "<youtube playlist URL>"
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

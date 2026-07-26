# Deploying to Render

The app deploys as a single Render web service: FastAPI serves both the `/api/chat` SSE
endpoint and the static frontend from `solution/frontend`.

## Before the first deploy

1. Run ingestion locally against your playlist so `solution/data/transcripts.json` exists
   and is committed:
   ```bash
   cd solution/backend
   python -m app.ingest --playlist "<youtube playlist URL>"
   ```
2. Commit `solution/data/transcripts.json`. This is the one data artifact that's meant to be
   in git — no embeddings, no secrets, just chunked text + timestamps.

## Deploy steps

1. Push the repo to GitHub (already done — `origin` points at `RAG-2.O`).
2. In the Render dashboard: **New > Blueprint**, point it at this repo. Render reads
   `render.yaml` at the repo root and creates the `rag-2-0` web service with `rootDir:
   solution/backend`.
3. Set the `GROQ_API_KEY` environment variable in the Render dashboard (marked `sync: false`
   in `render.yaml` on purpose — secrets don't belong in a committed file).
4. Deploy. Build runs `pip install -r requirements.txt`; start runs `uvicorn app.main:app
   --host 0.0.0.0 --port $PORT`.

## Why there's no separate "build the index" step

Render's free-tier disk is ephemeral — anything written to it disappears on the next
restart or redeploy. Rather than persisting a Chroma directory, the FastAPI app's
`lifespan` hook rebuilds the Chroma collection from `solution/data/transcripts.json` on
every startup (see `solution/backend/app/main.py`). That's a few seconds for one playlist,
and it means every deploy is reproducible from source — no manual "seed the database" step,
no drift between what's in git and what's actually served.

## Verifying a deploy end-to-end

1. Trigger a fresh deploy (or manual redeploy) and confirm in the logs: `Rebuilding Chroma
   index from transcripts.json...` followed by `Index ready.`
2. Open the public URL, ask a question that IS covered in the lectures — confirm you get a
   streamed answer with citation chips.
3. Click a citation chip — confirm the embedded player seeks to that timestamp.
4. Ask something NOT covered in the lectures — confirm the guardrail response ("I couldn't
   find that in these lectures") fires instead of a hallucinated answer.
5. Ask a follow-up question referencing the previous answer — confirm multi-turn context
   works.

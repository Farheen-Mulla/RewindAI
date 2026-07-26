# Architecture

Live, editable diagram (FigJam): https://www.figma.com/board/t6RrdGRu3EwJZVASiAKX1v

## Summary

```
Browser (Chat UI)
  --HTTPS--> FastAPI App (Render Web Service)
    --routes /api/chat, rebuilds index at startup--> RAG Query Pipeline
      --queries top-k / rebuilds index--> ChromaDB (rebuilt at startup, never persisted)
      --reads chunks--> transcripts.json (committed to repo)
      --stream completion--> Groq (external)

Ingestion CLI (offline, run before deploy / live on stage)
  --writes chunks--> transcripts.json
  --fetch transcripts--> YouTube (external)
```

Two pipelines, one deployable backend:

- **Ingestion** (`app/ingest.py`) runs offline — pulls playlist transcripts from YouTube,
  chunks them by timestamp window, writes `transcripts.json`. Not part of the running web
  service; invoked manually (or live, Day 2).
- **Query** (`app/rag.py`, `app/vectorstore.py`, `app/main.py`) runs per-request inside the
  deployed FastAPI app — retrieval, guardrail filtering, Groq streaming, SSE to the browser.

The one non-obvious edge: FastAPI's startup hook rebuilds the ChromaDB index from
`transcripts.json` every time the process starts, because Render's free-tier disk doesn't
survive a restart. See `docs/deploy.md` for why.

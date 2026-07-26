# data/

`transcripts.json` lives here once you run ingestion — it's the pre-processed, chunked, timestamped
transcript output that gets committed to the repo and is what a fresh deploy rebuilds its Chroma
index from on startup (see root README, "Why transcripts are rebuilt on startup").

Generate it with:

```bash
cd solution/backend
python -m app.ingest --playlist "<youtube playlist URL>"
```

It contains chunked lecture text + timestamps + video IDs — no embeddings, no secrets — so it's
safe to commit.

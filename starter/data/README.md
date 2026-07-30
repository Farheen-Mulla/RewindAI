# data/

`transcripts.json` is the pre-processed, chunked, timestamped transcript output — what a fresh
deploy rebuilds its Chroma index from on startup (see root README, "Why transcripts are rebuilt on
startup"). A ready-made demo set (3Blue1Brown "Essence of calculus") **ships here already**, so the
app runs out of the box.

To use your own playlist, regenerate it (overwrites the demo). Run this once from a **residential
IP** — YouTube IP-blocks cloud IPs and rate-limits over-eager home IPs:

```bash
cd starter/backend
python -m app.ingest --playlist "<youtube playlist URL>"
# IpBlocked? ingest auto-falls back to yt-dlp. Also try a phone hotspot, or set
# YTDLP_COOKIES_FROM_BROWSER / WEBSHARE_PROXY_* in .env (see .env.example)
```

It contains chunked lecture text + timestamps + video IDs — no embeddings, no secrets — so it's
safe to commit.

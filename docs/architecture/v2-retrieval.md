# v2 retrieval (stretch content, not part of the core build)

`solution/` runs a better retrieval pipeline than what `starter/` teaches in the core 3-hour
Day 2 build. This is deliberate: the core path stays the simple, single-vector-search
pipeline so the empty-folder-to-public-URL promise fits the time box. This doc explains what
`solution/` actually does on top of that, for instructors or attendees who want to go
further — read the code in `solution/backend/app/retrieval.py` and `app/evaluate.py`
directly; nothing here is stubbed out in `starter/`.

## What changed vs. the core pipeline

The core pipeline (`starter/`, and `vectorstore.query()` in `solution/`) is: embed the
question, vector-search Chroma, take the top-k, done. Four upgrades on top of that, all in
`solution/backend/app/retrieval.py`:

1. **Hybrid search (vector + keyword, RRF)** — dense embeddings miss exact terms and
   acronyms (a question containing "BM25" won't necessarily retrieve a chunk that says
   "BM25" if the surrounding phrasing differs). A keyword index (`rank_bm25`, in-memory,
   no new infra) runs alongside vector search; results are merged by rank via Reciprocal
   Rank Fusion, which sidesteps the fact that L2 distance and BM25 score live on
   incomparable scales.
2. **Cross-encoder reranking** — vector/keyword search score a chunk in isolation; a
   cross-encoder (`cross-encoder/ms-marco-MiniLM-L-6-v2`, local, free) scores the question
   and chunk together, which is slower — so it only runs over ~15 fused candidates, not the
   whole corpus — but meaningfully more precise. This becomes the ranking signal for
   everything downstream.
3. **MMR diversity filter** — without it, two near-duplicate chunks (the same point recapped
   across two lectures) can both score well and crowd out a third, genuinely different,
   relevant chunk. Maximal Marginal Relevance trades a little raw relevance for topic
   coverage in the final top-k.
4. **Overlapping chunk windows** — not retrieval-time, but related: `chunk_transcript` now
   overlaps windows by ~10s so an answer split right across a boundary still appears whole
   in at least one chunk.

## The guardrail threshold isn't a number you can guess

The original guardrail compared Chroma's L2 distance to a fixed cutoff. Once reranking is in
the loop, that has to become a cross-encoder score cutoff (`MIN_RERANK_SCORE`) instead — and
this is the one place worth calling out explicitly, because it went wrong during
development: the naive assumption was "0.0 is the relevant/irrelevant boundary." On a real
run, genuinely relevant top hits scored anywhere from **-0.7 to -8**, while clearly irrelevant
questions clustered around **-11**. A 0.0 cutoff would have rejected correct answers outright
— a false "I couldn't find that in these lectures" on questions the playlist actually
covers, which is a worse failure mode live than answering.

This is exactly why `app/evaluate.py` exists as more than a hit-rate/MRR reporter: run it
against your own labeled `eval_questions.json` and it prints the actual score range for
questions that hit vs. questions that missed, plus a suggested `MIN_RERANK_SCORE` computed
from that gap. Calibrate from your own playlist's data, not a guess — the same lesson as
`MAX_DISTANCE` in the base pipeline, just sharper.

## Trying it

```bash
cd solution/backend
cp ../data/eval_questions.example.json ../data/eval_questions.json   # then hand-label it
python -m app.evaluate --pipeline hybrid        # what the deployed app runs
python -m app.evaluate --pipeline vector-only   # base pipeline, for comparison
```

Worth doing live in the Day 1 architecture walkthrough or the buffer hour: run both and show
the actual hit-rate/MRR delta on your own playlist. "Here's the number this upgrade actually
buys you" lands better than the concept alone.

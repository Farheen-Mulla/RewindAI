# data/

`transcripts.json` lives here once you run ingestion — it's the pre-processed, chunked, timestamped
transcript output the app rebuilds its Chroma index from on startup (see root README, "Why
transcripts are rebuilt on startup"). It is **not committed** — it's playlist-specific and generated
locally. Without it the index is empty and the app answers nothing.

Generate it (or just run `./setup.sh` from the repo root, which does this for you):

```bash
cd solution/backend
python -m app.ingest --playlist "<youtube playlist URL>"
```

To deploy on Render, commit the generated `transcripts.json` so the container has data to rebuild
from on startup.

It contains chunked lecture text + timestamps + video IDs — no embeddings, no secrets — so it's
safe to commit.

## eval_questions.json

Copy `eval_questions.example.json` to `eval_questions.json` and hand-label 5-10 real
question/expected-video pairs from your own playlist (see the format notes in the example
file). Then run:

```bash
python -m app.evaluate --pipeline hybrid       # what the deployed app actually runs
python -m app.evaluate --pipeline vector-only  # baseline, for comparison
```

Reports hit-rate@k and MRR — see `docs/architecture/v2-retrieval.md` for what these mean and
why they're worth showing live in the Day 1 architecture walkthrough.

# Day 1 — RAG Theory & Architecture (3hrs core + 1hr buffer)

Aug 1, 2026. Goal: everyone leaves understanding *why* each piece of RAG 2.0 exists, so Day 2
is pure typing, no conceptual surprises. Buffer hour absorbs Q&A overrun and environment-setup
troubleshooting — don't plan new content into it.

## 1. Why RAG at all (15 min)

- The problem: LLMs don't know your lectures, and fine-tuning is slow/expensive/goes stale.
- The idea: retrieve relevant material at question time, hand it to the model as context,
  let the model reason over *your* content instead of its training data.
- Preview the end state: ask this room's own lecture playlist a question, get a cited,
  seekable answer. That's what gets built tomorrow.

## 2. Embeddings (25 min)

- Text → vector: semantically similar text ends up close in vector space.
- Why not keyword search: "how do I avoid overfitting" should match a chunk that says
  "regularization prevents the model memorizing training data" — no shared words.
- Local vs hosted embeddings: this project uses `sentence-transformers` (runs on your
  laptop, free, no API key) — trade-off is lower quality than hosted models like OpenAI's
  or Voyage's, acceptable for a workshop-scale playlist.
- Live demo: embed two similar sentences and two unrelated ones, show cosine distance.

## 3. Vector search (20 min)

- What a vector store actually does: nearest-neighbor search over embeddings, plus
  metadata filtering.
- Why ChromaDB for this project: embedded (no server to run), file-based, zero infra —
  matches the "empty folder to public URL" constraint. Contrast briefly with
  Qdrant/Pinecone for when you'd reach for a real server.
- Distance metrics in one sentence: smaller distance = more similar; today's guardrail
  logic later depends on this.

## 4. Chunking strategies (30 min) — the part most tutorials skip

- Naive chunking (fixed character count) breaks mid-sentence and, worse for this project,
  loses the connection between a chunk and *when* it was said.
- This project's approach: chunk by timestamp window (~45s), not character count — every
  chunk keeps the timestamp of its first line. That's the entire mechanism behind "citations
  that seek to the right minute."
- Trade-offs to name explicitly: window too short → chunks lack context; too long → less
  precise seeking and noisier retrieval. 45s is a starting point, not gospel — tune per
  content density.
- Mention near-duplicate chunks across videos in a series (same topic recapped) as a known
  rough edge — not solved here, worth knowing it exists.

## 5. Retrieval + generation (30 min)

- The RAG loop end to end: question → embed → retrieve top-k → stuff into prompt as
  labeled context → generate.
- Query rewriting for follow-ups: "what about the second one?" only retrieves correctly if
  recent chat history gets folded into the search query first.
- Groq as the generation provider: why — extremely fast inference (good for a live demo),
  swappable models via one config string, generous free tier for a room full of attendees
  hitting the API at once.
- Streaming: why token-by-token SSE instead of waiting for the full response — perceived
  latency, and it's what makes Groq's speed *visible* in the demo.

## 6. Hallucination guardrails (20 min)

- The failure mode: model answers confidently from its own training data instead of the
  retrieved lecture content, when nothing relevant was actually retrieved.
- Two-layer defense used in this project:
  1. Distance-threshold filter — if the best retrieved chunk is still too far from the
     question, don't even call the LLM; return "not covered in these lectures" directly.
  2. Prompt-level instruction — system prompt explicitly forbids outside knowledge and
     tells the model to say so when context is insufficient.
- Why both layers: the threshold catches "nothing relevant was retrieved," the prompt
  catches "something was retrieved but doesn't actually answer this."

## 7. This project's architecture, walked end to end (35 min)

Walk the architecture diagram (`docs/architecture/`) live:

- **Ingestion pipeline**: playlist → transcripts (with the "no captions available" edge
  case) → timestamp-windowed chunks → local embeddings → ChromaDB.
- **Query pipeline**: question + history → rewritten query → retrieval → guardrail filter
  → prompt assembly → Groq streaming → SSE → frontend chips that seek the player.
- **The ephemeral-disk deploy decision**: Render's free tier wipes disk on every
  restart/redeploy — so the built Chroma index is never persisted or committed. Instead
  `transcripts.json` (cheap, text-only, no secrets) is committed, and the index rebuilds
  from it on every container startup. This is the one architectural decision most
  tutorials skip and it's why the deploy in tomorrow's demo will actually survive a
  redeploy without a manual re-seeding step.
- Name every edge case built into the app and where it lives in the code (captionless
  video skip in `ingest.py`, guardrail in `rag.py`, disconnect handling in the token
  generator, rate-limit error surfaced to the chat UI).

## 8. Environment setup (25 min, hands-on)

Do this live so Day 2 starts with zero setup friction:

- Clone the repo, `cd starter/backend`, create a venv, `pip install -r requirements.txt`.
- Sign up for a Groq API key (free), copy `.env.example` to `.env`, fill it in.
- Confirm `python -c "import chromadb, sentence_transformers, groq"` succeeds for everyone
  in the room before moving on — this is the single most common place a workshop stalls.
- Preview tomorrow's build order so people know what's coming: ingestion → query pipeline
  → frontend wiring → deploy.

## Buffer hour

Reserve for: attendees behind on environment setup, deeper Q&A on any section above,
or a short live walkthrough of the `solution/` code for anyone who wants to see the target
before Day 2 starts building toward it.

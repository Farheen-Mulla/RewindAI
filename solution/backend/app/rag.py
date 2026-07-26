import logging

from groq import Groq

from . import config
from .vectorstore import query as vector_query

logger = logging.getLogger(__name__)

_client = None

SYSTEM_PROMPT = """You are a teaching assistant that answers questions using ONLY the lecture \
transcript excerpts provided below as context. Each excerpt is labeled with a source number.

Rules:
- Answer only from the provided context. Do not use outside knowledge.
- If the context does not contain the answer, say plainly: "I couldn't find that in these \
lectures." Do not guess or make anything up.
- Keep answers concise and direct.
- When you reference something a source excerpt said, mention which source number backs it, \
like (Source 2)."""


def _get_client():
    global _client
    if _client is None:
        _client = Groq(api_key=config.GROQ_API_KEY)
    return _client


def _format_timestamp(seconds):
    seconds = int(seconds)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def _format_context(hits):
    lines = []
    for i, hit in enumerate(hits, start=1):
        meta = hit["metadata"]
        timestamp = _format_timestamp(meta["start_seconds"])
        lines.append(f'[Source {i} — "{meta["title"]}" @ {timestamp}]\n{hit["text"]}')
    return "\n\n".join(lines)


def _rewrite_query(question, history):
    if not history:
        return question
    recent = history[-4:]
    convo = "\n".join(f"{turn['role']}: {turn['content']}" for turn in recent)
    return f"{convo}\nuser: {question}"


def _relevant_hits(hits):
    return [h for h in hits if h["distance"] <= config.MAX_DISTANCE]


def _citations_from_hits(hits):
    return [
        {
            "index": i + 1,
            "title": h["metadata"]["title"],
            "video_id": h["metadata"]["video_id"],
            "start_seconds": h["metadata"]["start_seconds"],
            "youtube_url": h["metadata"]["youtube_url"],
            "timestamp": _format_timestamp(h["metadata"]["start_seconds"]),
        }
        for i, h in enumerate(hits)
    ]


def _empty_stream():
    yield "I couldn't find that in these lectures."


def answer_stream(question, history=None):
    """Retrieve relevant chunks and return (token_generator, citations) for the question.

    Returns immediately with citations (retrieval already happened) so the caller
    can send them ahead of the token stream.
    """
    history = history or []
    search_query = _rewrite_query(question, history)
    hits = vector_query(search_query, top_k=config.TOP_K)
    relevant = _relevant_hits(hits)

    if not relevant:
        return _empty_stream(), []

    citations = _citations_from_hits(relevant)
    context = _format_context(relevant)

    messages = [{"role": "system", "content": SYSTEM_PROMPT + "\n\nContext:\n" + context}]
    for turn in history[-6:]:
        messages.append({"role": turn["role"], "content": turn["content"]})
    messages.append({"role": "user", "content": question})

    client = _get_client()

    def token_gen():
        try:
            stream = client.chat.completions.create(model=config.GROQ_MODEL, messages=messages, stream=True)
            for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    yield delta
        except GeneratorExit:
            # Client disconnected mid-stream — let Groq's connection close, don't retry/swallow.
            raise
        except Exception as exc:
            logger.exception("Groq streaming failed")
            yield f"\n\n[Error: could not reach the model — {exc}]"

    return token_gen(), citations

import logging

from groq import Groq

from . import config
from .vectorstore import query as vector_query

logger = logging.getLogger(__name__)

_client = None

SYSTEM_PROMPT = """You are a teaching assistant answering questions from a set of lecture \
transcript excerpts provided below as context. Each excerpt is labeled with a source number.

How to answer:
- Explain the concept fully and clearly in your own words, synthesizing across the excerpts into \
one coherent answer — aim for a substantive paragraph, not a one-line summary.
- Use ONLY the provided context; do not add outside facts. If the context genuinely doesn't \
cover the question, say exactly: "I couldn't find that in these lectures." Don't guess.
- Don't narrate the sources ("Source 2 says…"). Explain the idea directly and cite by appending \
the source number in parentheses after the claim it supports, e.g. "…how much a function is \
changing at each point (Source 1)."
- Be specific: include the concrete details, examples, and intuition the excerpts give. Teach the \
concept rather than describing what the excerpts contain."""


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


def _rewrite_query(question, history):
    """Fold recent chat history into the retrieval query for follow-up questions.

    TODO: if `history` is empty, just return `question` unchanged. Otherwise, take the
    last few turns (e.g. history[-4:]) and prepend them to the question as plain text
    ("role: content" per line) so a vague follow-up like "what about the second one?"
    still retrieves the right chunks.
    """
    raise NotImplementedError("TODO: implement _rewrite_query")


def _relevant_hits(hits):
    """Filter retrieved hits down to ones actually worth answering from.

    TODO: keep only hits whose "distance" is <= config.MAX_DISTANCE. This is the
    guardrail against hallucination — if nothing retrieved is close enough, the caller
    should fall back to "I couldn't find that in these lectures" instead of asking the
    model to answer from irrelevant context.
    """
    raise NotImplementedError("TODO: implement _relevant_hits")


def answer_stream(question, history=None):
    """Retrieve relevant chunks and return (token_generator, citations) for the question.

    TODO:
    1. Build a search query via _rewrite_query(question, history or []).
    2. Retrieve hits via vector_query(search_query, top_k=config.TOP_K).
    3. Filter to relevant = _relevant_hits(hits). If empty, return (_empty_stream(), []) —
       this is the "not covered in these lectures" guardrail path.
    4. Otherwise build citations = _citations_from_hits(relevant) and context =
       _format_context(relevant).
    5. Build the messages list: a system message (SYSTEM_PROMPT + the context), then
       the last few turns of `history`, then the current user question.
    6. Return a generator that streams tokens from Groq (client.chat.completions.create
       with stream=True, yielding chunk.choices[0].delta.content for each chunk that has
       one) alongside `citations`.

    Handle two failure modes inside the token generator:
    - GeneratorExit (client disconnected mid-stream): re-raise it, don't swallow it —
      that's what lets the Groq connection actually close instead of hanging.
    - Any other exception (Groq API error, rate limit, etc): log it and yield a visible
      "[Error: ...]" message instead of letting the whole request 500 silently.
    """
    raise NotImplementedError("TODO: implement answer_stream")

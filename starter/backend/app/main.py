import json
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .rag import answer_stream
from .vectorstore import get_collection

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Rebuilding Chroma index from transcripts.json...")
    get_collection(rebuild=True)
    logger.info("Index ready.")
    yield


app = FastAPI(title="RAG 2.0", lifespan=lifespan)


class ChatTurn(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    question: str
    history: list[ChatTurn] = []


def _sse_event(event, data):
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


@app.post("/api/chat")
async def chat(req: ChatRequest):
    """Stream an SSE response for req.question, grounded in the lecture playlist.

    TODO:
    1. Convert req.history (list[ChatTurn]) into plain dicts: [{"role": ..., "content":
       ...}, ...] — answer_stream() expects that shape, not pydantic models.
    2. Define an inner generator `stream()` that:
       a. Calls answer_stream(req.question, history=history) to get (token_gen, citations).
       b. Yields _sse_event("citations", {"citations": citations}) FIRST, before any
          tokens — the frontend needs citation metadata to render chips as text streams in.
       c. Yields _sse_event("token", {"text": token}) for every token from token_gen.
       d. Yields _sse_event("done", {}) once the generator is exhausted.
    3. Return StreamingResponse(stream(), media_type="text/event-stream").
    """
    raise NotImplementedError("TODO: implement the /api/chat streaming endpoint")


@app.get("/api/health")
async def health():
    return {"status": "ok"}


frontend_dir = Path(__file__).resolve().parent.parent.parent / "frontend"
app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")

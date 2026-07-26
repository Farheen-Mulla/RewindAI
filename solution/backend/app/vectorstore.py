import json
import logging
from pathlib import Path

import chromadb
from chromadb.utils import embedding_functions

from . import config

logger = logging.getLogger(__name__)

_client = None
_collection = None


def _get_client():
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=config.CHROMA_DIR)
    return _client


def _embedding_function():
    return embedding_functions.SentenceTransformerEmbeddingFunction(model_name=config.EMBEDDING_MODEL)


def get_collection(rebuild=False):
    """Get the Chroma collection, rebuilding it from transcripts.json if requested.

    Called with rebuild=True once at app startup, since Render's disk is
    ephemeral and any previously-built index won't survive a redeploy.
    """
    global _collection
    if _collection is not None and not rebuild:
        return _collection

    client = _get_client()
    ef = _embedding_function()

    if rebuild:
        try:
            client.delete_collection(config.COLLECTION_NAME)
        except Exception:
            pass

    collection = client.get_or_create_collection(name=config.COLLECTION_NAME, embedding_function=ef)

    if rebuild:
        _populate_from_transcripts(collection)

    _collection = collection
    return _collection


def _populate_from_transcripts(collection):
    transcripts_path = Path(config.TRANSCRIPTS_PATH)
    if not transcripts_path.exists():
        logger.warning(
            "No transcripts.json found at %s — collection will be empty until `python -m app.ingest` runs",
            transcripts_path,
        )
        return

    chunks = json.loads(transcripts_path.read_text())
    if not chunks:
        logger.warning("transcripts.json is empty — nothing to index")
        return

    ids = [f"{c['video_id']}-{c['start_seconds']}" for c in chunks]
    documents = [c["text"] for c in chunks]
    metadatas = [
        {
            "video_id": c["video_id"],
            "title": c["title"],
            "start_seconds": c["start_seconds"],
            "youtube_url": c["youtube_url"],
        }
        for c in chunks
    ]

    batch_size = 100
    for i in range(0, len(ids), batch_size):
        collection.add(
            ids=ids[i : i + batch_size],
            documents=documents[i : i + batch_size],
            metadatas=metadatas[i : i + batch_size],
        )
    logger.info("Indexed %d chunks into Chroma", len(ids))


def query(question, top_k=None):
    collection = get_collection()
    top_k = top_k or config.TOP_K
    if collection.count() == 0:
        return []

    results = collection.query(query_texts=[question], n_results=min(top_k, collection.count()))
    hits = []
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]
    for doc, meta, distance in zip(docs, metas, distances):
        hits.append({"text": doc, "metadata": meta, "distance": distance})
    return hits

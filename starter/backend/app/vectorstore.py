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

    TODO:
    1. If we already have a cached `_collection` and `rebuild` is False, return it.
    2. Get a client via _get_client() and an embedding function via _embedding_function().
    3. If `rebuild` is True: delete any existing collection named config.COLLECTION_NAME
       first (wrap in try/except — it may not exist yet), then get_or_create_collection().
    4. If `rebuild` is True, call _populate_from_transcripts(collection) to fill it.
    5. Cache the collection in the module-level `_collection` and return it.
    """
    raise NotImplementedError("TODO: implement get_collection")


def _populate_from_transcripts(collection):
    """Read transcripts.json and collection.add() every chunk with its metadata.

    TODO:
    1. Read config.TRANSCRIPTS_PATH. If it doesn't exist yet, log a warning and return
       (the collection just stays empty until ingestion has been run).
    2. Parse the JSON into a list of chunk dicts.
    3. Build parallel lists: ids (e.g. f"{video_id}-{start_seconds}"), documents (the
       chunk text), metadatas (video_id, title, start_seconds, youtube_url).
    4. Call collection.add(ids=..., documents=..., metadatas=...). Chroma has a batch
       size limit — if your playlist is large, chunk this into batches of ~100.
    """
    raise NotImplementedError("TODO: implement _populate_from_transcripts")


def query(question, top_k=None):
    """Embed `question` and return the top_k nearest chunks as a list of dicts.

    Each returned dict should look like: {"text": ..., "metadata": {...}, "distance": ...}

    TODO:
    1. Get the collection via get_collection() (no rebuild — it should already exist).
    2. Guard against an empty collection (collection.count() == 0) — return [].
    3. Call collection.query(query_texts=[question], n_results=top_k or config.TOP_K).
    4. Zip together the documents/metadatas/distances from the result and return them
       as the list of dicts described above.
    """
    raise NotImplementedError("TODO: implement query")

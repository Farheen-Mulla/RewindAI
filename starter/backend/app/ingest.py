import argparse
import json
import logging
from pathlib import Path

import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import NoTranscriptFound, TranscriptsDisabled

from . import config
from .chunking import chunk_transcript

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def get_playlist_videos(playlist_url):
    ydl_opts = {"extract_flat": True, "quiet": True, "skip_download": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(playlist_url, download=False)
    entries = info.get("entries", []) if info else []
    return [{"video_id": e["id"], "title": e.get("title") or e["id"]} for e in entries if e.get("id")]


def fetch_transcript(video_id):
    try:
        return YouTubeTranscriptApi.get_transcript(video_id)
    except (TranscriptsDisabled, NoTranscriptFound):
        logger.warning("No captions for video %s — skipping", video_id)
        return None
    except Exception as exc:
        logger.warning("Failed to fetch transcript for %s: %s — skipping", video_id, exc)
        return None


def build_transcripts_json(playlist_url, output_path, window_seconds, overlap_seconds=None):
    """Fetch every video in the playlist, chunk its transcript, write transcripts.json.

    TODO:
    1. Call get_playlist_videos(playlist_url) to get [{"video_id", "title"}, ...].
    2. For each video: call fetch_transcript(video_id). If it returns None (no
       captions — see the edge case handled above), skip it and keep going, don't crash.
    3. Otherwise, call chunk_transcript(entries, window_seconds=window_seconds,
       overlap_seconds=overlap_seconds or config.CHUNK_OVERLAP_SECONDS) and turn
       each chunk into a record:
           {
               "video_id": video_id,
               "title": title,
               "text": chunk["text"],
               "start_seconds": chunk["start_seconds"],
               "youtube_url": f"https://www.youtube.com/watch?v={video_id}",
           }
    4. Collect all records across all videos into one list.
    5. Write that list as JSON to `output_path` (create parent dirs if needed).
    6. Log a summary: how many chunks, from how many videos, how many skipped.
    """
    raise NotImplementedError("TODO: implement build_transcripts_json")


def main():
    parser = argparse.ArgumentParser(description="Ingest a YouTube playlist into transcripts.json")
    parser.add_argument("--playlist", required=True, help="YouTube playlist URL")
    parser.add_argument("--output", default=str(config.TRANSCRIPTS_PATH))
    parser.add_argument("--window-seconds", type=int, default=config.CHUNK_WINDOW_SECONDS)
    parser.add_argument("--overlap-seconds", type=int, default=config.CHUNK_OVERLAP_SECONDS)
    args = parser.parse_args()
    build_transcripts_json(args.playlist, args.output, args.window_seconds, args.overlap_seconds)


if __name__ == "__main__":
    main()

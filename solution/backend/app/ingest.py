import argparse
import json
import logging
from pathlib import Path

import yt_dlp
from youtube_transcript_api import NoTranscriptFound, TranscriptsDisabled, YouTubeTranscriptApi

from . import config
from .chunking import chunk_transcript

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

_yt_api = YouTubeTranscriptApi()


def get_playlist_videos(playlist_url):
    ydl_opts = {"extract_flat": True, "quiet": True, "skip_download": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(playlist_url, download=False)
    entries = info.get("entries", []) if info else []
    return [{"video_id": e["id"], "title": e.get("title") or e["id"]} for e in entries if e.get("id")]


def fetch_transcript(video_id):
    # youtube-transcript-api 1.x: instance .fetch() returns a FetchedTranscript;
    # .to_raw_data() gives the [{text, start, duration}] dicts chunking expects.
    try:
        return _yt_api.fetch(video_id).to_raw_data()
    except (TranscriptsDisabled, NoTranscriptFound):
        logger.warning("No captions for video %s — skipping", video_id)
        return None
    except Exception as exc:
        logger.warning("Failed to fetch transcript for %s: %s — skipping", video_id, exc)
        return None


def build_transcripts_json(playlist_url, output_path, window_seconds, overlap_seconds=None):
    videos = get_playlist_videos(playlist_url)
    logger.info("Found %d videos in playlist", len(videos))

    overlap_seconds = config.CHUNK_OVERLAP_SECONDS if overlap_seconds is None else overlap_seconds
    all_chunks = []
    indexed_count = 0
    skipped_count = 0

    for video in videos:
        video_id = video["video_id"]
        title = video["title"]
        entries = fetch_transcript(video_id)
        if not entries:
            skipped_count += 1
            continue

        chunks = chunk_transcript(entries, window_seconds=window_seconds, overlap_seconds=overlap_seconds)
        for chunk in chunks:
            all_chunks.append(
                {
                    "video_id": video_id,
                    "title": title,
                    "text": chunk["text"],
                    "start_seconds": chunk["start_seconds"],
                    "youtube_url": f"https://www.youtube.com/watch?v={video_id}",
                }
            )
        indexed_count += 1
        logger.info("Chunked %s (%s) into %d chunks", video_id, title, len(chunks))

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(all_chunks, indent=2))
    logger.info(
        "Wrote %d chunks from %d videos to %s (%d skipped: no captions)",
        len(all_chunks),
        indexed_count,
        output_path,
        skipped_count,
    )


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

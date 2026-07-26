def chunk_transcript(entries, window_seconds=45):
    """Group timestamped transcript entries into fixed-duration windows.

    Each output chunk keeps the start_seconds of its first entry, so a citation
    on that chunk seeks the video to where the covered speech actually begins.
    """
    chunks = []
    current_texts = []
    window_start = None
    window_end = None

    for entry in entries:
        text = entry.get("text", "").strip()
        if not text:
            continue

        start = entry["start"]
        if window_start is None:
            window_start = start

        current_texts.append(text)
        window_end = start + entry.get("duration", 0)

        if window_end - window_start >= window_seconds:
            chunks.append({"text": " ".join(current_texts), "start_seconds": int(window_start)})
            current_texts = []
            window_start = None

    if current_texts:
        chunks.append({"text": " ".join(current_texts), "start_seconds": int(window_start)})

    return chunks

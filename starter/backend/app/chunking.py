def chunk_transcript(entries, window_seconds=45, overlap_seconds=10):
    """Group timestamped transcript entries into overlapping fixed-duration windows.

    `entries` is a list of dicts from youtube-transcript-api, each shaped like:
        {"text": "...", "start": 12.4, "duration": 3.1}

    Return a list of dicts shaped like:
        {"text": "<joined text for the window>", "start_seconds": <int start of window>}

    TODO:
    1. Walk through `entries` in order, accumulating (text, start, duration) into the
       current window.
    2. Track when the current window started (the `start` of its first entry).
    3. Once the window has covered >= window_seconds of transcript, close it out:
       append {"text": ..., "start_seconds": ...} to your results list.
    4. Instead of clearing the window entirely, keep only the entries whose end time
       (start + duration) falls after `window_end - overlap_seconds` — that's your
       overlap into the next window. Why bother: without overlap, an answer that's
       split right across a window boundary won't fully appear in either chunk, and
       retrieval quietly misses it.
    5. Don't forget to flush whatever's left in the last (possibly short) window.

    Why start_seconds matters: it's what lets a citation seek the YouTube player to
    the moment this chunk's content was actually said — get it from the FIRST entry
    in the window, not the last.
    """
    raise NotImplementedError("TODO: implement chunk_transcript")

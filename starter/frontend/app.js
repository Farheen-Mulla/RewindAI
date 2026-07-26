const messagesEl = document.getElementById("messages");
const formEl = document.getElementById("chat-form");
const inputEl = document.getElementById("chat-input");
const playerHintEl = document.getElementById("player-hint");

const history = [];
let player = null;
let currentVideoId = null;

// Called by the YouTube IFrame API script once it has loaded.
window.onYouTubeIframeAPIReady = function () {
  player = new YT.Player("player", {
    height: "100%",
    width: "100%",
    playerVars: { rel: 0 },
  });
};

function seekTo(videoId, startSeconds) {
  if (!player) return;
  if (currentVideoId !== videoId) {
    currentVideoId = videoId;
    player.loadVideoById({ videoId, startSeconds });
  } else {
    player.seekTo(startSeconds, true);
    player.playVideo();
  }
  playerHintEl.textContent = "Playing from the cited moment.";
}

function addBubble(role, text) {
  const bubble = document.createElement("div");
  bubble.className = `bubble ${role}`;
  bubble.textContent = text;
  messagesEl.appendChild(bubble);
  messagesEl.scrollTop = messagesEl.scrollHeight;
  return bubble;
}

function renderCitations(container, citations) {
  if (!citations.length) return;
  const wrap = document.createElement("div");
  wrap.className = "citations";
  for (const c of citations) {
    const chip = document.createElement("button");
    chip.type = "button";
    chip.className = "citation-chip";
    chip.textContent = `Source ${c.index} — ${c.title} @ ${c.timestamp}`;
    chip.addEventListener("click", () => seekTo(c.video_id, c.start_seconds));
    wrap.appendChild(chip);
  }
  container.appendChild(wrap);
}

// Parses "event: X\ndata: Y\n\n" frames off an SSE stream sent via fetch (not EventSource,
// since EventSource can't send a POST body — we need one to pass question + history).
//
// TODO:
// 1. fetch("/api/chat", { method: "POST", headers: {"Content-Type": "application/json"},
//    body: JSON.stringify({ question, history }) }).
// 2. If !response.ok || !response.body, throw an Error.
// 3. Get a reader via response.body.getReader() and a TextDecoder.
// 4. Loop: read a chunk, decode it into a running `buffer` string.
// 5. While the buffer contains a "\n\n" boundary, slice out one complete frame, parse its
//    "event: X" and "data: Y" lines (Y is JSON), and:
//    - if event === "citations", call onCitations(data.citations)
//    - if event === "token", call onToken(data.text)
// 6. Stop when the reader reports `done`.
async function streamChat(question, onCitations, onToken) {
  throw new Error("TODO: implement streamChat (SSE-over-fetch parsing)");
}

formEl.addEventListener("submit", async (e) => {
  e.preventDefault();
  const question = inputEl.value.trim();
  if (!question) return;

  inputEl.value = "";
  inputEl.disabled = true;

  addBubble("user", question);
  const assistantBubble = addBubble("assistant", "");
  let answerText = "";
  let citationsContainer = null;

  // TODO: call streamChat(question, onCitations, onToken):
  //   - onCitations(citations): create a container element after assistantBubble and
  //     call renderCitations(citationsContainer, citations) into it.
  //   - onToken(token): append the token to `answerText` and set
  //     assistantBubble.textContent = answerText (keep scrolling messagesEl to bottom).
  // On success, push {role: "user", content: question} and
  // {role: "assistant", content: answerText} onto `history` so follow-up questions have
  // context. On failure, add the "error" class to assistantBubble and show the message.
  // Always re-enable inputEl and refocus it when done (try/finally).
});

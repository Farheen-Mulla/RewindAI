#!/usr/bin/env bash
#
# RAG 2.0 — one-shot local setup for solution/
#
# Does everything needed to run the reference app locally:
#   1. creates a Python venv           (solution/backend/venv)
#   2. installs requirements
#   3. creates .env from .env.example  (prompts for GROQ_API_KEY if missing)
#   4. builds data/transcripts.json    (ingests a YouTube playlist — the app has
#                                        no data and answers nothing without this)
#   5. starts the server               (uvicorn, serves the frontend at /)
#
# Usage:
#   ./setup.sh                         # prompts for playlist URL + Groq key as needed
#   ./setup.sh "<youtube playlist URL>"
#   PLAYLIST_URL="<url>" ./setup.sh
#
# Flags:
#   --no-serve        set up everything but don't start the server
#   --force-ingest    re-ingest even if data/transcripts.json already exists
#
set -euo pipefail

# --- locate paths (works regardless of where the script is called from) ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/solution/backend"
DATA_DIR="$SCRIPT_DIR/solution/data"
VENV_DIR="$BACKEND_DIR/venv"
TRANSCRIPTS="$DATA_DIR/transcripts.json"

# --- parse args ---
SERVE=1
FORCE_INGEST=0
PLAYLIST_URL="${PLAYLIST_URL:-}"
for arg in "$@"; do
  case "$arg" in
    --no-serve)     SERVE=0 ;;
    --force-ingest) FORCE_INGEST=1 ;;
    --*)            echo "Unknown flag: $arg" >&2; exit 1 ;;
    *)              PLAYLIST_URL="$arg" ;;
  esac
done

log() { printf '\n\033[1;36m==>\033[0m %s\n' "$1"; }
warn() { printf '\033[1;33mwarning:\033[0m %s\n' "$1" >&2; }
die() { printf '\033[1;31merror:\033[0m %s\n' "$1" >&2; exit 1; }

# --- 0. prerequisites ---
PYTHON="${PYTHON:-python3}"
command -v "$PYTHON" >/dev/null 2>&1 || die "python3 not found. Install Python 3.11+ first."
[ -d "$BACKEND_DIR" ] || die "solution/backend not found next to setup.sh."
cd "$BACKEND_DIR"

# --- 1. venv ---
if [ ! -d "$VENV_DIR" ]; then
  log "Creating virtualenv ($VENV_DIR)"
  "$PYTHON" -m venv "$VENV_DIR"
else
  log "Reusing existing virtualenv"
fi
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

# --- 2. dependencies ---
log "Installing dependencies (this can take a few minutes on first run)"
python -m pip install --upgrade pip >/dev/null
python -m pip install -r requirements.txt

# --- 3. .env / GROQ_API_KEY ---
if [ ! -f .env ]; then
  log "Creating .env from .env.example"
  cp .env.example .env
fi

# consider the key unset if it's missing or still the placeholder
if ! grep -qE '^GROQ_API_KEY=.+' .env || grep -q '^GROQ_API_KEY=your_groq_api_key_here' .env; then
  if [ -t 0 ]; then
    log "Groq API key needed (get one free at https://console.groq.com/keys)"
    printf 'Paste your GROQ_API_KEY: '
    read -r KEY
    if [ -n "$KEY" ]; then
      # replace the line in-place (portable sed: write temp, move back)
      grep -v '^GROQ_API_KEY=' .env > .env.tmp || true
      printf 'GROQ_API_KEY=%s\n' "$KEY" >> .env.tmp
      mv .env.tmp .env
    else
      warn "No key entered — edit solution/backend/.env before asking questions."
    fi
  else
    warn "GROQ_API_KEY not set in .env — edit solution/backend/.env before asking questions."
  fi
fi

# --- 4. transcripts.json (the data the app is missing) ---
if [ "$FORCE_INGEST" -eq 0 ] && [ -s "$TRANSCRIPTS" ]; then
  log "Found existing $TRANSCRIPTS — skipping ingest (use --force-ingest to rebuild)"
else
  if [ -z "$PLAYLIST_URL" ]; then
    if [ -t 0 ]; then
      log "No transcripts yet — need a YouTube playlist to ingest"
      printf 'Paste a YouTube playlist URL: '
      read -r PLAYLIST_URL
    fi
  fi
  [ -n "$PLAYLIST_URL" ] || die "No playlist URL. Re-run: ./setup.sh \"<youtube playlist URL>\""
  log "Ingesting playlist into $TRANSCRIPTS"
  python -m app.ingest --playlist "$PLAYLIST_URL"
  [ -s "$TRANSCRIPTS" ] || die "Ingest produced no data (videos may lack captions). Check the playlist and retry."
fi

# --- 5. run ---
if [ "$SERVE" -eq 1 ]; then
  log "Starting server at http://127.0.0.1:8000  (Ctrl-C to stop)"
  exec uvicorn app.main:app --reload
else
  log "Setup complete. Start the server with:"
  printf '    cd solution/backend && source venv/bin/activate && uvicorn app.main:app --reload\n'
fi

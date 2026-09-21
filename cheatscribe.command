#!/usr/bin/env bash
# Double-click this file to start cheatscribe and open it in your browser.
set -euo pipefail

cd "$(dirname "$0")"

if [ ! -d .venv ]; then
  echo "Setting up for the first time (this takes a minute)..."
  python3 -m venv .venv
fi

source .venv/bin/activate
python -m pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

# Optional: keep your key in a .env file (gitignored) instead of exporting it each time
if [ -f .env ]; then
  set -a; source .env; set +a
fi

if [ -z "${ANTHROPIC_API_KEY:-}" ]; then
  echo
  echo "  Heads up: ANTHROPIC_API_KEY isn't set, so summarizing will fail."
  echo "  Add it to a .env file in this folder:  ANTHROPIC_API_KEY=your-key"
  echo
fi

PORT="${CHEATSCRIBE_PORT:-5001}"
( sleep 2; open "http://127.0.0.1:${PORT}" ) &

PYTHONPATH=src python -m cheatscribe.web.app

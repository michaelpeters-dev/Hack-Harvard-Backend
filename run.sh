#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

# Kill anything already on 8080
if lsof -ti:8080 >/dev/null; then
  kill -9 $(lsof -ti:8080)
fi

# Start Ollama if not running
if ! pgrep -x "ollama" >/dev/null; then
  echo "Starting Ollama..."
  ollama serve &
  sleep 2
else
  echo "Ollama already running."
fi

# Pull model
ollama pull llava:7b

# Setup venv
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

. .venv/bin/activate
pip install -U pip
pip install -r requirements.txt

# Run API server
echo "Starting caption API at http://0.0.0.0:8080"
uvicorn server:app --host 0.0.0.0 --port 8080 --reload
#!/usr/bin/env bash
set -euo pipefail

# Go to project root
cd "$(dirname "$0")"

# 1) Ensure Ollama server is running (only once per boot)
if ! lsof -i :11434 >/dev/null 2>&1; then
  echo "Starting Ollama..."
  ollama serve &
  sleep 2
else
  echo "Ollama already running."
fi

# 2) Pull the LLaVA model (idempotent, skips if present)
ollama pull llava:7b

# 3) Setup Python venv + deps (only installs missing packages)
if [ ! -d ".venv" ]; then
  echo "Creating venv..."
  python3 -m venv .venv
fi

. .venv/bin/activate
pip install -U pip
pip install -r requirements.txt

# 4) Run the API server (listens on port 8000)
echo "Starting caption API at http://localhost:8000"
uvicorn server:app --host 0.0.0.0 --port 8000 --reload

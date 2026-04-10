#!/usr/bin/env bash
# ------------------------------------------------------------------
# run_api.sh — Launch the AI Chief Agent FastAPI backend
#
# Usage:
#   ./run_api.sh           (foreground, port 8000)
#   ./run_api.sh &         (background)
#
# On VPS, use the systemd service (deploy/ai-chief-api.service).
# ------------------------------------------------------------------
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
elif [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

echo "Starting AI Chief Agent API on http://0.0.0.0:8000"
echo "Docs at http://0.0.0.0:8000/docs"
exec uvicorn app.api.server:app --host 0.0.0.0 --port 8000 --reload

#!/usr/bin/env bash
# ------------------------------------------------------------------
# run_dashboard.sh — Launch the AI Chief Agent Streamlit dashboard
#
# Usage:
#   ./run_dashboard.sh           (foreground)
#   ./run_dashboard.sh &         (background)
#
# On a VPS, prefer the systemd service instead (see deploy/).
# ------------------------------------------------------------------
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Activate venv if present
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
elif [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

echo "Starting AI Chief Agent Dashboard on http://0.0.0.0:8501"
exec streamlit run app/dashboard/app.py \
    --server.address 0.0.0.0 \
    --server.port 8501 \
    --server.headless true

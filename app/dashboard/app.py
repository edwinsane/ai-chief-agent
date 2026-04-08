"""
Streamlit dashboard.

A minimal monitoring UI for the multi-agent system.
Run with:  streamlit run app/dashboard/app.py
"""

import json
import sys
from pathlib import Path

import streamlit as st

# Ensure project root is on the path so app.* imports work
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.storage.database import get_runs, init_db  # noqa: E402

st.set_page_config(page_title="AI Chief Agent", layout="wide")
st.title("AI Chief Agent - Dashboard")

# Make sure the DB exists
init_db()

# --- Recent runs -----------------------------------------------------------
st.header("Recent Runs")
runs = get_runs(limit=50)

if runs:
    for run in runs:
        with st.expander(f"Run #{run['id']} — {run['topic']} ({run['created_at']})"):
            result = json.loads(run["result"]) if run["result"] else {}
            st.json(result)
else:
    st.info("No runs recorded yet. Run the pipeline first with `python main.py`.")

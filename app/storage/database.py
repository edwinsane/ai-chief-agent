"""
SQLite database layer.

Provides a lightweight storage backend for persisting agent run history.
Uses raw sqlite3 to keep dependencies minimal — swap for SQLAlchemy
or async drivers when the project grows.
"""

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from app.core.config import settings
from app.core.logger import logger

# Extract the file path from the SQLite URL (strip "sqlite:///")
_DB_PATH = settings.database_url.replace("sqlite:///", "")


def _get_connection() -> sqlite3.Connection:
    """Return a connection, creating the data directory if needed."""
    Path(_DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create tables if they do not exist."""
    conn = _get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS runs (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            topic      TEXT    NOT NULL,
            result     TEXT,
            created_at TEXT    NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()
    logger.info("Database initialized at %s", _DB_PATH)


def save_run(topic: str, result: dict) -> int:
    """Persist an agent run and return the new row id."""
    conn = _get_connection()
    cursor = conn.execute(
        "INSERT INTO runs (topic, result, created_at) VALUES (?, ?, ?)",
        (topic, json.dumps(result), datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()
    row_id = cursor.lastrowid
    conn.close()
    logger.info("Saved run #%s for topic '%s'", row_id, topic)
    return row_id


def get_runs(limit: int = 20) -> list[dict]:
    """Return the most recent runs."""
    conn = _get_connection()
    rows = conn.execute(
        "SELECT * FROM runs ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_last_run() -> dict | None:
    """Return the single most recent run, or None."""
    runs = get_runs(limit=1)
    return runs[0] if runs else None


def get_run_count() -> int:
    """Return total number of recorded runs."""
    conn = _get_connection()
    count = conn.execute("SELECT COUNT(*) FROM runs").fetchone()[0]
    conn.close()
    return count


def get_all_runs() -> list[dict]:
    """Return every run (no limit). Used by the dashboard for filtering."""
    conn = _get_connection()
    rows = conn.execute("SELECT * FROM runs ORDER BY id DESC").fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_distinct_topics() -> list[str]:
    """Return all unique topics, most recent first."""
    conn = _get_connection()
    rows = conn.execute(
        "SELECT DISTINCT topic FROM runs ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return [row["topic"] for row in rows]


def get_qa_stats() -> dict:
    """Return counts of passed and failed QA checks."""
    conn = _get_connection()
    rows = conn.execute("SELECT result FROM runs WHERE result IS NOT NULL").fetchall()
    conn.close()
    passed = 0
    failed = 0
    for row in rows:
        try:
            data = json.loads(row["result"])
            if data.get("qa_passed"):
                passed += 1
            else:
                failed += 1
        except (json.JSONDecodeError, TypeError):
            failed += 1
    return {"passed": passed, "failed": failed}

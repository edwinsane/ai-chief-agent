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

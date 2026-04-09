"""
SQLite database layer.

Provides storage for both pipeline runs and individual classified articles.
Uses raw sqlite3 to keep dependencies minimal.
"""

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from app.core.config import settings
from app.core.logger import logger

_DB_PATH = settings.database_url.replace("sqlite:///", "")


def _get_connection() -> sqlite3.Connection:
    Path(_DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

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
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS articles (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id           INTEGER NOT NULL,
            title            TEXT    NOT NULL,
            source           TEXT,
            url              TEXT,
            published_at     TEXT,
            short_summary    TEXT,
            why_it_matters   TEXT,
            tags             TEXT,
            relevance_score  REAL,
            category         TEXT,
            region           TEXT,
            urgency          TEXT,
            market_impact    TEXT,
            ai_relevance     TEXT,
            confidence_score REAL,
            created_at       TEXT    NOT NULL,
            FOREIGN KEY (run_id) REFERENCES runs(id)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS briefings (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id           INTEGER NOT NULL,
            top_theme        TEXT,
            overall_risk     TEXT,
            overall_confidence REAL,
            data             TEXT    NOT NULL,
            created_at       TEXT    NOT NULL,
            FOREIGN KEY (run_id) REFERENCES runs(id)
        )
        """
    )
    conn.commit()
    conn.close()
    logger.info("Database initialized at %s", _DB_PATH)


# ---------------------------------------------------------------------------
# Runs
# ---------------------------------------------------------------------------

def save_run(topic: str, result: dict) -> int:
    conn = _get_connection()
    cursor = conn.execute(
        "INSERT INTO runs (topic, result, created_at) VALUES (?, ?, ?)",
        (topic, json.dumps(result, default=str), datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()
    row_id = cursor.lastrowid
    conn.close()
    logger.info("Saved run #%s for topic '%s'", row_id, topic)
    return row_id


def get_runs(limit: int = 20) -> list[dict]:
    conn = _get_connection()
    rows = conn.execute(
        "SELECT * FROM runs ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_last_run() -> dict | None:
    runs = get_runs(limit=1)
    return runs[0] if runs else None


def get_run_count() -> int:
    conn = _get_connection()
    count = conn.execute("SELECT COUNT(*) FROM runs").fetchone()[0]
    conn.close()
    return count


def get_all_runs() -> list[dict]:
    conn = _get_connection()
    rows = conn.execute("SELECT * FROM runs ORDER BY id DESC").fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_distinct_topics() -> list[str]:
    conn = _get_connection()
    rows = conn.execute(
        "SELECT DISTINCT topic FROM runs ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return [row["topic"] for row in rows]


def get_qa_stats() -> dict:
    conn = _get_connection()
    rows = conn.execute("SELECT result FROM runs WHERE result IS NOT NULL").fetchall()
    conn.close()
    passed = failed = 0
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


# ---------------------------------------------------------------------------
# Articles
# ---------------------------------------------------------------------------

def save_articles(run_id: int, articles: list[dict]) -> int:
    """Bulk-insert classified articles for a given run. Returns count saved."""
    conn = _get_connection()
    now = datetime.now(timezone.utc).isoformat()
    for a in articles:
        conn.execute(
            """
            INSERT INTO articles (
                run_id, title, source, url, published_at,
                short_summary, why_it_matters, tags,
                relevance_score, category, region, urgency,
                market_impact, ai_relevance, confidence_score, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run_id,
                a.get("title", ""),
                a.get("source", ""),
                a.get("url", ""),
                a.get("published_at", ""),
                a.get("short_summary", ""),
                a.get("why_it_matters", ""),
                json.dumps(a.get("tags", [])),
                a.get("relevance_score", 0.0),
                a.get("category", ""),
                a.get("region", "Global"),
                a.get("urgency", "low"),
                a.get("market_impact", "low"),
                a.get("ai_relevance", "low"),
                a.get("confidence_score", 0.5),
                now,
            ),
        )
    conn.commit()
    conn.close()
    logger.info("Saved %d articles for run #%d", len(articles), run_id)
    return len(articles)


def get_articles(limit: int = 200) -> list[dict]:
    """Return the most recent articles across all runs."""
    conn = _get_connection()
    rows = conn.execute(
        "SELECT * FROM articles ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    results = []
    for row in rows:
        d = dict(row)
        try:
            d["tags"] = json.loads(d["tags"]) if d["tags"] else []
        except (json.JSONDecodeError, TypeError):
            d["tags"] = []
        results.append(d)
    return results


def get_article_count() -> int:
    conn = _get_connection()
    count = conn.execute("SELECT COUNT(*) FROM articles").fetchone()[0]
    conn.close()
    return count


def get_distinct_categories() -> list[str]:
    conn = _get_connection()
    rows = conn.execute(
        "SELECT DISTINCT category FROM articles WHERE category != '' ORDER BY category"
    ).fetchall()
    conn.close()
    return [row["category"] for row in rows]


def get_distinct_sources() -> list[str]:
    conn = _get_connection()
    rows = conn.execute(
        "SELECT DISTINCT source FROM articles WHERE source != '' ORDER BY source"
    ).fetchall()
    conn.close()
    return [row["source"] for row in rows]


def get_distinct_regions() -> list[str]:
    conn = _get_connection()
    rows = conn.execute(
        "SELECT DISTINCT region FROM articles WHERE region != '' ORDER BY region"
    ).fetchall()
    conn.close()
    return [row["region"] for row in rows]


# ---------------------------------------------------------------------------
# Briefings
# ---------------------------------------------------------------------------

def save_briefing(run_id: int, briefing: dict) -> int:
    """Save a macro intelligence briefing linked to a run."""
    conn = _get_connection()
    now = datetime.now(timezone.utc).isoformat()
    cursor = conn.execute(
        """
        INSERT INTO briefings (run_id, top_theme, overall_risk, overall_confidence, data, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            run_id,
            briefing.get("top_theme", ""),
            briefing.get("overall_risk_level", "low"),
            briefing.get("overall_confidence", 0.0),
            json.dumps(briefing, default=str),
            now,
        ),
    )
    conn.commit()
    row_id = cursor.lastrowid
    conn.close()
    logger.info("Saved briefing #%d for run #%d (theme: %s)", row_id, run_id, briefing.get("top_theme"))
    return row_id


def get_latest_briefing() -> dict | None:
    """Return the most recent briefing with parsed data."""
    conn = _get_connection()
    row = conn.execute("SELECT * FROM briefings ORDER BY id DESC LIMIT 1").fetchone()
    conn.close()
    if not row:
        return None
    d = dict(row)
    try:
        d["data"] = json.loads(d["data"]) if d["data"] else {}
    except (json.JSONDecodeError, TypeError):
        d["data"] = {}
    return d


def get_briefings(limit: int = 20) -> list[dict]:
    """Return recent briefings."""
    conn = _get_connection()
    rows = conn.execute("SELECT * FROM briefings ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    results = []
    for row in rows:
        d = dict(row)
        try:
            d["data"] = json.loads(d["data"]) if d["data"] else {}
        except (json.JSONDecodeError, TypeError):
            d["data"] = {}
        results.append(d)
    return results

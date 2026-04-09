"""
NewsAPI provider.

Fetches headlines and articles from newsapi.org.
Requires NEWSAPI_KEY in environment. Free tier: 100 requests/day.
"""

from __future__ import annotations

import requests

from app.core.config import settings
from app.core.logger import logger
from app.integrations.base_provider import BaseProvider


class NewsAPIProvider(BaseProvider):
    """Fetch news articles from NewsAPI.org."""

    name = "newsapi"
    _BASE = "https://newsapi.org/v2"

    def is_available(self) -> bool:
        return settings.newsapi_enabled

    def fetch(self, queries: list[str], limit: int = 25) -> list[dict]:
        if not self.is_available():
            logger.warning("[newsapi] No API key configured — skipping")
            return []

        articles: list[dict] = []
        per_query = max(limit // len(queries), 5) if queries else limit

        for q in queries:
            try:
                resp = requests.get(
                    f"{self._BASE}/everything",
                    params={
                        "q": q,
                        "pageSize": per_query,
                        "sortBy": "publishedAt",
                        "language": "en",
                        "apiKey": settings.newsapi_key,
                    },
                    timeout=15,
                )
                resp.raise_for_status()
                data = resp.json()
                for a in data.get("articles", []):
                    articles.append(self._normalize(a))
            except requests.RequestException as exc:
                logger.error("[newsapi] Error fetching '%s': %s", q, exc)

        # Deduplicate by title
        seen: set[str] = set()
        unique: list[dict] = []
        for a in articles:
            key = a["title"].lower().strip()
            if key not in seen:
                seen.add(key)
                unique.append(a)

        logger.info("[newsapi] Fetched %d unique articles", len(unique))
        return unique[:limit]

    @staticmethod
    def _normalize(raw: dict) -> dict:
        return {
            "title": raw.get("title") or "",
            "description": raw.get("description") or "",
            "content": raw.get("content") or "",
            "source": (raw.get("source") or {}).get("name", "Unknown"),
            "url": raw.get("url") or "",
            "published_at": raw.get("publishedAt") or "",
        }

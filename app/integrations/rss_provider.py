"""
RSS feed provider.

Fetches articles from curated free RSS feeds. No API key required.
Acts as the always-available fallback when NewsAPI is not configured.
"""

from __future__ import annotations

from datetime import datetime, timezone

import feedparser

from app.core.logger import logger
from app.integrations.base_provider import BaseProvider

# Curated feeds covering AI, tech, markets, geopolitics, and breaking news
_FEEDS: dict[str, str] = {
    "Reuters World": "https://feeds.reuters.com/Reuters/worldNews",
    "Reuters Business": "https://feeds.reuters.com/reuters/businessNews",
    "Reuters Tech": "https://feeds.reuters.com/reuters/technologyNews",
    "BBC World": "https://feeds.bbci.co.uk/news/world/rss.xml",
    "BBC Tech": "https://feeds.bbci.co.uk/news/technology/rss.xml",
    "TechCrunch": "https://techcrunch.com/feed/",
    "Ars Technica AI": "https://feeds.arstechnica.com/arstechnica/technology-lab",
    "Hacker News": "https://hnrss.org/frontpage",
    "Google News AI": "https://news.google.com/rss/search?q=artificial+intelligence&hl=en-US&gl=US&ceid=US:en",
    "Google News Markets": "https://news.google.com/rss/search?q=stock+market+economy&hl=en-US&gl=US&ceid=US:en",
    "Google News Geopolitics": "https://news.google.com/rss/search?q=geopolitics+conflict&hl=en-US&gl=US&ceid=US:en",
}


class RSSProvider(BaseProvider):
    """Fetch articles from curated RSS feeds."""

    name = "rss"

    def is_available(self) -> bool:
        return True  # always available

    def fetch(self, queries: list[str], limit: int = 25) -> list[dict]:
        articles: list[dict] = []

        for feed_name, url in _FEEDS.items():
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries[:8]:  # cap per feed
                    articles.append(self._normalize(entry, feed_name))
            except Exception as exc:
                logger.warning("[rss] Error parsing '%s': %s", feed_name, exc)

        # Deduplicate by title
        seen: set[str] = set()
        unique: list[dict] = []
        for a in articles:
            key = a["title"].lower().strip()
            if key and key not in seen:
                seen.add(key)
                unique.append(a)

        # Sort by published date descending
        unique.sort(key=lambda a: a.get("published_at", ""), reverse=True)

        logger.info("[rss] Fetched %d unique articles from %d feeds", len(unique), len(_FEEDS))
        return unique[:limit]

    @staticmethod
    def _normalize(entry: dict, feed_name: str) -> dict:
        published = ""
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            try:
                dt = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                published = dt.isoformat()
            except Exception:
                published = getattr(entry, "published", "")
        elif hasattr(entry, "published"):
            published = entry.published

        return {
            "title": getattr(entry, "title", ""),
            "description": getattr(entry, "summary", ""),
            "content": "",
            "source": feed_name,
            "url": getattr(entry, "link", ""),
            "published_at": published,
        }

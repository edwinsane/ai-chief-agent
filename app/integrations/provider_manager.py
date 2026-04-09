"""
Provider manager.

Orchestrates all registered data providers. Tries NewsAPI first,
falls back to RSS if NewsAPI is unavailable, and merges results.
"""

from __future__ import annotations

from app.core.logger import logger
from app.integrations.base_provider import BaseProvider
from app.integrations.newsapi_provider import NewsAPIProvider
from app.integrations.rss_provider import RSSProvider


class ProviderManager:
    """Manage and query all registered data providers."""

    def __init__(self) -> None:
        self._providers: list[BaseProvider] = [
            NewsAPIProvider(),
            RSSProvider(),
        ]

    def fetch_all(self, queries: list[str], limit: int = 25) -> list[dict]:
        """
        Fetch from all available providers. Returns merged, deduplicated
        articles up to *limit*.
        """
        all_articles: list[dict] = []
        used_providers: list[str] = []

        for provider in self._providers:
            if provider.is_available():
                try:
                    results = provider.fetch(queries, limit=limit)
                    all_articles.extend(results)
                    used_providers.append(provider.name)
                except Exception as exc:
                    logger.error("[provider_manager] %s failed: %s", provider.name, exc)

        # Deduplicate across providers
        seen: set[str] = set()
        unique: list[dict] = []
        for a in all_articles:
            key = a["title"].lower().strip()
            if key and key not in seen:
                seen.add(key)
                unique.append(a)

        logger.info(
            "[provider_manager] %d unique articles from providers: %s",
            len(unique),
            ", ".join(used_providers) or "none",
        )
        return unique[:limit]

    def register(self, provider: BaseProvider) -> None:
        """Add a new provider at runtime."""
        self._providers.append(provider)
        logger.info("[provider_manager] Registered provider: %s", provider.name)

"""
Abstract base for news/data providers.

Every provider (NewsAPI, RSS, future APIs) implements this interface
so the research agent can swap or combine sources transparently.
"""

from abc import ABC, abstractmethod


class BaseProvider(ABC):
    """Interface that all data providers must implement."""

    name: str = "base"

    @abstractmethod
    def fetch(self, queries: list[str], limit: int = 25) -> list[dict]:
        """
        Fetch articles matching the given queries.

        Returns a list of dicts, each with at minimum:
            title, description, source, url, published_at
        """
        ...

    @abstractmethod
    def is_available(self) -> bool:
        """Return True if this provider is configured and reachable."""
        ...

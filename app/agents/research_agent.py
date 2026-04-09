"""
Research Agent.

Fetches real articles from configured providers (NewsAPI, RSS feeds),
classifies each article, and optionally enriches with LLM analysis.
Falls back to stub data when no providers return results.
"""

from typing import Any

from app.agents.base import BaseAgent
from app.core.classifier import classify
from app.core.logger import logger
from app.integrations.provider_manager import ProviderManager

# Default search queries covering all intelligence categories
_DEFAULT_QUERIES = [
    "artificial intelligence",
    "AI coding agents",
    "AI trading crypto",
    "geopolitics conflict",
    "stock market economy",
    "breaking news world",
]

# Stub articles used when no live provider is available
_STUB_ARTICLES = [
    {
        "title": "OpenAI Announces Next-Gen AI Agent Framework",
        "description": "OpenAI unveiled a new autonomous agent SDK enabling developers to build multi-step AI workflows with tool calling and memory.",
        "source": "TechCrunch",
        "url": "",
        "published_at": "2026-04-08T12:00:00Z",
    },
    {
        "title": "Federal Reserve Signals Rate Hold Amid Inflation Concerns",
        "description": "The Fed indicated it will maintain current interest rates through Q2 as inflation remains above the 2% target.",
        "source": "Reuters",
        "url": "",
        "published_at": "2026-04-08T10:30:00Z",
    },
    {
        "title": "AI Coding Copilots Surpass 50% Adoption in Enterprise",
        "description": "New survey shows over half of Fortune 500 companies now use AI code assistants, with Cursor and GitHub Copilot leading adoption.",
        "source": "Ars Technica",
        "url": "",
        "published_at": "2026-04-08T09:15:00Z",
    },
    {
        "title": "Iran Nuclear Talks Resume Amid Regional Tensions",
        "description": "Diplomatic efforts restart in Vienna as Middle East tensions escalate following recent military developments.",
        "source": "BBC News",
        "url": "",
        "published_at": "2026-04-08T08:00:00Z",
    },
    {
        "title": "Crypto AI Trading Bots Generate Record Returns in Q1",
        "description": "Algorithmic trading platforms using AI models report 40% higher returns than traditional quant strategies this quarter.",
        "source": "CoinDesk",
        "url": "",
        "published_at": "2026-04-08T07:45:00Z",
    },
    {
        "title": "BREAKING: Major Earthquake Hits Southeast Asia",
        "description": "A 7.2 magnitude earthquake struck near Jakarta. Emergency response teams have been deployed. Tsunami warnings issued.",
        "source": "Reuters",
        "url": "",
        "published_at": "2026-04-08T06:00:00Z",
    },
    {
        "title": "Europe Accelerates Renewable Energy Push with New Solar Mandate",
        "description": "EU Parliament approves requirement for solar panels on all new commercial buildings starting 2027.",
        "source": "BBC News",
        "url": "",
        "published_at": "2026-04-08T05:30:00Z",
    },
    {
        "title": "AI Vibe Coding Movement Reshapes Developer Workflows",
        "description": "The trend of natural-language-first coding gains momentum as developers adopt prompt-driven development with AI IDE tools.",
        "source": "Hacker News",
        "url": "",
        "published_at": "2026-04-08T04:00:00Z",
    },
]


class ResearchAgent(BaseAgent):
    """Fetches and classifies articles from live or stub sources."""

    name = "research"

    def __init__(self) -> None:
        super().__init__()
        self.provider_manager = ProviderManager()

    def run(self, state: dict[str, Any]) -> dict[str, Any]:
        topic = state.get("topic", "general")
        queries = state.get("queries", _DEFAULT_QUERIES)
        limit = state.get("fetch_limit", 25)
        logger.info("[%s] Fetching articles for: %s", self.name, topic)

        # Fetch from live providers
        raw_articles = self.provider_manager.fetch_all(queries, limit=limit)

        # Fall back to stubs if nothing came back
        if not raw_articles:
            logger.info("[%s] No live results — using stub articles", self.name)
            raw_articles = _STUB_ARTICLES

        # Classify every article
        classified = [classify(a) for a in raw_articles]

        # Optional LLM enrichment for why_it_matters
        if self.llm:
            classified = self._enrich_with_llm(classified)

        state["articles"] = classified
        state["article_count"] = len(classified)
        logger.info("[%s] Classified %d articles", self.name, len(classified))
        return state

    def _enrich_with_llm(self, articles: list[dict]) -> list[dict]:
        """Add LLM-generated 'why_it_matters' to each article."""
        for a in articles:
            try:
                prompt = (
                    f"In one sentence, explain why this news matters for "
                    f"decision makers:\n\nTitle: {a['title']}\n"
                    f"Summary: {a['short_summary']}"
                )
                resp = self.llm.invoke(prompt)
                a["why_it_matters"] = resp.content.strip()
            except Exception as exc:
                logger.warning("[research] LLM enrichment failed: %s", exc)
        return articles

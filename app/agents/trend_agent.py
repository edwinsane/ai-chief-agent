"""
Trend Analysis Agent.

Analyzes classified articles to identify:
- Repeated topics and emerging patterns
- Top categories and regions
- Optional LLM-generated trend summary
"""

from collections import Counter
from typing import Any

from app.agents.base import BaseAgent
from app.core.logger import logger


class TrendAgent(BaseAgent):
    """Extracts trend insights from classified articles."""

    name = "trend_analysis"

    def run(self, state: dict[str, Any]) -> dict[str, Any]:
        articles = state.get("articles", [])
        logger.info("[%s] Analyzing trends from %d articles", self.name, len(articles))

        if not articles:
            state["trends"] = {"top_categories": [], "top_tags": [], "top_regions": [], "summary": "No data"}
            return state

        # Count categories
        cat_counter = Counter(a.get("category", "Unknown") for a in articles)
        top_categories = cat_counter.most_common(8)

        # Count tags
        tag_counter: Counter = Counter()
        for a in articles:
            for tag in a.get("tags", []):
                tag_counter[tag] += 1
        top_tags = tag_counter.most_common(15)

        # Count regions
        region_counter = Counter(a.get("region", "Global") for a in articles)
        top_regions = region_counter.most_common(5)

        # Breaking count
        breaking = [a for a in articles if a.get("urgency") == "breaking"]

        trends = {
            "top_categories": [{"category": c, "count": n} for c, n in top_categories],
            "top_tags": [{"tag": t, "count": n} for t, n in top_tags],
            "top_regions": [{"region": r, "count": n} for r, n in top_regions],
            "breaking_count": len(breaking),
            "total_articles": len(articles),
            "avg_relevance": round(sum(a.get("relevance_score", 0) for a in articles) / len(articles), 2),
            "summary": "",
        }

        # Optional LLM trend summary
        if self.llm:
            trends["summary"] = self._generate_summary(articles, trends)
        else:
            top_cat_str = ", ".join(c for c, _ in top_categories[:3])
            top_tag_str = ", ".join(t for t, _ in top_tags[:5])
            trends["summary"] = (
                f"Analyzed {len(articles)} articles. "
                f"Top categories: {top_cat_str}. "
                f"Trending topics: {top_tag_str}. "
                f"Breaking stories: {len(breaking)}."
            )

        state["trends"] = trends
        logger.info("[%s] Trend analysis complete", self.name)
        return state

    def _generate_summary(self, articles: list[dict], trends: dict) -> str:
        titles = "\n".join(f"- {a['title']}" for a in articles[:15])
        prompt = (
            f"You are an intelligence analyst. Summarize the top trends "
            f"from these {len(articles)} articles in 3-4 sentences. "
            f"Focus on patterns and what matters most.\n\n"
            f"Headlines:\n{titles}"
        )
        try:
            resp = self.llm.invoke(prompt)
            return resp.content.strip()
        except Exception as exc:
            logger.warning("[trend] LLM summary failed: %s", exc)
            return trends.get("summary", "")

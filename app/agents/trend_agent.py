"""
Trend Analysis Agent.

Analyzes research results to identify patterns, emerging trends,
and actionable insights.
"""

from typing import Any

from app.agents.base import BaseAgent
from app.core.logger import logger


class TrendAgent(BaseAgent):
    """Processes research data and extracts trend insights."""

    name = "trend_analysis"

    def run(self, state: dict[str, Any]) -> dict[str, Any]:
        research = state.get("research_results", "")
        logger.info("[%s] Analyzing trends from research data", self.name)

        if self.llm:
            # TODO: add LLM chain for deeper trend extraction
            response = self.llm.invoke(
                f"Identify the top trends from this research:\n{research}"
            )
            state["trend_results"] = response.content
        else:
            state["trend_results"] = (
                f"[Stub] Trend analysis identified 2 patterns: "
                f"(1) Upward momentum — interest growing quarter over quarter. "
                f"(2) Cross-sector convergence — adoption spreading beyond early movers. "
                f"Source data length: {len(research)} chars."
            )
        return state

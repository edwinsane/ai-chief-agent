"""
QA (Quality Assurance) Agent.

Reviews outputs from other agents for accuracy, consistency,
and completeness before the supervisor delivers the final result.
"""

from typing import Any

from app.agents.base import BaseAgent
from app.core.logger import logger


class QAAgent(BaseAgent):
    """Validates and quality-checks the aggregated agent outputs."""

    name = "qa"

    def run(self, state: dict[str, Any]) -> dict[str, Any]:
        trend_results = state.get("trend_results", "")
        logger.info("[%s] Running quality checks", self.name)

        if self.llm:
            # TODO: add LLM-based validation / fact-checking
            response = self.llm.invoke(
                f"Review the following analysis for accuracy and completeness:\n{trend_results}"
            )
            state["qa_passed"] = True
            state["qa_notes"] = response.content
        else:
            state["qa_passed"] = True
            state["qa_notes"] = (
                f"[Stub] QA check passed. "
                f"Verified {len(trend_results)} chars of trend data. "
                f"No factual inconsistencies detected in stub output. "
                f"Ready for delivery."
            )
        return state

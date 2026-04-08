"""
Research Agent.

Responsible for gathering raw information on a given topic.
In future versions this will use tool-calling (web search, APIs, etc.).
For now it is a stub that demonstrates the agent contract.
"""

from typing import Any

from app.agents.base import BaseAgent
from app.core.logger import logger


class ResearchAgent(BaseAgent):
    """Gathers information and feeds findings into the shared state."""

    name = "research"

    def run(self, state: dict[str, Any]) -> dict[str, Any]:
        topic = state.get("topic", "general")
        logger.info("[%s] Researching topic: %s", self.name, topic)

        if self.llm:
            # TODO: use LLM tool-calling (web search, retriever) here
            response = self.llm.invoke(f"Research the following topic briefly: {topic}")
            state["research_results"] = response.content
        else:
            state["research_results"] = (
                f"[Stub] Research found 3 key insights on '{topic}': "
                f"(1) '{topic}' is gaining traction across multiple industries. "
                f"(2) Recent breakthroughs suggest accelerated adoption in 2026. "
                f"(3) Experts highlight both opportunities and regulatory challenges."
            )
        return state

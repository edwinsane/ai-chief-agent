"""
Base agent class.

All subagents inherit from BaseAgent to share common setup
(LLM instance, logging, state schema).

When no OPENAI_API_KEY is set, agents run in stub mode —
self.llm is None and each agent uses local placeholder logic.
Set the key to switch to real LLM calls automatically.
"""

from abc import ABC, abstractmethod
from typing import Any

from app.core.config import settings
from app.core.logger import logger


class BaseAgent(ABC):
    """Abstract base for every agent in the system."""

    name: str = "base"

    def __init__(self) -> None:
        if settings.llm_enabled:
            from langchain_openai import ChatOpenAI

            self.llm = ChatOpenAI(
                model=settings.llm_model,
                temperature=settings.llm_temperature,
                api_key=settings.openai_api_key,
            )
            logger.info("Initialized agent: %s (LLM mode)", self.name)
        else:
            self.llm = None
            logger.info("Initialized agent: %s (stub mode — no API key)", self.name)

    @abstractmethod
    def run(self, state: dict[str, Any]) -> dict[str, Any]:
        """Execute the agent's task and return updated state."""
        ...

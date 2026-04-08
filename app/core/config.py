"""
Application configuration.

Loads settings from environment variables with sensible defaults.
Uses pydantic-settings for validation when available, falls back to dataclass.
"""

import os
from dataclasses import dataclass, field


@dataclass
class Settings:
    """Central configuration for the multi-agent system."""

    # LLM
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    llm_model: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
    llm_temperature: float = float(os.getenv("LLM_TEMPERATURE", "0"))

    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///data/agents.db")

    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    # Application
    app_name: str = "AI-Chief-Agent"
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"

    @property
    def llm_enabled(self) -> bool:
        """True when a valid API key is configured."""
        return bool(self.openai_api_key and self.openai_api_key != "sk-your-key-here")


# Singleton instance — import this wherever config is needed
settings = Settings()

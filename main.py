"""
Entry point for the AI Chief Agent system.

Usage:
    python main.py                      # run with default topic
    python main.py "artificial intelligence"  # run with a custom topic
"""

import sys

from app.agents.supervisor import SupervisorAgent
from app.core.logger import logger
from app.storage.database import init_db, save_run


def main() -> None:
    topic = sys.argv[1] if len(sys.argv) > 1 else "AI trends 2026"

    logger.info("=== Starting AI Chief Agent ===")

    # Ensure database tables exist
    init_db()

    # Run the agent pipeline
    supervisor = SupervisorAgent()
    result = supervisor.run(topic)

    # Persist the result
    save_run(topic, result)

    logger.info("=== Pipeline finished ===")
    logger.info("Result: %s", result)


if __name__ == "__main__":
    main()

"""
Entry point for the AI Chief Agent system.

Usage:
    python main.py                              # full intelligence sweep
    python main.py "artificial intelligence"    # custom topic
"""

import sys

from app.agents.supervisor import SupervisorAgent
from app.core.logger import logger
from app.storage.database import init_db, save_articles, save_run


def main() -> None:
    topic = sys.argv[1] if len(sys.argv) > 1 else "intelligence sweep"

    logger.info("=== Starting AI Chief Agent ===")

    init_db()

    supervisor = SupervisorAgent()
    result = supervisor.run(topic)

    # Extract articles before saving the run (articles are large)
    articles = result.pop("articles", [])

    # Save run metadata
    run_id = save_run(topic, result)

    # Save classified articles linked to this run
    if articles:
        save_articles(run_id, articles)

    logger.info("=== Pipeline finished ===")
    logger.info(
        "Run #%d: %d articles collected, QA %s",
        run_id,
        len(articles),
        "passed" if result.get("qa_passed") else "issues found",
    )


if __name__ == "__main__":
    main()

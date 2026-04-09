"""
Entry point for the AI Chief Agent system.

Usage:
    python main.py                              # full intelligence sweep
    python main.py "artificial intelligence"    # custom topic
"""

import sys

from app.agents.supervisor import SupervisorAgent
from app.core.logger import logger
from app.storage.database import init_db, save_articles, save_briefing, save_run


def main() -> None:
    topic = sys.argv[1] if len(sys.argv) > 1 else "intelligence sweep"

    logger.info("=== Starting AI Chief Agent ===")

    init_db()

    supervisor = SupervisorAgent()
    result = supervisor.run(topic)

    # Extract large objects before saving the run
    articles = result.pop("articles", [])
    briefing = result.pop("macro_briefing", {})

    # Save run metadata
    run_id = save_run(topic, result)

    # Save classified articles
    if articles:
        save_articles(run_id, articles)

    # Save macro intelligence briefing
    if briefing:
        save_briefing(run_id, briefing)

    logger.info("=== Pipeline finished ===")
    logger.info(
        "Run #%d: %d articles, macro theme: %s, QA %s",
        run_id,
        len(articles),
        briefing.get("top_theme", "N/A"),
        "passed" if result.get("qa_passed") else "issues found",
    )


if __name__ == "__main__":
    main()

"""
QA (Quality Assurance) Agent.

Validates classified articles for:
- Missing required fields
- Suspicious duplicates
- Confidence thresholds
- Optional LLM review
"""

from typing import Any

from app.agents.base import BaseAgent
from app.core.logger import logger


class QAAgent(BaseAgent):
    """Validates article quality before storage and display."""

    name = "qa"

    def run(self, state: dict[str, Any]) -> dict[str, Any]:
        articles = state.get("articles", [])
        logger.info("[%s] Running quality checks on %d articles", self.name, len(articles))

        issues: list[str] = []
        valid_articles: list[dict] = []

        for a in articles:
            article_issues = self._check_article(a)
            if article_issues:
                issues.extend(article_issues)
            else:
                valid_articles.append(a)

        # Duplicate check
        titles_seen: set[str] = set()
        deduped: list[dict] = []
        for a in valid_articles:
            key = a["title"].lower().strip()
            if key not in titles_seen:
                titles_seen.add(key)
                deduped.append(a)
            else:
                issues.append(f"Duplicate removed: {a['title'][:60]}")

        passed = len(issues) == 0 or len(deduped) > 0

        # Optional LLM review of the batch
        qa_notes = ""
        if self.llm and deduped:
            qa_notes = self._llm_review(deduped)
        else:
            qa_notes = (
                f"QA complete. {len(deduped)} articles passed, "
                f"{len(articles) - len(deduped)} filtered. "
                f"Issues: {len(issues)}."
            )

        state["articles"] = deduped
        state["article_count"] = len(deduped)
        state["qa_passed"] = passed
        state["qa_notes"] = qa_notes
        state["qa_issues"] = issues
        logger.info("[%s] QA done: %d passed, %d issues", self.name, len(deduped), len(issues))
        return state

    @staticmethod
    def _check_article(article: dict) -> list[str]:
        """Return a list of issues, empty if article is valid."""
        problems = []
        if not article.get("title", "").strip():
            problems.append("Missing title")
        if article.get("title", "").strip().lower() in ("[removed]", "null", "none"):
            problems.append(f"Invalid title: {article['title']}")
        if article.get("confidence_score", 0) < 0.2:
            problems.append(f"Low confidence: {article.get('title', '')[:60]}")
        return problems

    def _llm_review(self, articles: list[dict]) -> str:
        titles = "\n".join(f"- {a['title']}" for a in articles[:10])
        prompt = (
            f"You are a QA reviewer. Briefly assess the quality and "
            f"diversity of these {len(articles)} intelligence items. "
            f"Note any concerns in 2-3 sentences.\n\n{titles}"
        )
        try:
            resp = self.llm.invoke(prompt)
            return resp.content.strip()
        except Exception as exc:
            logger.warning("[qa] LLM review failed: %s", exc)
            return f"QA passed. {len(articles)} articles validated."

"""
Article classifier.

Assigns categories, tags, region, urgency, and scores to raw articles
using keyword rules. Optionally enriches with LLM when available.
"""

from __future__ import annotations

from app.core.categories import (
    CATEGORIES,
    REGION_KEYWORDS,
    TOPIC_TAGS,
    URGENCY_KEYWORDS,
)


def classify(article: dict) -> dict:
    """
    Take a raw article dict (must have at least 'title') and return
    a fully classified article with all intelligence fields populated.
    """
    text = _searchable_text(article)

    category = _detect_category(text)
    tags = _detect_tags(text)
    region = _detect_region(text)
    urgency = _detect_urgency(text)
    relevance = _compute_relevance(category, tags, urgency)
    ai_relevance = _ai_relevance_label(category, tags)
    market_impact = _market_impact_label(category, tags, text)

    return {
        "title": article.get("title", ""),
        "source": article.get("source", "Unknown"),
        "url": article.get("url", ""),
        "published_at": article.get("published_at", ""),
        "short_summary": article.get("description", article.get("title", ""))[:500],
        "why_it_matters": "",  # populated by LLM enrichment or left empty
        "tags": tags,
        "relevance_score": relevance,
        "category": category,
        "region": region,
        "urgency": urgency,
        "market_impact": market_impact,
        "ai_relevance": ai_relevance,
        "confidence_score": 0.7 if tags else 0.5,
    }


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _searchable_text(article: dict) -> str:
    parts = [
        article.get("title", ""),
        article.get("description", ""),
        article.get("content", ""),
    ]
    return " ".join(p for p in parts if p).lower()


def _detect_category(text: str) -> str:
    scores: dict[str, int] = {}
    for cat, keywords in CATEGORIES.items():
        hits = sum(1 for kw in keywords if kw in text)
        if hits:
            scores[cat] = hits
    if not scores:
        return "Global News"
    return max(scores, key=scores.get)


def _detect_tags(text: str) -> list[str]:
    found: list[str] = []
    for tag, keywords in TOPIC_TAGS.items():
        if any(kw in text for kw in keywords):
            found.append(tag)
    return found


def _detect_region(text: str) -> str:
    scores: dict[str, int] = {}
    for region, keywords in REGION_KEYWORDS.items():
        hits = sum(1 for kw in keywords if kw in text)
        if hits:
            scores[region] = hits
    if not scores:
        return "Global"
    return max(scores, key=scores.get)


def _detect_urgency(text: str) -> str:
    for level in ("breaking", "high", "medium"):
        keywords = URGENCY_KEYWORDS[level]
        if any(kw in text for kw in keywords):
            return level
    return "low"


def _compute_relevance(category: str, tags: list[str], urgency: str) -> float:
    score = 0.3
    if category in ("AI", "AI Coding", "AI Trading"):
        score += 0.2
    if category == "Breaking News":
        score += 0.15
    score += min(len(tags) * 0.08, 0.3)
    urgency_bonus = {"breaking": 0.2, "high": 0.12, "medium": 0.05, "low": 0.0}
    score += urgency_bonus.get(urgency, 0.0)
    return round(min(score, 1.0), 2)


def _ai_relevance_label(category: str, tags: list[str]) -> str:
    if category in ("AI", "AI Coding", "AI Trading"):
        return "high"
    ai_tags = {"ai agents", "vibe coding", "coding copilots", "AI IDE tools",
               "trading bots", "quant AI", "crypto AI"}
    if ai_tags & set(tags):
        return "medium"
    return "low"


def _market_impact_label(category: str, tags: list[str], text: str) -> str:
    if category in ("Markets", "AI Trading"):
        return "high"
    if "market impact" in tags:
        return "high"
    market_words = ["crash", "surge", "plunge", "rally", "recession", "rate hike"]
    if any(w in text for w in market_words):
        return "medium"
    return "low"

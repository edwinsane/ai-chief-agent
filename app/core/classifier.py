"""
Article classifier — impact-weighted global intelligence scoring.

Assigns categories, tags, region, urgency, and multi-dimensional scores.
Scoring hierarchy: breaking/conflict > market-moving > AI/tech > general.
"""

from __future__ import annotations

from app.core.categories import (
    CATEGORIES,
    REGION_KEYWORDS,
    TOPIC_TAGS,
    URGENCY_KEYWORDS,
)


def classify(article: dict) -> dict:
    """Classify a raw article with full intelligence scoring."""
    text = _searchable_text(article)

    category = _detect_category(text)
    tags = _detect_tags(text)
    region = _detect_region(text)
    urgency = _detect_urgency(text)
    market_impact = _market_impact_label(category, tags, text)
    geo_significance = _geo_significance(category, tags, text)
    ai_relevance = _ai_relevance_label(category, tags)
    relevance = _compute_relevance(category, tags, urgency, market_impact, geo_significance)
    confidence = _compute_confidence(tags, urgency, category)

    return {
        "title": article.get("title", ""),
        "source": article.get("source", "Unknown"),
        "url": article.get("url", ""),
        "published_at": article.get("published_at", ""),
        "short_summary": article.get("description", article.get("title", ""))[:500],
        "why_it_matters": "",
        "tags": tags,
        "relevance_score": relevance,
        "category": category,
        "region": region,
        "urgency": urgency,
        "market_impact": market_impact,
        "ai_relevance": ai_relevance,
        "confidence_score": confidence,
    }


# ---------------------------------------------------------------------------
# Detection
# ---------------------------------------------------------------------------

def _searchable_text(article: dict) -> str:
    parts = [article.get("title", ""), article.get("description", ""), article.get("content", "")]
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
    return [tag for tag, keywords in TOPIC_TAGS.items() if any(kw in text for kw in keywords)]


def _detect_region(text: str) -> str:
    scores: dict[str, int] = {}
    for region, keywords in REGION_KEYWORDS.items():
        if not keywords:
            continue
        hits = sum(1 for kw in keywords if kw in text)
        if hits:
            scores[region] = hits
    return max(scores, key=scores.get) if scores else "Global"


def _detect_urgency(text: str) -> str:
    for level in ("breaking", "high", "medium"):
        if any(kw in text for kw in URGENCY_KEYWORDS[level]):
            return level
    return "low"


# ---------------------------------------------------------------------------
# Impact-weighted scoring
# Priority: breaking/conflict > market-moving > AI/tech > general
# ---------------------------------------------------------------------------

# Category impact tiers
_TIER_1 = {"Breaking News", "Military / Security"}          # highest
_TIER_2 = {"Geopolitics", "Sanctions", "Natural Disasters"}
_TIER_3 = {"Markets", "Energy", "Shipping / Supply Chain", "Infrastructure", "Crypto"}
_TIER_4 = {"AI", "AI Coding", "AI Trading"}
_TIER_5 = {"Global News"}                                    # lowest


def _compute_relevance(
    category: str, tags: list[str], urgency: str,
    market_impact: str, geo_significance: str,
) -> float:
    """Impact-weighted relevance score 0-1."""
    score = 0.15  # base

    # Category tier bonus
    if category in _TIER_1:
        score += 0.30
    elif category in _TIER_2:
        score += 0.25
    elif category in _TIER_3:
        score += 0.20
    elif category in _TIER_4:
        score += 0.18
    else:
        score += 0.05

    # Urgency bonus (biggest weight)
    score += {"breaking": 0.25, "high": 0.15, "medium": 0.06, "low": 0.0}.get(urgency, 0.0)

    # Market impact bonus
    score += {"high": 0.12, "medium": 0.06, "low": 0.0}.get(market_impact, 0.0)

    # Geopolitical significance bonus
    score += {"high": 0.10, "medium": 0.05, "low": 0.0}.get(geo_significance, 0.0)

    # Tag richness bonus (more tags = more signal)
    score += min(len(tags) * 0.04, 0.12)

    return round(min(score, 1.0), 2)


def _compute_confidence(tags: list[str], urgency: str, category: str) -> float:
    """Confidence in classification accuracy."""
    base = 0.4
    if tags:
        base += min(len(tags) * 0.08, 0.25)
    if urgency in ("breaking", "high"):
        base += 0.1
    if category not in ("Global News",):
        base += 0.1
    return round(min(base, 0.95), 2)


# ---------------------------------------------------------------------------
# Multi-dimensional impact labels
# ---------------------------------------------------------------------------

def _market_impact_label(category: str, tags: list[str], text: str) -> str:
    if category in ("Markets", "AI Trading", "Crypto"):
        return "high"
    high_tags = {"market crash", "market rally", "central banks", "sanctions", "energy crisis", "shipping disruption"}
    if high_tags & set(tags):
        return "high"
    market_words = ["crash", "surge", "plunge", "rally", "recession", "rate hike",
                    "rate cut", "tariff", "embargo", "oil price", "default"]
    if any(w in text for w in market_words):
        return "medium"
    if category in ("Energy", "Sanctions", "Shipping / Supply Chain"):
        return "medium"
    return "low"


def _geo_significance(category: str, tags: list[str], text: str) -> str:
    if category in ("Military / Security", "Geopolitics", "Sanctions"):
        return "high"
    high_tags = {"armed conflict", "nuclear risk", "sanctions", "cyber threats", "shipping disruption"}
    if high_tags & set(tags):
        return "high"
    geo_words = ["invasion", "airstrike", "casualties", "troops", "blockade",
                 "ceasefire", "escalation", "alliance", "nato"]
    if any(w in text for w in geo_words):
        return "medium"
    return "low"


def _ai_relevance_label(category: str, tags: list[str]) -> str:
    if category in ("AI", "AI Coding", "AI Trading"):
        return "high"
    ai_tags = {"ai agents", "vibe coding", "coding copilots", "AI IDE tools",
               "trading bots", "quant AI", "crypto AI", "ai regulation"}
    if ai_tags & set(tags):
        return "medium"
    return "low"

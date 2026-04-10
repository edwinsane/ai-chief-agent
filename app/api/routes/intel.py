"""
Intelligence endpoints — predictions, risk, themes, macro briefing, assets.
"""

from collections import Counter

from fastapi import APIRouter

from app.core.predictions import generate_outlook
from app.storage.database import get_articles, get_latest_briefing

router = APIRouter()


@router.get("/predictions")
def predictions():
    """Return 6H/24H predictive outlook computed from current articles."""
    articles = get_articles(limit=500)
    outlook = generate_outlook(articles)
    return {"predictions": outlook}


@router.get("/global-risk")
def global_risk():
    """
    Return a compact global risk pulse optimized for signal bars.
    Each signal has: level, score (0-1), detail text.
    """
    articles = get_articles(limit=500)
    outlook = generate_outlook(articles)

    cats = Counter(a.get("category", "") for a in articles)
    ai_count = cats.get("AI", 0) + cats.get("AI Coding", 0) + cats.get("AI Trading", 0)
    breaking = sum(1 for a in articles if a.get("urgency") == "breaking")

    return {
        "signals": {
            "escalation": outlook["escalation_risk"],
            "market": outlook["market_reaction"],
            "ai_momentum": outlook["ai_momentum"],
            "supply_chain": outlook["supply_chain_risk"],
            "energy": outlook["energy_sensitivity"],
        },
        "counts": {
            "total": len(articles),
            "breaking": breaking,
            "ai": ai_count,
            "conflict": outlook["signal_counts"]["conflict"],
            "market_sensitive": outlook["signal_counts"]["market"],
        },
        "overall_confidence": outlook["overall_confidence"],
        "watchlist": outlook["watchlist"],
    }


@router.get("/themes")
def themes():
    """Return topic/tag frequency analysis."""
    articles = get_articles(limit=500)
    tag_counter = Counter(t for a in articles for t in a.get("tags", []))
    cat_counter = Counter(a.get("category", "") for a in articles)

    return {
        "topics": [{"tag": t, "count": c} for t, c in tag_counter.most_common(20)],
        "categories": [{"category": c, "count": n} for c, n in cat_counter.most_common()],
    }


@router.get("/macro-summary")
def macro_summary():
    """Return the latest macro intelligence briefing."""
    row = get_latest_briefing()
    if not row:
        return {"briefing": None}
    return {"briefing": row["data"]}


@router.get("/assets")
def assets():
    """Return asset-class breakdown from the latest macro briefing."""
    row = get_latest_briefing()
    if not row or not row["data"]:
        return {"assets": [], "scenarios": {}}
    data = row["data"]
    return {
        "assets": data.get("asset_views", []),
        "scenarios": data.get("scenarios", {}),
        "top_theme": data.get("top_theme", ""),
        "overall_risk": data.get("overall_risk_level", "low"),
        "overall_confidence": data.get("overall_confidence", 0),
    }

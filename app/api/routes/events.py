"""
Event endpoints — articles, top story, filtering, detail.
"""

from collections import Counter
from typing import Optional

from fastapi import APIRouter, Query

from app.core.geo_coords import infer_coordinates
from app.storage.database import (
    get_article_count, get_articles, get_distinct_categories,
    get_distinct_regions, get_distinct_sources, get_freshness_info,
    get_qa_stats, get_run_count,
)

router = APIRouter()


@router.get("/events")
def list_events(
    category: Optional[str] = Query(None, description="Filter by category"),
    region: Optional[str] = Query(None, description="Filter by region"),
    urgency: Optional[str] = Query(None, description="Filter by urgency"),
    source: Optional[str] = Query(None, description="Filter by source"),
    min_relevance: float = Query(0.0, ge=0, le=1),
    keyword: Optional[str] = Query(None, description="Search titles & summaries"),
    limit: int = Query(100, ge=1, le=500),
):
    """Return filtered, scored, and sorted articles."""
    articles = get_articles(limit=500)

    if category:
        articles = [a for a in articles if a.get("category") == category]
    if region:
        articles = [a for a in articles if a.get("region") == region]
    if urgency:
        articles = [a for a in articles if a.get("urgency") == urgency]
    if source:
        articles = [a for a in articles if a.get("source") == source]
    if min_relevance > 0:
        articles = [a for a in articles if (a.get("relevance_score") or 0) >= min_relevance]
    if keyword:
        kw = keyword.lower()
        articles = [a for a in articles if kw in (a.get("title", "") + a.get("short_summary", "")).lower()]

    articles.sort(key=lambda a: a.get("relevance_score", 0), reverse=True)
    return {"count": len(articles[:limit]), "events": articles[:limit]}


@router.get("/events/{event_id}")
def event_detail(event_id: int):
    """Return full intelligence detail for a single event."""
    articles = get_articles(limit=500)
    for a in articles:
        if a.get("id") == event_id:
            lat, lon = infer_coordinates(a)
            a["lat"] = lat
            a["lon"] = lon
            return {"event": a}
    return {"error": "Event not found"}


@router.get("/top-story")
def top_story():
    """Return the single highest-relevance article."""
    articles = get_articles(limit=500)
    if not articles:
        return {"top_story": None}
    articles.sort(key=lambda a: a.get("relevance_score", 0), reverse=True)
    top = articles[0]
    lat, lon = infer_coordinates(top)
    top["lat"] = lat
    top["lon"] = lon
    return {"top_story": top}


@router.get("/events/stats/summary")
def event_stats():
    """Return aggregate statistics for the current event set."""
    articles = get_articles(limit=500)
    cats = Counter(a.get("category", "") for a in articles)
    urgencies = Counter(a.get("urgency", "low") for a in articles)
    regions = Counter(a.get("region", "Global") for a in articles)
    sources = Counter(a.get("source", "") for a in articles)

    return {
        "total_articles": get_article_count(),
        "total_runs": get_run_count(),
        "qa": get_qa_stats(),
        "freshness": get_freshness_info(),
        "categories": dict(cats.most_common()),
        "urgencies": dict(urgencies),
        "regions": dict(regions.most_common()),
        "sources": dict(sources.most_common(10)),
        "filters": {
            "available_categories": get_distinct_categories(),
            "available_regions": get_distinct_regions(),
            "available_sources": get_distinct_sources(),
        },
    }

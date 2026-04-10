"""
Map endpoints — geo markers, heatmap data, regional breakdown.
Optimized for Deck.gl / CesiumJS / Plotly globe consumption.
"""

from collections import Counter
from typing import Optional

from fastapi import APIRouter, Query

from app.core.geo_coords import infer_coordinates, get_country_iso
from app.storage.database import get_articles

router = APIRouter()

# Category → hex color for map layers
_CATEGORY_COLORS = {
    "AI": "#00D4FF", "AI Coding": "#4ECDC4", "AI Trading": "#45B7D1",
    "Geopolitics": "#FFB800", "Military / Security": "#FF5252",
    "Markets": "#BB86FC", "Crypto": "#96CEB4", "Energy": "#FFEAA7",
    "Shipping / Supply Chain": "#FF6B6B", "Natural Disasters": "#E17055",
    "Global News": "#4A6A8A", "Breaking News": "#FF5252",
    "Sanctions": "#fd79a8", "Infrastructure": "#a29bfe",
}

_URGENCY_RADIUS = {"breaking": 18, "high": 12, "medium": 8, "low": 5}


@router.get("/world-map")
def world_map(
    category: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    min_relevance: float = Query(0.0, ge=0, le=1),
):
    """
    Return geo-positioned event markers for a world map.

    Each marker includes lat, lon, size (urgency-based), color (category),
    and full event metadata for hover/click detail panels.

    Designed for direct consumption by:
    - Plotly scatter_geo
    - Deck.gl ScatterplotLayer
    - CesiumJS Entity API
    """
    articles = get_articles(limit=500)

    if category:
        articles = [a for a in articles if a.get("category") == category]
    if region:
        articles = [a for a in articles if a.get("region") == region]
    if min_relevance > 0:
        articles = [a for a in articles if (a.get("relevance_score") or 0) >= min_relevance]

    markers = []
    for a in articles:
        lat, lon = infer_coordinates(a)
        urg = a.get("urgency", "low")
        cat = a.get("category", "Global News")
        markers.append({
            "id": a.get("id"),
            "lat": lat,
            "lon": lon,
            "title": a.get("title", ""),
            "category": cat,
            "urgency": urg,
            "region": a.get("region", "Global"),
            "relevance": a.get("relevance_score", 0),
            "market_impact": a.get("market_impact", "low"),
            "source": a.get("source", ""),
            "published_at": a.get("published_at", ""),
            "summary": a.get("short_summary", ""),
            "tags": a.get("tags", []),
            # Visual properties (frontend can use directly)
            "radius": _URGENCY_RADIUS.get(urg, 5),
            "color": _CATEGORY_COLORS.get(cat, "#4A6A8A"),
            "country_iso": get_country_iso(a),
        })

    return {"count": len(markers), "markers": markers}


@router.get("/heatmap")
def heatmap_data():
    """
    Return weighted geo points for heatmap visualization.

    Each point has lat, lon, and a weight derived from
    urgency + relevance + market impact. Higher weight = hotter.

    Designed for:
    - Deck.gl HeatmapLayer
    - Plotly density_mapbox
    """
    articles = get_articles(limit=500)
    points = []
    for a in articles:
        lat, lon = infer_coordinates(a)
        # Compute heat weight
        urg_w = {"breaking": 1.0, "high": 0.7, "medium": 0.4, "low": 0.15}.get(a.get("urgency", "low"), 0.15)
        rel_w = a.get("relevance_score", 0)
        mkt_w = {"high": 0.4, "medium": 0.2, "low": 0.0}.get(a.get("market_impact", "low"), 0.0)
        weight = round(urg_w + rel_w + mkt_w, 2)
        points.append({"lat": lat, "lon": lon, "weight": weight, "category": a.get("category", "")})

    return {"count": len(points), "points": points}


@router.get("/regions")
def regional_breakdown():
    """Return event counts and risk levels per region."""
    articles = get_articles(limit=500)
    region_counter = Counter(a.get("region", "Global") for a in articles)
    region_urgency: dict[str, Counter] = {}
    for a in articles:
        r = a.get("region", "Global")
        if r not in region_urgency:
            region_urgency[r] = Counter()
        region_urgency[r][a.get("urgency", "low")] += 1

    regions = []
    for reg, count in region_counter.most_common():
        urg = region_urgency.get(reg, Counter())
        if urg.get("breaking", 0) >= 1 or count >= 8:
            risk = "critical"
        elif urg.get("high", 0) >= 2 or count >= 5:
            risk = "elevated"
        elif count >= 2:
            risk = "moderate"
        else:
            risk = "low"
        regions.append({
            "region": reg,
            "event_count": count,
            "risk_level": risk,
            "urgency_breakdown": dict(urg),
        })

    return {"regions": regions}

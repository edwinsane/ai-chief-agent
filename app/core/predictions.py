"""
Predictive intelligence layer.

Generates rule-based 6H and 24H outlooks from current article signals.
No LLM required — pure signal analysis from article metadata.
"""

from __future__ import annotations

from collections import Counter


def generate_outlook(articles: list[dict]) -> dict:
    """Generate 6-hour and 24-hour predictive outlook from articles."""
    if not articles:
        return _empty_outlook()

    cats = Counter(a.get("category", "") for a in articles)
    urgencies = Counter(a.get("urgency", "low") for a in articles)
    regions = Counter(a.get("region", "Global") for a in articles)
    tags = Counter(t for a in articles for t in a.get("tags", []))
    market_impacts = Counter(a.get("market_impact", "low") for a in articles)

    # Compute signal levels
    conflict_count = cats.get("Military / Security", 0) + cats.get("Geopolitics", 0)
    ai_count = cats.get("AI", 0) + cats.get("AI Coding", 0) + cats.get("AI Trading", 0)
    market_count = cats.get("Markets", 0) + cats.get("Crypto", 0)
    energy_count = cats.get("Energy", 0)
    supply_count = cats.get("Shipping / Supply Chain", 0) + cats.get("Infrastructure", 0)
    breaking_count = urgencies.get("breaking", 0)
    high_urgency = urgencies.get("high", 0)
    high_market_impact = market_impacts.get("high", 0)

    # === ESCALATION RISK ===
    if conflict_count >= 5 or breaking_count >= 3:
        escalation = {"level": "HIGH", "score": 0.82, "detail": f"{conflict_count} conflict signals, {breaking_count} breaking alerts. Elevated probability of follow-on events."}
    elif conflict_count >= 2 or breaking_count >= 1:
        escalation = {"level": "ELEVATED", "score": 0.55, "detail": f"{conflict_count} conflict signals detected. Monitor for escalation patterns."}
    else:
        escalation = {"level": "LOW", "score": 0.20, "detail": "No significant conflict signals. Baseline geopolitical risk."}

    # === MARKET REACTION ===
    if high_market_impact >= 3 or (breaking_count >= 2 and conflict_count >= 2):
        market_rx = {"level": "RISK-OFF LIKELY", "score": 0.75, "detail": f"{high_market_impact} high-impact market signals. Expect defensive positioning in equities, safe-haven bid."}
    elif high_market_impact >= 1 or market_count >= 3:
        market_rx = {"level": "VOLATILE", "score": 0.50, "detail": f"Mixed signals across {market_count} market articles. Two-way risk, headline-driven."}
    elif ai_count >= 5:
        market_rx = {"level": "RISK-ON BIAS", "score": 0.60, "detail": f"Strong AI/tech momentum ({ai_count} articles). Growth-sector bid likely."}
    else:
        market_rx = {"level": "NEUTRAL", "score": 0.35, "detail": "No strong directional signal. Markets likely range-bound."}

    # === AI MOMENTUM ===
    if ai_count >= 7:
        ai_momentum = {"level": "STRONG", "score": 0.85, "detail": f"{ai_count} AI-related articles. High sector attention — watch for breakout moves in AI equities."}
    elif ai_count >= 3:
        ai_momentum = {"level": "MODERATE", "score": 0.55, "detail": f"{ai_count} AI articles. Steady interest, selective opportunities."}
    else:
        ai_momentum = {"level": "QUIET", "score": 0.25, "detail": "Limited AI-specific news flow this cycle."}

    # === SUPPLY CHAIN RISK ===
    if supply_count >= 3 or tags.get("shipping disruption", 0) >= 1:
        supply_risk = {"level": "ELEVATED", "score": 0.65, "detail": f"{supply_count} supply-chain/shipping signals. Potential cost-push and delivery delays."}
    elif supply_count >= 1:
        supply_risk = {"level": "MODERATE", "score": 0.40, "detail": "Minor supply-chain signals. Watch for escalation."}
    else:
        supply_risk = {"level": "LOW", "score": 0.15, "detail": "No significant supply-chain disruption detected."}

    # === ENERGY SENSITIVITY ===
    if energy_count >= 3 or tags.get("energy crisis", 0) >= 1:
        energy_sens = {"level": "HIGH", "score": 0.70, "detail": f"{energy_count} energy signals. Oil/gas price sensitivity elevated."}
    elif energy_count >= 1:
        energy_sens = {"level": "MODERATE", "score": 0.40, "detail": "Some energy signals. Monitor for supply disruption catalysts."}
    else:
        energy_sens = {"level": "LOW", "score": 0.15, "detail": "Energy markets quiet this cycle."}

    # === OVERALL CONFIDENCE ===
    total = len(articles)
    signal_density = (breaking_count + high_urgency + conflict_count + high_market_impact) / max(total, 1)
    overall_confidence = round(min(0.40 + signal_density * 0.5 + min(total * 0.01, 0.15), 0.95), 2)

    # === TOP WATCHLIST ===
    watchlist = []
    if escalation["level"] in ("HIGH", "ELEVATED"):
        watchlist.append("Geopolitical escalation — monitor for military/diplomatic developments")
    if market_rx["level"] == "RISK-OFF LIKELY":
        watchlist.append("Risk-off positioning — watch safe-haven flows (gold, USD, bonds)")
    if ai_momentum["level"] == "STRONG":
        watchlist.append("AI sector momentum — watch for breakout in AI equities/infrastructure")
    if supply_risk["level"] == "ELEVATED":
        watchlist.append("Supply-chain disruption — shipping rates, semiconductor availability")
    if energy_sens["level"] == "HIGH":
        watchlist.append("Energy price sensitivity — crude oil, natural gas, utility costs")
    top_region = regions.most_common(1)[0][0] if regions else "Global"
    if top_region != "Global":
        watchlist.append(f"Regional focus: {top_region} — highest article concentration")
    if not watchlist:
        watchlist.append("No elevated signals — maintain baseline monitoring")

    return {
        "escalation_risk": escalation,
        "market_reaction": market_rx,
        "ai_momentum": ai_momentum,
        "supply_chain_risk": supply_risk,
        "energy_sensitivity": energy_sens,
        "overall_confidence": overall_confidence,
        "watchlist": watchlist,
        "signal_counts": {
            "total": total,
            "breaking": breaking_count,
            "high_urgency": high_urgency,
            "conflict": conflict_count,
            "ai": ai_count,
            "market": market_count,
            "energy": energy_count,
            "supply": supply_count,
        },
    }


def _empty_outlook() -> dict:
    return {
        "escalation_risk": {"level": "NO DATA", "score": 0.0, "detail": "Run a sweep to generate predictions."},
        "market_reaction": {"level": "NO DATA", "score": 0.0, "detail": ""},
        "ai_momentum": {"level": "NO DATA", "score": 0.0, "detail": ""},
        "supply_chain_risk": {"level": "NO DATA", "score": 0.0, "detail": ""},
        "energy_sensitivity": {"level": "NO DATA", "score": 0.0, "detail": ""},
        "overall_confidence": 0.0,
        "watchlist": ["No data available"],
        "signal_counts": {"total": 0, "breaking": 0, "high_urgency": 0, "conflict": 0, "ai": 0, "market": 0, "energy": 0, "supply": 0},
    }

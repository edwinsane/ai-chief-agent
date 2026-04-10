"""
Macro intelligence rules engine.

Maps headline keywords to asset-class impacts, directional views,
scenario logic, and risk triggers. This is the backbone of the
MacroIntelAgent's rule-based briefing generation.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Asset class definitions
# ---------------------------------------------------------------------------

ASSET_CLASSES: dict[str, dict] = {
    "crude_oil": {
        "label": "Crude Oil / WTI",
        "emoji": "🛢️",
        "baseline": "Sensitive to Middle East supply risk, OPEC policy, and global demand outlook.",
    },
    "gold": {
        "label": "Gold / XAU",
        "emoji": "🥇",
        "baseline": "Safe-haven bid on geopolitical risk, inversely correlated with real yields.",
    },
    "sp500": {
        "label": "S&P 500 / Nasdaq",
        "emoji": "📈",
        "baseline": "Risk-on barometer. Reacts to earnings, Fed policy, and macro sentiment.",
    },
    "crypto": {
        "label": "Crypto / BTC",
        "emoji": "₿",
        "baseline": "Risk-on digital asset. Moves with liquidity conditions and regulatory headlines.",
    },
    "energy_sector": {
        "label": "Energy Sector",
        "emoji": "⚡",
        "baseline": "Follows crude direction. Amplified by capex cycles and green-transition policy.",
    },
    "defense_sector": {
        "label": "Defense Sector",
        "emoji": "🛡️",
        "baseline": "Benefits from geopolitical escalation and government spending increases.",
    },
    "grains": {
        "label": "Grains / Fertilizers",
        "emoji": "🌾",
        "baseline": "Supply-chain sensitive. Reacts to conflict in breadbasket regions and sanctions.",
    },
}

# ---------------------------------------------------------------------------
# Keyword → asset relevance mapping
# Each keyword triggers one or more assets with a directional bias.
# direction: "up", "down", "volatile", "neutral"
# ---------------------------------------------------------------------------

KEYWORD_ASSET_MAP: list[dict] = [
    # === GLOBAL CONFLICT / MILITARY ===
    {"keywords": ["armed conflict", "military operation", "invasion", "airstrike", "troop deployment", "drone strike"],
     "assets": {"crude_oil": "up", "gold": "up", "sp500": "down", "defense_sector": "up"},
     "theme": "Armed conflict / military action", "risk_level": "high"},

    {"keywords": ["ceasefire", "peace talk", "de-escalat", "diplomatic resolution", "peace agreement"],
     "assets": {"crude_oil": "down", "gold": "down", "sp500": "up", "defense_sector": "down"},
     "theme": "De-escalation / ceasefire", "risk_level": "medium"},

    {"keywords": ["nuclear threat", "nuclear test", "nuclear weapon", "nuclear deal"],
     "assets": {"gold": "up", "sp500": "down", "defense_sector": "up", "crude_oil": "up"},
     "theme": "Nuclear risk escalation", "risk_level": "high"},

    {"keywords": ["cyberattack", "cyber warfare", "ransomware", "infrastructure attack"],
     "assets": {"sp500": "down", "gold": "up"},
     "theme": "Cyber / infrastructure threat", "risk_level": "high"},

    {"keywords": ["terror attack", "terrorist", "mass casualty"],
     "assets": {"sp500": "down", "gold": "up", "defense_sector": "up"},
     "theme": "Terror / security event", "risk_level": "high"},

    # === REGIONAL (triggered by events, not by default) ===
    {"keywords": ["iran", "tehran", "irgc", "hormuz", "strait of hormuz"],
     "assets": {"crude_oil": "up", "gold": "up", "sp500": "down", "defense_sector": "up", "energy_sector": "up"},
     "theme": "Middle East oil supply risk", "risk_level": "high"},

    {"keywords": ["israel", "gaza", "lebanon", "hezbollah", "hamas"],
     "assets": {"crude_oil": "up", "gold": "up", "sp500": "volatile", "defense_sector": "up"},
     "theme": "Israel-regional conflict", "risk_level": "high"},

    {"keywords": ["ukraine", "russia", "kremlin", "putin"],
     "assets": {"crude_oil": "up", "gold": "up", "grains": "up", "sp500": "down", "defense_sector": "up", "energy_sector": "up"},
     "theme": "Russia-Ukraine conflict", "risk_level": "high"},

    {"keywords": ["taiwan strait", "china military", "south china sea"],
     "assets": {"sp500": "down", "crypto": "volatile", "gold": "up", "defense_sector": "up"},
     "theme": "China-Taiwan tensions", "risk_level": "high"},

    # === MONETARY POLICY / MACRO ===
    {"keywords": ["federal reserve", "interest rate", "fomc", "powell", "central bank"],
     "assets": {"sp500": "volatile", "gold": "volatile", "crypto": "volatile"},
     "theme": "Central bank policy", "risk_level": "medium"},

    {"keywords": ["rate cut", "dovish", "easing", "stimulus"],
     "assets": {"sp500": "up", "gold": "up", "crypto": "up"},
     "theme": "Dovish pivot / easing", "risk_level": "low"},

    {"keywords": ["rate hike", "hawkish", "tightening"],
     "assets": {"sp500": "down", "gold": "down", "crypto": "down"},
     "theme": "Hawkish tightening", "risk_level": "medium"},

    # === SANCTIONS / TRADE ===
    {"keywords": ["sanction", "trade war", "tariff", "embargo", "export ban", "trade restriction"],
     "assets": {"sp500": "down", "gold": "up", "crude_oil": "up", "grains": "up"},
     "theme": "Sanctions / trade disruption", "risk_level": "high"},

    # === ENERGY / SUPPLY ===
    {"keywords": ["opec", "opec+", "oil production", "oil cut", "crude inventory"],
     "assets": {"crude_oil": "volatile", "energy_sector": "volatile"},
     "theme": "OPEC / energy supply", "risk_level": "medium"},

    {"keywords": ["shipping lane", "suez canal", "panama canal", "port closure", "maritime security"],
     "assets": {"crude_oil": "up", "grains": "up", "sp500": "down"},
     "theme": "Shipping / waterway disruption", "risk_level": "high"},

    {"keywords": ["supply chain", "chip shortage", "semiconductor shortage", "logistics crisis"],
     "assets": {"sp500": "down"},
     "theme": "Supply chain disruption", "risk_level": "medium"},

    # === CRYPTO ===
    {"keywords": ["bitcoin", "ethereum", "crypto regulation", "sec crypto", "stablecoin", "crypto exchange"],
     "assets": {"crypto": "volatile"},
     "theme": "Crypto markets / regulation", "risk_level": "medium"},

    # === AI / TECH ===
    {"keywords": ["artificial intelligence", "openai", "nvidia", "ai chip", "ai regulation", "ai model"],
     "assets": {"sp500": "up"},
     "theme": "AI sector momentum", "risk_level": "low"},

    # === NATURAL DISASTER ===
    {"keywords": ["earthquake", "tsunami", "hurricane", "flood", "wildfire", "volcanic eruption", "typhoon"],
     "assets": {"sp500": "down", "gold": "up", "crude_oil": "volatile"},
     "theme": "Natural disaster", "risk_level": "medium"},

    # === INFRASTRUCTURE ===
    {"keywords": ["power outage", "grid failure", "internet outage", "pipeline explosion", "dam failure"],
     "assets": {"sp500": "down", "energy_sector": "volatile"},
     "theme": "Infrastructure disruption", "risk_level": "medium"},

    # --- Inflation ---
    {"keywords": ["inflation", "cpi", "ppi", "consumer price"],
     "assets": {"gold": "up", "sp500": "volatile", "crypto": "volatile"},
     "theme": "Inflation data", "risk_level": "medium"},
]


# ---------------------------------------------------------------------------
# Scenario templates
# ---------------------------------------------------------------------------

SCENARIO_TEMPLATES: dict[str, dict[str, str]] = {
    "Armed conflict / military action": {
        "bull_case": "Conflict contained and ceasefire reached — risk premium unwinds, equities recover, commodities retrace.",
        "base_case": "Hostilities continue but localized — defense outperforms, commodities elevated, equities range-bound.",
        "risk_case": "Escalation or spillover to major powers — severe risk-off, flight to gold and USD, energy spikes.",
    },
    "Nuclear risk escalation": {
        "bull_case": "Diplomatic resolution, test moratorium — risk premium unwinds rapidly.",
        "base_case": "Rhetoric stays elevated but no action — markets adapt, defense bid persists.",
        "risk_case": "Actual test or deployment threat — extreme risk-off, gold surges, equities crater.",
    },
    "Cyber / infrastructure threat": {
        "bull_case": "Attack contained, systems restored — markets shrug off after initial dip.",
        "base_case": "Ongoing cyber campaign — cybersecurity stocks bid, broad markets nervous.",
        "risk_case": "Critical infrastructure compromised — cascading failures, economic disruption.",
    },
    "Terror / security event": {
        "bull_case": "Isolated incident, rapid response — markets recover within sessions.",
        "base_case": "Heightened alert status — defense bid, travel and consumer discretionary pressured.",
        "risk_case": "Coordinated multi-site attack — sustained risk-off, policy response uncertainty.",
    },
    "Middle East oil supply risk": {
        "bull_case": "Diplomacy succeeds — crude retraces, risk assets recover, defense gives back gains.",
        "base_case": "Tensions persist but contained — crude elevated, gold bid, equities choppy.",
        "risk_case": "Strait of Hormuz disruption — crude spikes, broad risk-off, flight to gold and USD.",
    },
    "De-escalation / ceasefire": {
        "bull_case": "Ceasefire becomes durable peace — crude drops sharply, risk-on rally, defense sector fades.",
        "base_case": "Ceasefire holds temporarily — gradual normalization, crude drifts lower, moderate equity relief.",
        "risk_case": "Ceasefire collapses — sharp reversal in crude and gold, renewed risk-off positioning.",
    },
    "Israel-regional conflict": {
        "bull_case": "Conflict contained and diplomatic resolution — risk premium unwinds, crude normalizes.",
        "base_case": "Ongoing hostilities but limited escalation — elevated crude, gold supported, equities uncertain.",
        "risk_case": "Regional spillover to broader Middle East — supply disruption fears, sharp risk-off.",
    },
    "Russia-Ukraine conflict": {
        "bull_case": "Peace negotiations progress — grain exports resume, energy prices ease, European equities rally.",
        "base_case": "Frozen conflict continues — grains and energy stay elevated, defense spending persists.",
        "risk_case": "Escalation with NATO involvement — severe risk-off, energy crisis, gold and defense surge.",
    },
    "China-Taiwan tensions": {
        "bull_case": "Rhetoric cools, status quo maintained — tech recovers, supply chain fears ease.",
        "base_case": "Elevated tensions but no military action — semiconductor supply concerns persist, hedging activity rises.",
        "risk_case": "Military action or blockade — global supply chain shock, severe equity selloff, massive flight to safety.",
    },
    "Fed monetary policy": {
        "bull_case": "Dovish surprise — rate cuts accelerate, equities and crypto rally, gold supported.",
        "base_case": "Data-dependent hold — markets range-bound, gradual repricing.",
        "risk_case": "Hawkish surprise — yields spike, equities sell off, gold pressured short-term.",
    },
    "Dovish pivot": {
        "bull_case": "Multiple cuts signaled — risk assets surge, liquidity improves broadly.",
        "base_case": "Single cut delivered — modest rally, markets wait for guidance.",
        "risk_case": "Cut seen as panic response — initial rally fades, uncertainty increases.",
    },
    "Hawkish tightening": {
        "bull_case": "Inflation falls faster than expected — tightening cycle ends early.",
        "base_case": "Gradual tightening continues — equities grind lower, credit spreads widen.",
        "risk_case": "Overtightening causes recession — sharp equity decline, flight to bonds and gold.",
    },
    "Sanctions / trade disruption": {
        "bull_case": "Sanctions eased or circumvented — supply normalizes, risk premium fades.",
        "base_case": "Sanctions persist — affected commodities stay elevated, trade rerouting continues.",
        "risk_case": "Escalation to secondary sanctions — broader supply disruption, inflationary pressure.",
    },
    "Shipping / waterway disruption": {
        "bull_case": "Route reopens or rerouting succeeds — freight rates normalize, supply resumes.",
        "base_case": "Disruption persists — elevated shipping costs, commodity price pressure, longer delivery times.",
        "risk_case": "Multiple chokepoints compromised — global trade crisis, stagflation risk, severe commodity spikes.",
    },
    "Supply chain disruption": {
        "bull_case": "Bottlenecks clear, inventory rebuilds — manufacturing recovers, inflation eases.",
        "base_case": "Partial disruption continues — select sectors impacted, cost pass-through to consumers.",
        "risk_case": "Cascading shortages — production halts, earnings downgrades, inflationary spiral.",
    },
    "Infrastructure disruption": {
        "bull_case": "Systems restored quickly — minimal economic impact, infrastructure spending accelerates.",
        "base_case": "Partial recovery — regional economic drag, insurance and rebuild costs.",
        "risk_case": "Widespread failure — economic paralysis in affected region, contagion risk.",
    },
    "Crypto markets / regulation": {
        "bull_case": "Regulatory clarity favors adoption — crypto rallies, institutional inflows increase.",
        "base_case": "Mixed regulatory signals — crypto volatile, market structure evolves gradually.",
        "risk_case": "Major crackdown or exchange failure — crypto selloff, contagion to risk assets.",
    },
    "Natural disaster": {
        "bull_case": "Damage contained, rapid recovery — markets stabilize quickly.",
        "base_case": "Moderate economic impact — regional disruption, insurance sector hit, temporary commodity moves.",
        "risk_case": "Major infrastructure destruction — prolonged supply chain disruption, GDP hit.",
    },
    "Inflation data": {
        "bull_case": "Inflation undershoots — rate cut expectations rise, risk-on.",
        "base_case": "Inline print — no surprise, markets steady.",
        "risk_case": "Hot inflation print — yields spike, equities sell, gold bid on stagflation fears.",
    },
}

# Default scenario for themes without a specific template
DEFAULT_SCENARIO: dict[str, str] = {
    "bull_case": "Situation resolves favorably — risk premium unwinds, assets normalize.",
    "base_case": "Current dynamics persist — markets adapt with elevated volatility.",
    "risk_case": "Situation deteriorates — risk-off positioning, safe havens bid.",
}


# ---------------------------------------------------------------------------
# Directional language templates
# ---------------------------------------------------------------------------

DIRECTION_LANGUAGE: dict[str, dict[str, str]] = {
    "up": {
        "reaction": "Likely bid higher on this catalyst.",
        "short_term": "Expect upward pressure in the near term.",
        "risk_trigger": "Reverses if catalyst narrative fades or opposing data emerges.",
    },
    "down": {
        "reaction": "Likely offered lower on this catalyst.",
        "short_term": "Expect downward pressure in the near term.",
        "risk_trigger": "Reverses if sentiment shifts or dovish / de-escalation surprise.",
    },
    "volatile": {
        "reaction": "Whipsaw likely — headline-driven two-way risk.",
        "short_term": "Expect range expansion and elevated volatility.",
        "risk_trigger": "Settles once clarity emerges on the catalyst direction.",
    },
    "neutral": {
        "reaction": "Limited direct impact expected.",
        "short_term": "Likely range-bound absent further developments.",
        "risk_trigger": "Watch for second-order effects or contagion from related assets.",
    },
}


# ---------------------------------------------------------------------------
# Confidence scoring
# ---------------------------------------------------------------------------

def compute_asset_confidence(direction: str, num_supporting_headlines: int) -> float:
    """Return a 0-1 confidence score for an asset view."""
    base = {"up": 0.55, "down": 0.55, "volatile": 0.4, "neutral": 0.3}.get(direction, 0.3)
    headline_bonus = min(num_supporting_headlines * 0.08, 0.3)
    return round(min(base + headline_bonus, 0.95), 2)

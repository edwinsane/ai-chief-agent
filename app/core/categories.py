"""
Category and tag definitions for the global intelligence pipeline.

Designed for worldwide high-impact event detection — not region-specific.
Regions are filters, not focal points.
"""

# ---------------------------------------------------------------------------
# Categories — global high-impact event types
# ---------------------------------------------------------------------------
CATEGORIES: dict[str, list[str]] = {
    "AI": [
        "artificial intelligence", "machine learning", "deep learning",
        "neural network", "openai", "gpt", "llm", "large language model",
        "generative ai", "chatgpt", "gemini", "claude", "anthropic",
        "mistral", "meta ai", "hugging face", "transformer", "ai model",
        "ai safety", "ai regulation",
    ],
    "AI Coding": [
        "copilot", "code generation", "vibe coding", "cursor ide",
        "ai coding", "code assistant", "codex", "devin", "replit",
        "ai ide", "repo automation", "coding agent", "ai developer",
        "windsurf", "cline", "aider",
    ],
    "AI Trading": [
        "trading bot", "quant ai", "algorithmic trading", "crypto ai",
        "ai trading", "market prediction", "execution agent",
        "robo advisor", "fintech ai", "ai hedge fund",
    ],
    "Geopolitics": [
        "geopolit", "diplomatic crisis", "territorial dispute",
        "international tensions", "foreign policy", "defense pact",
        "arms deal", "security alliance", "peace negotiation",
        "ceasefire", "diplomatic breakdown",
    ],
    "Military / Security": [
        "warfare", "armed conflict", "military operation", "airstrike",
        "missile strike", "invasion", "combat zone", "defense spending",
        "nuclear weapon", "military buildup", "drone strike",
        "naval operation", "troop deployment", "arms race",
        "cyberattack", "cyber warfare", "terror attack",
    ],
    "Sanctions": [
        "sanction", "trade restriction", "embargo", "export ban",
        "trade war", "tariff", "asset freeze", "blacklist",
        "trade compliance", "import duty",
    ],
    "Markets": [
        "stock market", "s&p 500", "nasdaq", "dow jones", "bond",
        "federal reserve", "interest rate", "inflation", "gdp",
        "earnings", "ipo", "wall street", "forex", "commodity",
        "treasury", "central bank", "monetary policy", "recession",
        "yield curve", "rate cut", "rate hike",
    ],
    "Crypto": [
        "bitcoin", "ethereum", "crypto", "stablecoin", "defi",
        "blockchain", "nft", "web3", "crypto regulation",
        "sec crypto", "crypto exchange", "mining",
    ],
    "Energy": [
        "oil price", "crude oil", "renewable energy", "solar energy",
        "wind energy", "opec", "natural gas", "energy crisis",
        "petroleum", "ev battery", "hydrogen", "nuclear energy",
        "electricity grid", "energy transition", "lng",
    ],
    "Shipping / Supply Chain": [
        "shipping lane", "port closure", "supply chain",
        "strait of hormuz", "suez canal", "panama canal",
        "container shortage", "freight rate", "shipping disruption",
        "logistics crisis", "trade route", "maritime security",
        "port congestion", "semiconductor shortage",
    ],
    "Natural Disasters": [
        "earthquake", "tsunami", "hurricane", "typhoon", "flood",
        "wildfire", "volcanic eruption", "drought", "heat wave",
        "cyclone", "tornado", "landslide",
    ],
    "Infrastructure": [
        "power outage", "grid failure", "internet outage",
        "pipeline explosion", "bridge collapse", "dam failure",
        "infrastructure attack", "cable cut", "satellite failure",
        "data center outage",
    ],
    "Breaking News": [
        "breaking", "just in", "urgent", "alert", "developing story",
        "emergency", "flash",
    ],
    "Global News": [
        "world news", "global event", "international",
        "united nations", "summit", "treaty", "diplomacy",
    ],
}

# ---------------------------------------------------------------------------
# Topic tags — finer-grained labels (global scope)
# ---------------------------------------------------------------------------
TOPIC_TAGS: dict[str, list[str]] = {
    # AI / tech
    "ai agents": ["ai agent", "autonomous agent", "agent framework", "multi-agent"],
    "vibe coding": ["vibe coding", "vibe-coding"],
    "coding copilots": ["copilot", "code assistant", "code completion"],
    "repo automation": ["repo automation", "ci/cd ai", "github action ai", "devops ai"],
    "AI IDE tools": ["cursor", "windsurf", "cline", "ai ide", "aider"],
    "ai regulation": ["ai regulation", "ai safety", "ai governance", "ai policy"],
    # Trading / markets
    "trading bots": ["trading bot", "algo bot", "execution bot"],
    "quant AI": ["quant ai", "quantitative", "quant fund"],
    "crypto AI": ["crypto ai", "defi ai", "blockchain ai"],
    "market prediction": ["market prediction", "price forecast", "stock predict"],
    "execution agents": ["execution agent", "order routing", "smart execution"],
    "central banks": ["federal reserve", "ecb", "bank of japan", "central bank", "rate decision"],
    "market crash": ["market crash", "flash crash", "sell-off", "capitulation"],
    "market rally": ["market rally", "bull run", "all-time high", "risk-on"],
    # Geopolitical (global, not region-locked)
    "armed conflict": ["warfare", "armed conflict", "invasion", "airstrike", "military operation"],
    "sanctions": ["sanction", "embargo", "trade restriction", "asset freeze"],
    "shipping disruption": ["strait of hormuz", "suez canal", "panama canal", "shipping lane", "maritime"],
    "nuclear risk": ["nuclear weapon", "nuclear test", "nuclear threat", "nuclear deal"],
    "cyber threats": ["cyberattack", "ransomware", "cyber warfare", "data breach", "hacking"],
    # Supply / infrastructure
    "supply chain": ["supply chain", "chip shortage", "semiconductor", "logistics crisis"],
    "infrastructure": ["power outage", "grid failure", "pipeline", "internet outage"],
    "natural disaster": ["earthquake", "tsunami", "hurricane", "flood", "wildfire", "volcanic"],
    # Macro
    "global macro": ["global macro", "macro economy", "world economy"],
    "market impact": ["market impact", "market crash", "market rally", "volatility"],
    "energy crisis": ["energy crisis", "oil shock", "gas shortage", "blackout"],
}

# ---------------------------------------------------------------------------
# Regions — used as FILTERS, not focal points
# ---------------------------------------------------------------------------
REGION_KEYWORDS: dict[str, list[str]] = {
    "US": ["us ", "usa", "united states", "america", "wall street", "silicon valley", "washington", "pentagon", "white house"],
    "Europe": ["europe", "eu ", "uk ", "britain", "germany", "france", "ecb", "brussels", "nato", "london"],
    "Middle East": ["middle east", "iran", "iraq", "saudi", "israel", "gaza", "uae", "qatar", "syria", "lebanon", "hormuz"],
    "Asia Pacific": ["china", "japan", "india", "korea", "taiwan", "asean", "australia", "beijing", "tokyo", "southeast asia"],
    "Russia / CIS": ["russia", "moscow", "ukraine", "kremlin", "putin", "belarus"],
    "Africa": ["africa", "nigeria", "south africa", "kenya", "egypt", "ethiopia", "congo"],
    "Latin America": ["brazil", "mexico", "argentina", "latin america", "colombia", "venezuela", "chile"],
    "Global": [],
}

# ---------------------------------------------------------------------------
# Urgency keywords
# ---------------------------------------------------------------------------
URGENCY_KEYWORDS: dict[str, list[str]] = {
    "breaking": ["breaking", "just in", "urgent", "flash", "emergency", "alert"],
    "high": ["developing", "escalat", "crisis", "crash", "surge", "plunge",
             "attack", "strike", "explosion", "killed", "casualties",
             "collapse", "shutdown", "embargo"],
    "medium": ["update", "report", "announce", "plan", "proposal", "launch",
               "warning", "threat", "tension", "dispute", "investigation"],
    "low": [],
}

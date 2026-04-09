"""
Category and tag definitions for the intelligence pipeline.

All keyword-based classification rules live here.
Add new categories or tags by extending the dictionaries below.
"""

# ---------------------------------------------------------------------------
# Categories — each maps to a list of detection keywords (lowercase)
# ---------------------------------------------------------------------------
CATEGORIES: dict[str, list[str]] = {
    "AI": [
        "artificial intelligence", "machine learning", "deep learning",
        "neural network", "openai", "gpt", "llm", "large language model",
        "generative ai", "chatgpt", "gemini", "claude", "anthropic",
        "mistral", "meta ai", "hugging face", "transformer",
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
    "Global News": [
        "breaking news", "world news", "global event", "international",
        "united nations", "summit", "treaty", "diplomacy",
    ],
    "Geopolitics": [
        "geopolit", "warfare", "armed conflict", "sanction", "nato", "iran",
        "middle east", "china trade", "china military", "russia ukraine",
        "taiwan strait", "ukraine war", "ukraine conflict",
        "military strike", "defense spending", "nuclear weapon", "missile strike",
        "territorial dispute", "diplomatic crisis",
    ],
    "Energy": [
        "oil", "renewable", "solar", "wind energy", "opec", "natural gas",
        "energy crisis", "petroleum", "ev battery", "hydrogen",
        "nuclear energy", "electricity",
    ],
    "Markets": [
        "stock market", "s&p 500", "nasdaq", "dow jones", "bond",
        "federal reserve", "interest rate", "inflation", "gdp",
        "earnings", "ipo", "wall street", "forex", "commodity",
        "bitcoin", "ethereum", "crypto", "treasury",
    ],
    "Breaking News": [
        "breaking", "just in", "urgent", "alert", "developing story",
        "emergency", "flash",
    ],
}

# ---------------------------------------------------------------------------
# Topic tags — finer-grained labels
# ---------------------------------------------------------------------------
TOPIC_TAGS: dict[str, list[str]] = {
    "ai agents": ["ai agent", "autonomous agent", "agent framework", "multi-agent"],
    "vibe coding": ["vibe coding", "vibe-coding"],
    "coding copilots": ["copilot", "code assistant", "code completion"],
    "repo automation": ["repo automation", "ci/cd ai", "github action ai", "devops ai"],
    "AI IDE tools": ["cursor", "windsurf", "cline", "ai ide", "aider"],
    "trading bots": ["trading bot", "algo bot", "execution bot"],
    "quant AI": ["quant ai", "quantitative", "quant fund"],
    "crypto AI": ["crypto ai", "defi ai", "blockchain ai"],
    "market prediction": ["market prediction", "price forecast", "stock predict"],
    "execution agents": ["execution agent", "order routing", "smart execution"],
    "war / conflict": ["warfare", "armed conflict", "invasion", "airstrike", "combat zone", "military operation"],
    "Iran": ["iran", "tehran", "irgc", "iranian"],
    "Middle East": ["middle east", "saudi", "israel", "gaza", "lebanon", "syria"],
    "global macro": ["global macro", "macro economy", "world economy"],
    "market impact": ["market impact", "market crash", "market rally", "volatility"],
}

# ---------------------------------------------------------------------------
# Regions
# ---------------------------------------------------------------------------
REGION_KEYWORDS: dict[str, list[str]] = {
    "North America": ["us", "usa", "united states", "canada", "america", "wall street", "silicon valley", "washington"],
    "Europe": ["europe", "eu", "uk", "britain", "germany", "france", "ecb", "brussels"],
    "Middle East": ["middle east", "iran", "iraq", "saudi", "israel", "gaza", "uae", "qatar", "syria", "lebanon"],
    "Asia Pacific": ["china", "japan", "india", "korea", "taiwan", "asean", "australia", "beijing", "tokyo"],
    "Russia / CIS": ["russia", "moscow", "ukraine", "kremlin", "putin"],
    "Africa": ["africa", "nigeria", "south africa", "kenya", "egypt"],
    "Latin America": ["brazil", "mexico", "argentina", "latin america", "colombia"],
}

# ---------------------------------------------------------------------------
# Urgency keywords
# ---------------------------------------------------------------------------
URGENCY_KEYWORDS: dict[str, list[str]] = {
    "breaking": ["breaking", "just in", "urgent", "flash", "emergency", "alert"],
    "high": ["developing", "escalat", "crisis", "crash", "surge", "plunge"],
    "medium": ["update", "report", "announce", "plan", "proposal", "launch"],
    "low": [],  # default
}

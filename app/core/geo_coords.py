"""
Geo-coordinate mapping for intelligence map visualization.

Maps regions and country keywords to representative lat/lon coordinates
for plotting on a Plotly globe. When exact location is unknown, falls
back to the region centroid.
"""

from __future__ import annotations

# Country/city keyword → (lat, lon, country_iso3)
LOCATION_MAP: dict[str, tuple[float, float, str]] = {
    # North America
    "united states": (39.0, -98.0, "USA"), "us ": (39.0, -98.0, "USA"),
    "usa": (39.0, -98.0, "USA"), "america": (39.0, -98.0, "USA"),
    "washington": (38.9, -77.0, "USA"), "pentagon": (38.87, -77.05, "USA"),
    "wall street": (40.7, -74.0, "USA"), "silicon valley": (37.4, -122.0, "USA"),
    "new york": (40.7, -74.0, "USA"), "california": (36.7, -119.7, "USA"),
    "canada": (56.1, -106.3, "CAN"), "mexico": (23.6, -102.5, "MEX"),
    # Europe
    "uk ": (55.4, -3.4, "GBR"), "britain": (55.4, -3.4, "GBR"), "london": (51.5, -0.1, "GBR"),
    "germany": (51.2, 10.4, "DEU"), "berlin": (52.5, 13.4, "DEU"),
    "france": (46.2, 2.2, "FRA"), "paris": (48.9, 2.3, "FRA"),
    "brussels": (50.8, 4.4, "BEL"), "eu ": (50.8, 4.4, "BEL"),
    "nato": (50.8, 4.4, "BEL"),
    # Middle East
    "iran": (32.4, 53.7, "IRN"), "tehran": (35.7, 51.4, "IRN"),
    "hormuz": (26.6, 56.3, "IRN"),
    "israel": (31.0, 34.8, "ISR"), "gaza": (31.5, 34.5, "PSE"),
    "lebanon": (33.9, 35.9, "LBN"), "syria": (34.8, 38.9, "SYR"),
    "iraq": (33.2, 43.7, "IRQ"), "saudi": (23.9, 45.1, "SAU"),
    "uae": (23.4, 53.8, "ARE"), "qatar": (25.4, 51.2, "QAT"),
    "middle east": (29.0, 42.0, "SAU"),
    # Asia Pacific
    "china": (35.9, 104.2, "CHN"), "beijing": (39.9, 116.4, "CHN"),
    "japan": (36.2, 138.3, "JPN"), "tokyo": (35.7, 139.7, "JPN"),
    "india": (20.6, 78.9, "IND"), "korea": (37.6, 127.0, "KOR"),
    "taiwan": (23.7, 121.0, "TWN"), "australia": (-25.3, 133.8, "AUS"),
    "indonesia": (-0.8, 113.9, "IDN"), "jakarta": (-6.2, 106.8, "IDN"),
    "singapore": (1.3, 103.8, "SGP"), "vietnam": (14.1, 108.3, "VNM"),
    # Russia / CIS
    "russia": (61.5, 105.3, "RUS"), "moscow": (55.8, 37.6, "RUS"),
    "kremlin": (55.8, 37.6, "RUS"), "ukraine": (48.4, 31.2, "UKR"),
    # Africa
    "nigeria": (9.1, 8.7, "NGA"), "south africa": (-30.6, 22.9, "ZAF"),
    "kenya": (-0.02, 37.9, "KEN"), "egypt": (26.8, 30.8, "EGY"),
    "ethiopia": (9.1, 40.5, "ETH"), "congo": (-4.0, 21.8, "COD"),
    "africa": (2.0, 23.0, "COD"),
    # Latin America
    "brazil": (-14.2, -51.9, "BRA"), "argentina": (-38.4, -63.6, "ARG"),
    "colombia": (4.6, -74.3, "COL"), "venezuela": (6.4, -66.6, "VEN"),
    "chile": (-35.7, -71.5, "CHL"), "latin america": (-14.2, -51.9, "BRA"),
    # Shipping chokepoints
    "suez canal": (30.4, 32.3, "EGY"), "panama canal": (9.1, -79.7, "PAN"),
    "strait of hormuz": (26.6, 56.3, "IRN"),
    "south china sea": (12.0, 113.0, "CHN"),
}

# Region centroids (fallback)
REGION_CENTROIDS: dict[str, tuple[float, float]] = {
    "US": (39.0, -98.0),
    "North America": (45.0, -100.0),
    "Europe": (50.0, 10.0),
    "Middle East": (29.0, 42.0),
    "Asia Pacific": (25.0, 105.0),
    "Russia / CIS": (55.0, 60.0),
    "Africa": (2.0, 23.0),
    "Latin America": (-15.0, -60.0),
    "Global": (20.0, 0.0),
}


def infer_coordinates(article: dict) -> tuple[float, float]:
    """Infer lat/lon from article text and region metadata."""
    text = (article.get("title", "") + " " + article.get("short_summary", "")).lower()

    # Try specific location keywords first
    for keyword, (lat, lon, _) in LOCATION_MAP.items():
        if keyword in text:
            return (lat, lon)

    # Fall back to region centroid
    region = article.get("region", "Global")
    return REGION_CENTROIDS.get(region, REGION_CENTROIDS["Global"])


def get_country_iso(article: dict) -> str:
    """Get ISO-3 country code from article text."""
    text = (article.get("title", "") + " " + article.get("short_summary", "")).lower()
    for keyword, (_, _, iso) in LOCATION_MAP.items():
        if keyword in text:
            return iso
    return ""

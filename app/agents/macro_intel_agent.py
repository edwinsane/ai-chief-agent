"""
Macro Intelligence Agent.

Converts classified news headlines into structured institutional-grade
market and geopolitical briefings. Uses a rule-based engine to map
headlines to asset impacts, directional views, and scenario logic.
Optionally polished by LLM when available.
"""

from __future__ import annotations

from collections import Counter
from typing import Any

from app.agents.base import BaseAgent
from app.core.logger import logger
from app.core.macro_rules import (
    ASSET_CLASSES,
    DEFAULT_SCENARIO,
    DIRECTION_LANGUAGE,
    KEYWORD_ASSET_MAP,
    SCENARIO_TEMPLATES,
    compute_asset_confidence,
)


class MacroIntelAgent(BaseAgent):
    """Generates institutional macro intelligence briefings from headlines."""

    name = "macro_intel"

    def run(self, state: dict[str, Any]) -> dict[str, Any]:
        articles = state.get("articles", [])
        logger.info("[%s] Generating macro briefing from %d articles", self.name, len(articles))

        if not articles:
            state["macro_briefing"] = self._empty_briefing()
            return state

        # Step 1: Scan all headlines and match keyword rules
        matched_rules = self._match_rules(articles)

        # Step 2: Build asset-specific breakdowns (only relevant assets)
        asset_views = self._build_asset_views(matched_rules, articles)

        # Step 3: Identify top theme and build scenario logic
        themes = Counter(r["theme"] for r in matched_rules)
        top_theme = themes.most_common(1)[0][0] if themes else "Global macro"
        scenarios = SCENARIO_TEMPLATES.get(top_theme, DEFAULT_SCENARIO)

        # Step 4: Build the executive summary sections
        briefing = self._assemble_briefing(
            articles, matched_rules, asset_views, top_theme, themes, scenarios,
        )

        # Step 5: Optional LLM polish
        if self.llm:
            briefing = self._llm_polish(briefing)

        state["macro_briefing"] = briefing
        logger.info("[%s] Macro briefing complete — %d assets, theme: %s",
                    self.name, len(asset_views), top_theme)
        return state

    # ------------------------------------------------------------------
    # Rule matching
    # ------------------------------------------------------------------

    def _match_rules(self, articles: list[dict]) -> list[dict]:
        """Match articles against keyword-asset rules."""
        text_blob = " ".join(
            (a.get("title", "") + " " + a.get("short_summary", "")).lower()
            for a in articles
        )

        matched: list[dict] = []
        for rule in KEYWORD_ASSET_MAP:
            hits = sum(1 for kw in rule["keywords"] if kw in text_blob)
            if hits:
                matched.append({**rule, "hit_count": hits})

        # Sort by hit count descending
        matched.sort(key=lambda r: r["hit_count"], reverse=True)
        return matched

    # ------------------------------------------------------------------
    # Asset view construction
    # ------------------------------------------------------------------

    def _build_asset_views(
        self, matched_rules: list[dict], articles: list[dict],
    ) -> list[dict]:
        """Build per-asset analysis for all impacted assets."""
        # Aggregate directions per asset across all matched rules
        asset_signals: dict[str, list[tuple[str, str, int]]] = {}
        for rule in matched_rules:
            for asset_key, direction in rule["assets"].items():
                if asset_key not in asset_signals:
                    asset_signals[asset_key] = []
                asset_signals[asset_key].append(
                    (direction, rule["theme"], rule["hit_count"])
                )

        views: list[dict] = []
        for asset_key, signals in asset_signals.items():
            if asset_key not in ASSET_CLASSES:
                continue

            meta = ASSET_CLASSES[asset_key]

            # Determine dominant direction
            dir_counts = Counter(s[0] for s in signals)
            dominant_dir = dir_counts.most_common(1)[0][0]
            total_hits = sum(s[2] for s in signals)
            lang = DIRECTION_LANGUAGE.get(dominant_dir, DIRECTION_LANGUAGE["neutral"])

            # Top driving themes
            theme_counts = Counter(s[1] for s in signals)
            drivers = [t for t, _ in theme_counts.most_common(3)]

            # Relevant headlines
            relevant_titles = self._find_relevant_headlines(asset_key, articles)

            views.append({
                "asset_key": asset_key,
                "label": meta["label"],
                "emoji": meta["emoji"],
                "direction": dominant_dir,
                "immediate_reaction": lang["reaction"],
                "short_term_direction": lang["short_term"],
                "risk_reversal_trigger": lang["risk_trigger"],
                "confidence": compute_asset_confidence(dominant_dir, total_hits),
                "why_this_matters": meta["baseline"],
                "driving_themes": drivers,
                "supporting_headlines": relevant_titles[:3],
                "signal_strength": total_hits,
            })

        # Sort by signal strength
        views.sort(key=lambda v: v["signal_strength"], reverse=True)
        return views

    def _find_relevant_headlines(self, asset_key: str, articles: list[dict]) -> list[str]:
        """Find article titles most relevant to an asset class."""
        # Get keywords that map to this asset
        relevant_kw: list[str] = []
        for rule in KEYWORD_ASSET_MAP:
            if asset_key in rule["assets"]:
                relevant_kw.extend(rule["keywords"])

        titles: list[str] = []
        for a in articles:
            text = (a.get("title", "") + " " + a.get("short_summary", "")).lower()
            if any(kw in text for kw in relevant_kw):
                titles.append(a["title"])
        return titles

    # ------------------------------------------------------------------
    # Briefing assembly
    # ------------------------------------------------------------------

    def _assemble_briefing(
        self,
        articles: list[dict],
        matched_rules: list[dict],
        asset_views: list[dict],
        top_theme: str,
        themes: Counter,
        scenarios: dict[str, str],
    ) -> dict:
        # What happened — top headlines driving the briefing
        geo_articles = [a for a in articles
                        if a.get("category") in ("Geopolitics", "Markets", "Energy", "Breaking News")
                        or a.get("market_impact") == "high"]
        geo_articles.sort(key=lambda a: a.get("relevance_score", 0), reverse=True)
        what_happened = [a["title"] for a in geo_articles[:5]] or [a["title"] for a in articles[:3]]

        # Market reaction summary
        up_assets = [v["label"] for v in asset_views if v["direction"] == "up"]
        down_assets = [v["label"] for v in asset_views if v["direction"] == "down"]
        volatile_assets = [v["label"] for v in asset_views if v["direction"] == "volatile"]

        reaction_parts = []
        if up_assets:
            reaction_parts.append(f"Bullish: {', '.join(up_assets)}")
        if down_assets:
            reaction_parts.append(f"Bearish: {', '.join(down_assets)}")
        if volatile_assets:
            reaction_parts.append(f"Volatile: {', '.join(volatile_assets)}")
        market_reaction = " | ".join(reaction_parts) or "No significant directional signal."

        # My market read
        risk_levels = Counter(r.get("risk_level", "low") for r in matched_rules)
        dominant_risk = risk_levels.most_common(1)[0][0] if risk_levels else "low"
        market_read = self._generate_market_read(top_theme, dominant_risk, len(articles))

        # Probable direction
        if up_assets and len(up_assets) > len(down_assets):
            probable_direction = f"Net bullish bias — {len(up_assets)} assets bid, {len(down_assets)} offered."
        elif down_assets and len(down_assets) > len(up_assets):
            probable_direction = f"Net bearish bias — {len(down_assets)} assets offered, {len(up_assets)} bid."
        else:
            probable_direction = "Mixed signals — two-way risk dominates. Position for volatility."

        # Confidence
        avg_confidence = (
            round(sum(v["confidence"] for v in asset_views) / len(asset_views), 2)
            if asset_views else 0.3
        )

        # What to watch
        watch_items = list(dict.fromkeys(
            rule["theme"] for rule in matched_rules[:5]
        ))

        return {
            "what_happened": what_happened,
            "market_reaction": market_reaction,
            "market_read": market_read,
            "probable_direction": probable_direction,
            "overall_confidence": avg_confidence,
            "overall_risk_level": dominant_risk,
            "why_it_matters": f"Current macro theme: {top_theme}. {len(matched_rules)} keyword rules triggered across {len(asset_views)} asset classes.",
            "what_to_watch": watch_items,
            "conclusion": self._generate_conclusion(top_theme, dominant_risk, probable_direction),
            "top_theme": top_theme,
            "all_themes": [{"theme": t, "count": c} for t, c in themes.most_common(10)],
            "asset_views": asset_views,
            "scenarios": scenarios,
            "article_count": len(articles),
            "rule_triggers": len(matched_rules),
        }

    def _generate_market_read(self, theme: str, risk_level: str, article_count: int) -> str:
        risk_tone = {
            "high": "Elevated geopolitical risk is the dominant driver. Positioning should favor hedges and safe havens.",
            "medium": "Moderate macro uncertainty. Markets are data-dependent with headline risk in both directions.",
            "low": "Low near-term risk. Focus on sector rotation and earnings-driven moves.",
        }
        return (
            f"Dominant theme: {theme}. "
            f"Based on {article_count} intelligence items — "
            f"{risk_tone.get(risk_level, risk_tone['medium'])}"
        )

    def _generate_conclusion(self, theme: str, risk: str, direction: str) -> str:
        if risk == "high":
            return (
                f"Risk-off posture recommended. {theme} is the key driver. "
                f"{direction} Monitor for rapid developments that could trigger scenario pivots."
            )
        if risk == "medium":
            return (
                f"Balanced positioning with tactical hedges. {theme} creates two-way risk. "
                f"{direction} Stay nimble and watch for catalyst confirmation."
            )
        return (
            f"Constructive outlook with selective risk-taking. {theme} is manageable. "
            f"{direction} Focus on quality and conviction positions."
        )

    def _empty_briefing(self) -> dict:
        return {
            "what_happened": [],
            "market_reaction": "No data available.",
            "market_read": "Insufficient data for macro assessment.",
            "probable_direction": "No directional signal.",
            "overall_confidence": 0.0,
            "overall_risk_level": "low",
            "why_it_matters": "Run the pipeline to generate intelligence.",
            "what_to_watch": [],
            "conclusion": "No briefing available.",
            "top_theme": "None",
            "all_themes": [],
            "asset_views": [],
            "scenarios": DEFAULT_SCENARIO,
            "article_count": 0,
            "rule_triggers": 0,
        }

    # ------------------------------------------------------------------
    # LLM polish
    # ------------------------------------------------------------------

    def _llm_polish(self, briefing: dict) -> dict:
        """Use LLM to rewrite key sections in institutional analyst tone."""
        sections_to_polish = ["market_read", "conclusion"]
        for key in sections_to_polish:
            raw = briefing.get(key, "")
            if not raw:
                continue
            try:
                prompt = (
                    f"You are a senior macro strategist at an institutional trading desk. "
                    f"Rewrite the following in a concise, authoritative tone suitable for "
                    f"a morning briefing note. Keep it to 2-3 sentences. Do not add disclaimers.\n\n"
                    f"{raw}"
                )
                resp = self.llm.invoke(prompt)
                briefing[key] = resp.content.strip()
            except Exception as exc:
                logger.warning("[macro_intel] LLM polish failed for %s: %s", key, exc)

        # Polish the probable direction
        try:
            asset_summary = "\n".join(
                f"- {v['label']}: {v['direction']}" for v in briefing.get("asset_views", [])
            )
            prompt = (
                f"You are a macro strategist. Given these asset signals:\n{asset_summary}\n\n"
                f"Write a 2-sentence probable direction summary. Be direct and institutional."
            )
            resp = self.llm.invoke(prompt)
            briefing["probable_direction"] = resp.content.strip()
        except Exception as exc:
            logger.warning("[macro_intel] LLM polish failed for direction: %s", exc)

        return briefing

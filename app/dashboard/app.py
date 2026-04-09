"""
AI Chief Agent — Executive Intelligence Dashboard.

Dark-themed, executive-grade monitoring UI with:
- Summary metric cards
- "Most Important Right Now" briefing
- Breaking, AI, AI Coding, AI Trading, Global News sections
- Sidebar filters (category, region, urgency, source, date, keyword, QA, relevance)
- Trends & insights charts
- Auto-refresh every 30 seconds
"""

import json
import sys
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.core.config import settings  # noqa: E402
from app.storage.database import (  # noqa: E402
    get_article_count,
    get_articles,
    get_distinct_categories,
    get_distinct_regions,
    get_distinct_sources,
    get_last_run,
    get_qa_stats,
    get_run_count,
    init_db,
)

# ---------------------------------------------------------------------------
# Page setup
# ---------------------------------------------------------------------------
st.set_page_config(page_title="AI Chief Agent", page_icon="🤖", layout="wide")
init_db()

# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------
st.markdown("""
<style>
meta[http-equiv="refresh"]{display:none}
.block-container{padding-top:1.2rem}
h1,h2,h3{letter-spacing:-0.02em}

/* metric card */
.mc{background:#1A1F2B;border:1px solid #2A2F3B;border-radius:10px;padding:1rem 1.2rem;text-align:center}
.mc .lb{font-size:.72rem;color:#8B95A5;text-transform:uppercase;letter-spacing:.06em;margin-bottom:.2rem}
.mc .vl{font-size:1.5rem;font-weight:700;color:#E2E8F0}
.mc .vl.g{color:#48BB78} .mc .vl.r{color:#FC8181} .mc .vl.b{color:#63B3ED} .mc .vl.a{color:#F6AD55} .mc .vl.p{color:#B794F4}

/* article card */
.ac{background:#1A1F2B;border:1px solid #2A2F3B;border-radius:10px;padding:1rem 1.2rem;margin-bottom:.7rem}
.ac h4{margin:0 0 .3rem 0;color:#E2E8F0;font-size:.95rem;line-height:1.3}
.ac .meta{font-size:.73rem;color:#8B95A5;margin-bottom:.4rem}
.ac .summary{color:#C8CDD3;font-size:.84rem;line-height:1.5;margin-bottom:.4rem}
.ac .wim{color:#A0AEC0;font-size:.8rem;font-style:italic;margin-bottom:.4rem}
.ac .tags{display:flex;flex-wrap:wrap;gap:.3rem}
.ac .tag{background:#2A2F3B;color:#A0AEC0;padding:.1rem .5rem;border-radius:4px;font-size:.7rem}

/* urgency badges */
.ub{display:inline-block;padding:.1rem .5rem;border-radius:4px;font-size:.72rem;font-weight:600}
.ub.brk{background:#742A2A;color:#FC8181} .ub.hi{background:#744210;color:#F6AD55}
.ub.med{background:#2A4365;color:#63B3ED} .ub.lo{background:#1A3A2A;color:#48BB78}

/* qa badge */
.qa-p{display:inline-block;background:#22543D;color:#48BB78;padding:.1rem .5rem;border-radius:4px;font-size:.72rem;font-weight:600}
.qa-f{display:inline-block;background:#742A2A;color:#FC8181;padding:.1rem .5rem;border-radius:4px;font-size:.72rem;font-weight:600}

/* section divider */
.sd{border:none;border-top:1px solid #2A2F3B;margin:1.5rem 0}

/* briefing card */
.brief{background:linear-gradient(135deg,#1A1F2B 0%,#1E2636 100%);border:1px solid #3A4050;border-radius:12px;padding:1.3rem 1.5rem;margin-bottom:.6rem}
.brief h4{margin:0 0 .3rem 0;color:#F6AD55;font-size:.85rem;text-transform:uppercase;letter-spacing:.04em}
.brief p{margin:0;color:#E2E8F0;font-size:.88rem;line-height:1.5}

[data-testid="stSidebar"]{background:#0E1117;border-right:1px solid #1E2330}
</style>
<meta http-equiv="refresh" content="30">
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def mc(label: str, value, color: str = "") -> str:
    c = f" {color}" if color else ""
    return f'<div class="mc"><div class="lb">{label}</div><div class="vl{c}">{value}</div></div>'


def urgency_badge(u: str) -> str:
    cls = {"breaking": "brk", "high": "hi", "medium": "med", "low": "lo"}.get(u, "lo")
    return f'<span class="ub {cls}">{u.upper()}</span>'


def article_card(a: dict) -> str:
    tags_html = "".join(f'<span class="tag">{t}</span>' for t in a.get("tags", []))
    cat_tag = f'<span class="tag">{a.get("category", "")}</span>' if a.get("category") else ""
    src = a.get("source", "Unknown")
    ts = a.get("published_at", "")[:16].replace("T", " ")
    ub = urgency_badge(a.get("urgency", "low"))
    score = a.get("relevance_score", 0)

    title = a.get("title", "Untitled")
    url = a.get("url", "")
    title_html = f'<a href="{url}" target="_blank" style="color:#E2E8F0;text-decoration:none">{title}</a>' if url else title

    summary = a.get("short_summary", "")
    wim = a.get("why_it_matters", "")
    wim_html = f'<div class="wim">Why it matters: {wim}</div>' if wim else ""

    return (
        f'<div class="ac">'
        f'<h4>{title_html}</h4>'
        f'<div class="meta">{src} · {ts} · {ub} · Relevance: {score:.0%}</div>'
        f'<div class="summary">{summary}</div>'
        f'{wim_html}'
        f'<div class="tags">{cat_tag}{tags_html}</div>'
        f'</div>'
    )


def briefing_card(title: str, body: str) -> str:
    return f'<div class="brief"><h4>{title}</h4><p>{body}</p></div>'


def _parse_date(iso: str) -> date | None:
    if not iso:
        return None
    try:
        return datetime.fromisoformat(iso.replace("Z", "+00:00")).date()
    except (ValueError, TypeError):
        return None


# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
all_articles = get_articles(limit=500)
total_articles = get_article_count()
total_runs = get_run_count()
last_run = get_last_run()
qa_stats = get_qa_stats()
db_categories = get_distinct_categories()
db_sources = get_distinct_sources()
db_regions = get_distinct_regions()

# ---------------------------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### Filters")

    f_categories = st.multiselect("Category", options=db_categories, default=[], placeholder="All categories")
    f_regions = st.multiselect("Region", options=db_regions, default=[], placeholder="All regions")
    f_sources = st.multiselect("Source", options=db_sources, default=[], placeholder="All sources")
    f_urgency = st.multiselect("Urgency", options=["breaking", "high", "medium", "low"], default=[], placeholder="All levels")
    f_qa = st.radio("QA Status", ["All", "Passed", "Failed"], horizontal=True)

    f_relevance = st.slider("Min relevance", 0.0, 1.0, 0.0, 0.05)

    # Date range
    dates = [_parse_date(a.get("published_at", "")) for a in all_articles]
    valid_dates = [d for d in dates if d]
    if valid_dates:
        f_date_range = st.date_input("Date range", value=(min(valid_dates), max(valid_dates)),
                                     min_value=min(valid_dates), max_value=max(valid_dates))
    else:
        f_date_range = None

    f_keyword = st.text_input("Keyword search", placeholder="Search titles & summaries...")

    st.markdown("---")
    mode_label = "LLM" if settings.llm_enabled else "Stub"
    news_label = "NewsAPI + RSS" if settings.newsapi_enabled else "RSS only"
    st.caption(f"Agent mode: **{mode_label}**")
    st.caption(f"Providers: **{news_label}**")

# ---------------------------------------------------------------------------
# Apply filters
# ---------------------------------------------------------------------------
filtered = all_articles

if f_categories:
    filtered = [a for a in filtered if a.get("category") in f_categories]
if f_regions:
    filtered = [a for a in filtered if a.get("region") in f_regions]
if f_sources:
    filtered = [a for a in filtered if a.get("source") in f_sources]
if f_urgency:
    filtered = [a for a in filtered if a.get("urgency") in f_urgency]
if f_relevance > 0:
    filtered = [a for a in filtered if (a.get("relevance_score") or 0) >= f_relevance]
if f_date_range and isinstance(f_date_range, tuple) and len(f_date_range) == 2:
    d_start, d_end = f_date_range
    filtered = [a for a in filtered if (d := _parse_date(a.get("published_at", ""))) and d_start <= d <= d_end]
if f_keyword:
    kw = f_keyword.lower()
    filtered = [a for a in filtered if kw in (a.get("title", "") + " " + a.get("short_summary", "")).lower()]

# QA filter applies to runs, but we show it at article level as pass-through
# Since QA validates the batch, all articles in a passed run are "passed"

# Sort by relevance descending
filtered.sort(key=lambda a: a.get("relevance_score", 0), reverse=True)

# ---------------------------------------------------------------------------
# HEADER
# ---------------------------------------------------------------------------
st.markdown("## AI Chief Agent")
st.caption("Executive Intelligence Dashboard")
st.markdown('<hr class="sd">', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# 1. METRIC CARDS
# ---------------------------------------------------------------------------
c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.markdown(mc("Total Articles", total_articles, "b"), unsafe_allow_html=True)
with c2:
    st.markdown(mc("Total Runs", total_runs, "p"), unsafe_allow_html=True)
with c3:
    ts = last_run["created_at"][:16].replace("T", " ") + " UTC" if last_run else "—"
    st.markdown(mc("Latest Run", ts), unsafe_allow_html=True)
with c4:
    st.markdown(mc("QA Passed", qa_stats["passed"], "g"), unsafe_allow_html=True)
with c5:
    st.markdown(mc("QA Failed", qa_stats["failed"], "r"), unsafe_allow_html=True)

st.markdown('<hr class="sd">', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# 2. MOST IMPORTANT RIGHT NOW
# ---------------------------------------------------------------------------
st.markdown("### Most Important Right Now")

if filtered:
    top3 = filtered[:3]
    breaking = [a for a in filtered if a.get("urgency") == "breaking"]
    ai_articles = [a for a in filtered if a.get("category") in ("AI", "AI Coding", "AI Trading")]
    market_risk = [a for a in filtered if a.get("market_impact") == "high"]

    bc1, bc2 = st.columns(2)
    with bc1:
        # Top stories
        for i, a in enumerate(top3, 1):
            st.markdown(
                briefing_card(
                    f"#{i} Top Story",
                    f"<strong>{a['title']}</strong><br>{a.get('short_summary', '')[:200]}"
                ),
                unsafe_allow_html=True,
            )
    with bc2:
        # Breaking
        if breaking:
            b = breaking[0]
            st.markdown(
                briefing_card("Most Urgent Breaking", f"<strong>{b['title']}</strong><br>{b.get('short_summary', '')[:200]}"),
                unsafe_allow_html=True,
            )
        else:
            st.markdown(briefing_card("Most Urgent Breaking", "No breaking stories at this time."), unsafe_allow_html=True)

        # AI opportunity
        if ai_articles:
            a = ai_articles[0]
            st.markdown(
                briefing_card("Biggest AI Opportunity", f"<strong>{a['title']}</strong><br>{a.get('short_summary', '')[:200]}"),
                unsafe_allow_html=True,
            )

        # Market / geo risk
        if market_risk:
            r = market_risk[0]
            st.markdown(
                briefing_card("Biggest Market / Geo Risk", f"<strong>{r['title']}</strong><br>{r.get('short_summary', '')[:200]}"),
                unsafe_allow_html=True,
            )
else:
    st.info("No articles available. Run `python main.py` to collect intelligence.")

st.markdown('<hr class="sd">', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# 3. CATEGORY SECTIONS
# ---------------------------------------------------------------------------

def _render_section(title: str, items: list[dict], max_items: int = 5):
    """Render a collapsible section of article cards."""
    if not items:
        return
    st.markdown(f"### {title}")
    st.caption(f"{len(items)} articles")
    for a in items[:max_items]:
        st.markdown(article_card(a), unsafe_allow_html=True)
    if len(items) > max_items:
        with st.expander(f"Show {len(items) - max_items} more"):
            for a in items[max_items:]:
                st.markdown(article_card(a), unsafe_allow_html=True)


# Breaking News (always first)
breaking_filtered = [a for a in filtered if a.get("urgency") == "breaking"]
_render_section("Breaking News", breaking_filtered)

# AI sections
_render_section("AI News", [a for a in filtered if a.get("category") == "AI"])
_render_section("AI Coding", [a for a in filtered if a.get("category") == "AI Coding"])
_render_section("AI Trading", [a for a in filtered if a.get("category") == "AI Trading"])

# World sections
_render_section("Global News", [a for a in filtered if a.get("category") == "Global News"])
_render_section("Geopolitics", [a for a in filtered if a.get("category") == "Geopolitics"])
_render_section("Markets", [a for a in filtered if a.get("category") == "Markets"])
_render_section("Energy", [a for a in filtered if a.get("category") == "Energy"])

st.markdown('<hr class="sd">', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# 4. TRENDS & INSIGHTS
# ---------------------------------------------------------------------------
st.markdown("### Trends & Insights")

if filtered:
    ch1, ch2 = st.columns(2)

    with ch1:
        st.markdown("##### Category Distribution")
        cat_counts = Counter(a.get("category", "Unknown") for a in filtered)
        df_cats = pd.DataFrame(cat_counts.most_common(10), columns=["Category", "Count"])
        st.bar_chart(df_cats, x="Category", y="Count", color="#4A90D9")

    with ch2:
        st.markdown("##### Topic Frequency")
        tag_counter: Counter = Counter()
        for a in filtered:
            for t in a.get("tags", []):
                tag_counter[t] += 1
        if tag_counter:
            df_tags = pd.DataFrame(tag_counter.most_common(12), columns=["Topic", "Count"])
            st.bar_chart(df_tags, x="Topic", y="Count", color="#F6AD55", horizontal=True)
        else:
            st.info("No topic tags detected.")

    # Most Repeated Topics
    st.markdown("##### Most Repeated Topics")
    if tag_counter:
        top_topics = tag_counter.most_common(10)
        cols = st.columns(min(len(top_topics), 5))
        for i, (tag, count) in enumerate(top_topics[:5]):
            with cols[i]:
                st.markdown(mc(tag, f"{count}x", "a"), unsafe_allow_html=True)
    else:
        st.info("No topic patterns detected yet.")

st.markdown('<hr class="sd">', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# 5. FOOTER
# ---------------------------------------------------------------------------
now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
st.caption(
    f"Showing {len(filtered)} of {total_articles} articles · "
    f"Dashboard refreshed at {now_utc} UTC · Auto-refresh: 30s · "
    f"Agent mode: {'LLM' if settings.llm_enabled else 'Stub'}"
)

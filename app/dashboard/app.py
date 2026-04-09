"""
AI Chief Agent — Executive Intelligence Dashboard.

Two-tab layout:
  1. Intelligence Feed — articles, filters, trends
  2. Macro Intelligence — institutional briefing, asset views, scenarios
"""

import json
import sys
import time
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.core.config import settings  # noqa: E402
from app.storage.database import (  # noqa: E402
    get_article_count,
    get_articles,
    get_briefings,
    get_distinct_categories,
    get_distinct_regions,
    get_distinct_sources,
    get_last_run,
    get_latest_briefing,
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
# CSS — Premium Intelligence Terminal
# Palette: deep navy #0A0E1A, electric blue #00D4FF, gold #FFB800
# ---------------------------------------------------------------------------
st.markdown("""
<style>
/* ── Global ────────────────────────────────────────────────────────────── */
.block-container{padding-top:1.4rem;max-width:1400px}
html,body,[data-testid="stAppViewContainer"]{background:#0A0E1A!important}
[data-testid="stHeader"]{background:transparent!important}
h1{font-size:2rem;font-weight:800;letter-spacing:-.03em;color:#E8ECF1}
h2{font-size:1.65rem;font-weight:700;letter-spacing:-.03em;color:#E8ECF1}
h3{font-size:1.15rem;font-weight:700;letter-spacing:-.02em;color:#D0D8E4}
h5{font-size:.88rem;font-weight:600;color:#8899AA;text-transform:uppercase;letter-spacing:.05em}

/* ── Section divider ──────────────────────────────────────────────────── */
.sd{border:none;height:1px;background:linear-gradient(90deg,transparent 0%,#1E3A5F 30%,#1E3A5F 70%,transparent 100%);margin:2rem 0}

/* ── Sidebar ──────────────────────────────────────────────────────────── */
[data-testid="stSidebar"]{background:linear-gradient(180deg,#070B14 0%,#0A0E1A 100%)!important;border-right:1px solid #1E3A5F}

/* ── Tabs ─────────────────────────────────────────────────────────────── */
[data-testid="stTabs"] button{font-size:.9rem;font-weight:600;letter-spacing:.03em;padding:.7rem 1.4rem;border-radius:8px 8px 0 0;color:#6B7C93;border:1px solid transparent;border-bottom:none;transition:all .2s ease}
[data-testid="stTabs"] button[aria-selected="true"]{color:#00D4FF;background:#111827;border-color:#1E3A5F;box-shadow:0 -2px 12px rgba(0,212,255,.1)}
[data-testid="stTabs"] button:hover:not([aria-selected="true"]){color:#A0B4CC;background:rgba(17,24,39,.4)}

/* ── KPI metric card ─────────────────────────────────────────────────── */
.mc{
  background:linear-gradient(145deg,#111827 0%,#0D1321 100%);
  border:1px solid #1E3A5F;
  border-radius:14px;
  padding:1.3rem 1rem;
  text-align:center;
  box-shadow:0 4px 20px rgba(0,0,0,.35),inset 0 1px 0 rgba(255,255,255,.03);
  transition:transform .2s ease,box-shadow .2s ease;
}
.mc:hover{transform:translateY(-2px);box-shadow:0 8px 30px rgba(0,212,255,.08),inset 0 1px 0 rgba(255,255,255,.05)}
.mc .lb{font-size:.68rem;color:#6B7C93;text-transform:uppercase;letter-spacing:.08em;margin-bottom:.35rem;font-weight:500}
.mc .vl{font-size:1.75rem;font-weight:800;color:#E8ECF1;line-height:1.2}
.mc .vl.g{color:#00E676} .mc .vl.r{color:#FF5252} .mc .vl.b{color:#00D4FF}
.mc .vl.a{color:#FFB800} .mc .vl.p{color:#BB86FC}

/* ── Article card ─────────────────────────────────────────────────────── */
.ac{
  background:linear-gradient(145deg,#111827 0%,#0D1321 100%);
  border:1px solid #1A2744;
  border-radius:14px;
  padding:1.3rem 1.5rem;
  margin-bottom:.9rem;
  box-shadow:0 2px 12px rgba(0,0,0,.3);
  transition:border-color .2s ease,box-shadow .2s ease;
}
.ac:hover{border-color:#1E3A5F;box-shadow:0 4px 24px rgba(0,212,255,.06)}
.ac h4{margin:0 0 .45rem 0;color:#E8ECF1;font-size:1rem;font-weight:700;line-height:1.35}
.ac h4 a{color:#E8ECF1!important;text-decoration:none;transition:color .15s ease}
.ac h4 a:hover{color:#00D4FF!important}
.ac .meta{font-size:.72rem;color:#6B7C93;margin-bottom:.55rem;display:flex;align-items:center;gap:.4rem;flex-wrap:wrap}
.ac .summary{color:#A0B4CC;font-size:.85rem;line-height:1.6;margin-bottom:.5rem}
.ac .wim{color:#FFB800;font-size:.8rem;font-style:italic;margin-bottom:.5rem;padding-left:.6rem;border-left:2px solid rgba(255,184,0,.3)}
.ac .tags{display:flex;flex-wrap:wrap;gap:.35rem;margin-top:.4rem}
.ac .tag{background:rgba(0,212,255,.08);color:#6BDDFF;padding:.2rem .55rem;border-radius:6px;font-size:.68rem;font-weight:500;border:1px solid rgba(0,212,255,.12)}

/* ── Urgency badges ───────────────────────────────────────────────────── */
.ub{display:inline-block;padding:.15rem .6rem;border-radius:6px;font-size:.7rem;font-weight:700;letter-spacing:.04em}
.ub.brk{background:rgba(255,82,82,.15);color:#FF5252;border:1px solid rgba(255,82,82,.3);animation:pulse-red 2s ease-in-out infinite}
.ub.hi{background:rgba(255,184,0,.12);color:#FFB800;border:1px solid rgba(255,184,0,.25)}
.ub.med{background:rgba(0,212,255,.1);color:#00D4FF;border:1px solid rgba(0,212,255,.2)}
.ub.lo{background:rgba(0,230,118,.08);color:#00E676;border:1px solid rgba(0,230,118,.15)}
@keyframes pulse-red{0%,100%{box-shadow:0 0 4px rgba(255,82,82,.2)}50%{box-shadow:0 0 12px rgba(255,82,82,.4)}}

/* ── Briefing card ────────────────────────────────────────────────────── */
.brief{
  background:linear-gradient(145deg,#111827 0%,#0F1A2E 100%);
  border:1px solid #1E3A5F;
  border-radius:14px;
  padding:1.4rem 1.6rem;
  margin-bottom:.8rem;
  box-shadow:0 2px 16px rgba(0,0,0,.3),inset 0 1px 0 rgba(255,255,255,.02);
  transition:border-color .2s ease,box-shadow .2s ease;
}
.brief:hover{border-color:#2A5080;box-shadow:0 4px 24px rgba(0,212,255,.06)}
.brief h4{margin:0 0 .5rem 0;color:#FFB800;font-size:.78rem;text-transform:uppercase;letter-spacing:.07em;font-weight:700}
.brief p{margin:0;color:#D0D8E4;font-size:.88rem;line-height:1.65}
.brief p strong{color:#E8ECF1;font-weight:700}

/* ── Asset card ───────────────────────────────────────────────────────── */
.asc{
  background:linear-gradient(145deg,#111827 0%,#0D1321 100%);
  border:1px solid #1A2744;
  border-radius:14px;
  padding:1.4rem 1.5rem;
  margin-bottom:.9rem;
  box-shadow:0 2px 16px rgba(0,0,0,.3);
  transition:border-color .2s ease,box-shadow .2s ease;
}
.asc:hover{border-color:#1E3A5F;box-shadow:0 4px 24px rgba(0,212,255,.06)}
.asc .hdr{display:flex;align-items:center;gap:.6rem;margin-bottom:.7rem}
.asc .hdr .emoji{font-size:1.5rem}
.asc .hdr .name{font-size:1.05rem;font-weight:800;color:#E8ECF1}
.asc .dir{display:inline-block;padding:.2rem .7rem;border-radius:6px;font-size:.72rem;font-weight:700;margin-left:.5rem;letter-spacing:.04em}
.asc .dir.up{background:rgba(0,230,118,.12);color:#00E676;border:1px solid rgba(0,230,118,.25)}
.asc .dir.down{background:rgba(255,82,82,.12);color:#FF5252;border:1px solid rgba(255,82,82,.25)}
.asc .dir.volatile{background:rgba(255,184,0,.12);color:#FFB800;border:1px solid rgba(255,184,0,.25)}
.asc .dir.neutral{background:rgba(107,124,147,.12);color:#8899AA;border:1px solid rgba(107,124,147,.2)}
.asc .row{font-size:.84rem;color:#A0B4CC;margin-bottom:.4rem;line-height:1.5;padding-left:.1rem}
.asc .row strong{color:#D0D8E4;font-weight:600}
.asc .conf{font-size:.73rem;color:#6B7C93;margin-top:.5rem;padding-top:.5rem;border-top:1px solid #1A2744}
.asc .headlines{margin-top:.5rem;padding:0;list-style:none}
.asc .headlines li{font-size:.78rem;color:#6B7C93;margin-bottom:.25rem;padding-left:.8rem;position:relative}
.asc .headlines li::before{content:"";position:absolute;left:0;top:.45rem;width:4px;height:4px;border-radius:50%;background:#00D4FF}

/* ── Scenario card ────────────────────────────────────────────────────── */
.sc{
  background:linear-gradient(145deg,#111827 0%,#0D1321 100%);
  border:1px solid #1A2744;
  border-radius:14px;
  padding:1.3rem 1.4rem;
  margin-bottom:.7rem;
  box-shadow:0 2px 12px rgba(0,0,0,.25);
  transition:border-color .2s ease;
}
.sc:hover{border-color:#1E3A5F}
.sc .lbl{font-size:.73rem;font-weight:700;text-transform:uppercase;letter-spacing:.06em;margin-bottom:.45rem}
.sc .lbl.bull{color:#00E676} .sc .lbl.base{color:#00D4FF} .sc .lbl.risk{color:#FF5252}
.sc p{margin:0;color:#A0B4CC;font-size:.84rem;line-height:1.6}

/* border-left accent on scenario cards */
.sc:has(.lbl.bull){border-left:3px solid rgba(0,230,118,.4)}
.sc:has(.lbl.base){border-left:3px solid rgba(0,212,255,.4)}
.sc:has(.lbl.risk){border-left:3px solid rgba(255,82,82,.4)}

/* ── Risk badge ───────────────────────────────────────────────────────── */
.rb{display:inline-block;padding:.18rem .65rem;border-radius:6px;font-size:.72rem;font-weight:700;letter-spacing:.04em}
.rb.rhi{background:rgba(255,82,82,.12);color:#FF5252;border:1px solid rgba(255,82,82,.25)}
.rb.rmed{background:rgba(255,184,0,.12);color:#FFB800;border:1px solid rgba(255,184,0,.25)}
.rb.rlo{background:rgba(0,230,118,.08);color:#00E676;border:1px solid rgba(0,230,118,.15)}

/* ── Streamlit overrides ──────────────────────────────────────────────── */
[data-testid="stExpander"] summary{font-size:.82rem;color:#6B7C93}
[data-testid="stExpander"] summary:hover{color:#00D4FF}
.stCaption{color:#4A5568!important}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def mc(label, value, color=""):
    c = f" {color}" if color else ""
    return f'<div class="mc"><div class="lb">{label}</div><div class="vl{c}">{value}</div></div>'

def urgency_badge(u):
    cls = {"breaking":"brk","high":"hi","medium":"med","low":"lo"}.get(u,"lo")
    return f'<span class="ub {cls}">{u.upper()}</span>'

def risk_badge(r):
    cls = {"high":"rhi","medium":"rmed","low":"rlo"}.get(r,"rlo")
    return f'<span class="rb {cls}">{r.upper()}</span>'

def article_card(a):
    tags_html = "".join(f'<span class="tag">{t}</span>' for t in a.get("tags",[]))
    cat_tag = f'<span class="tag">{a.get("category","")}</span>' if a.get("category") else ""
    src = a.get("source","Unknown"); ts = a.get("published_at","")[:16].replace("T"," ")
    ub = urgency_badge(a.get("urgency","low")); score = a.get("relevance_score",0)
    title = a.get("title","Untitled"); url = a.get("url","")
    th = f'<a href="{url}" target="_blank" style="color:#E2E8F0;text-decoration:none">{title}</a>' if url else title
    summary = a.get("short_summary","")
    wim = a.get("why_it_matters","")
    wh = f'<div class="wim">Why it matters: {wim}</div>' if wim else ""
    return f'<div class="ac"><h4>{th}</h4><div class="meta">{src} · {ts} · {ub} · Relevance: {score:.0%}</div><div class="summary">{summary}</div>{wh}<div class="tags">{cat_tag}{tags_html}</div></div>'

def briefing_card(title, body):
    return f'<div class="brief"><h4>{title}</h4><p>{body}</p></div>'

def asset_card_html(v):
    d = v["direction"]
    dcls = {"up":"up","down":"down","volatile":"volatile"}.get(d,"neutral")
    headlines_li = "".join(f"<li>{h}</li>" for h in v.get("supporting_headlines",[])[:3])
    headlines_html = f'<ul class="headlines">{headlines_li}</ul>' if headlines_li else ""
    themes = ", ".join(v.get("driving_themes",[]))
    return (
        f'<div class="asc">'
        f'<div class="hdr"><span class="emoji">{v["emoji"]}</span>'
        f'<span class="name">{v["label"]}</span>'
        f'<span class="dir {dcls}">{d.upper()}</span></div>'
        f'<div class="row"><strong>Immediate reaction:</strong> {v["immediate_reaction"]}</div>'
        f'<div class="row"><strong>Short-term direction:</strong> {v["short_term_direction"]}</div>'
        f'<div class="row"><strong>Risk reversal trigger:</strong> {v["risk_reversal_trigger"]}</div>'
        f'<div class="row"><strong>Why this matters:</strong> {v["why_this_matters"]}</div>'
        f'<div class="row"><strong>Driving themes:</strong> {themes}</div>'
        f'<div class="conf">Confidence: {v["confidence"]:.0%} · Signal strength: {v["signal_strength"]}</div>'
        f'{headlines_html}'
        f'</div>'
    )

def scenario_card(label, text, cls):
    return f'<div class="sc"><div class="lbl {cls}">{label}</div><p>{text}</p></div>'

def _parse_date(iso):
    if not iso: return None
    try: return datetime.fromisoformat(iso.replace("Z","+00:00")).date()
    except (ValueError,TypeError): return None

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
latest_briefing_row = get_latest_briefing()
briefing_data = latest_briefing_row["data"] if latest_briefing_row else {}

# ---------------------------------------------------------------------------
# Sidebar — refresh controls (top) + filters
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### Refresh")
    _refresh_col1, _refresh_col2 = st.columns([1, 1])
    with _refresh_col1:
        if st.button("Refresh Now", use_container_width=True, type="primary"):
            st.rerun()
    with _refresh_col2:
        auto_refresh_on = st.toggle("Auto", value=False, key="_auto_refresh_toggle")

    INTERVAL_OPTIONS = {"Manual only": 0, "1 minute": 60, "5 minutes": 300, "15 minutes": 900}
    if auto_refresh_on:
        interval_label = st.selectbox(
            "Interval",
            options=list(INTERVAL_OPTIONS.keys())[1:],  # exclude "Manual only"
            index=0,
            key="_refresh_interval",
        )
        refresh_seconds = INTERVAL_OPTIONS[interval_label]
    else:
        interval_label = "Manual only"
        refresh_seconds = 0

    # Show last refresh timestamp
    now_for_display = datetime.now(timezone.utc).strftime("%H:%M:%S UTC")
    st.caption(f"Last loaded: {now_for_display}")

    st.markdown("---")
    st.markdown("### Filters")
    f_categories = st.multiselect("Category", options=db_categories, default=[], placeholder="All categories")
    f_regions = st.multiselect("Region", options=db_regions, default=[], placeholder="All regions")
    f_sources = st.multiselect("Source", options=db_sources, default=[], placeholder="All sources")
    f_urgency = st.multiselect("Urgency", options=["breaking","high","medium","low"], default=[], placeholder="All levels")
    f_relevance = st.slider("Min relevance", 0.0, 1.0, 0.0, 0.05)
    dates = [_parse_date(a.get("published_at","")) for a in all_articles]
    valid_dates = [d for d in dates if d]
    if valid_dates:
        f_date_range = st.date_input("Date range", value=(min(valid_dates),max(valid_dates)),
                                     min_value=min(valid_dates), max_value=max(valid_dates))
    else:
        f_date_range = None
    f_keyword = st.text_input("Keyword search", placeholder="Search titles & summaries...")
    st.markdown("---")
    mode_label = "LLM" if settings.llm_enabled else "Rules"
    news_label = "NewsAPI + RSS" if settings.newsapi_enabled else "RSS only"
    st.caption(f"Agent mode: **{mode_label}** · Providers: **{news_label}**")

# ---------------------------------------------------------------------------
# Auto-refresh via fragment (only when enabled)
# Uses st.fragment(run_every=...) to schedule a soft rerun that preserves
# all widget state (tabs, filters, scroll) — unlike the old <meta> tag.
# ---------------------------------------------------------------------------
if refresh_seconds > 0:
    @st.fragment(run_every=timedelta(seconds=refresh_seconds))
    def _auto_refresher():
        if "_arf_ts" not in st.session_state:
            st.session_state._arf_ts = time.time()
            return
        elapsed = time.time() - st.session_state._arf_ts
        if elapsed >= refresh_seconds * 0.8:
            st.session_state._arf_ts = time.time()
            st.rerun(scope="app")
    _auto_refresher()

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown(
    '<h1 style="margin-bottom:0;padding-bottom:0">AI Chief Agent</h1>'
    '<p style="color:#6B7C93;font-size:.82rem;letter-spacing:.06em;'
    'text-transform:uppercase;margin-top:.1rem;margin-bottom:.5rem">'
    'Executive Intelligence Terminal</p>',
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# TABS
# ---------------------------------------------------------------------------
tab_feed, tab_macro = st.tabs(["Intelligence Feed", "Macro Intelligence"])

# ============================= TAB 1: FEED ================================
with tab_feed:

    # Apply filters
    filtered = all_articles
    if f_categories: filtered = [a for a in filtered if a.get("category") in f_categories]
    if f_regions: filtered = [a for a in filtered if a.get("region") in f_regions]
    if f_sources: filtered = [a for a in filtered if a.get("source") in f_sources]
    if f_urgency: filtered = [a for a in filtered if a.get("urgency") in f_urgency]
    if f_relevance > 0: filtered = [a for a in filtered if (a.get("relevance_score") or 0) >= f_relevance]
    if f_date_range and isinstance(f_date_range, tuple) and len(f_date_range) == 2:
        d_start, d_end = f_date_range
        filtered = [a for a in filtered if (d := _parse_date(a.get("published_at",""))) and d_start <= d <= d_end]
    if f_keyword:
        kw = f_keyword.lower()
        filtered = [a for a in filtered if kw in (a.get("title","")+" "+a.get("short_summary","")).lower()]
    filtered.sort(key=lambda a: a.get("relevance_score",0), reverse=True)

    # Metric cards
    st.markdown('<hr class="sd">', unsafe_allow_html=True)
    c1,c2,c3,c4,c5 = st.columns(5)
    with c1: st.markdown(mc("Total Articles", total_articles, "b"), unsafe_allow_html=True)
    with c2: st.markdown(mc("Total Runs", total_runs, "p"), unsafe_allow_html=True)
    with c3:
        ts = last_run["created_at"][:16].replace("T"," ")+" UTC" if last_run else "—"
        st.markdown(mc("Latest Run", ts), unsafe_allow_html=True)
    with c4: st.markdown(mc("QA Passed", qa_stats["passed"], "g"), unsafe_allow_html=True)
    with c5: st.markdown(mc("QA Failed", qa_stats["failed"], "r"), unsafe_allow_html=True)
    st.markdown('<hr class="sd">', unsafe_allow_html=True)

    # Most Important Right Now
    st.markdown("### Most Important Right Now")
    if filtered:
        top3 = filtered[:3]
        breaking = [a for a in filtered if a.get("urgency")=="breaking"]
        ai_articles = [a for a in filtered if a.get("category") in ("AI","AI Coding","AI Trading")]
        market_risk = [a for a in filtered if a.get("market_impact")=="high"]
        bc1,bc2 = st.columns(2)
        with bc1:
            for i,a in enumerate(top3,1):
                st.markdown(briefing_card(f"#{i} Top Story", f"<strong>{a['title']}</strong><br>{a.get('short_summary','')[:200]}"), unsafe_allow_html=True)
        with bc2:
            if breaking:
                b = breaking[0]
                st.markdown(briefing_card("Most Urgent Breaking", f"<strong>{b['title']}</strong><br>{b.get('short_summary','')[:200]}"), unsafe_allow_html=True)
            else:
                st.markdown(briefing_card("Most Urgent Breaking", "No breaking stories at this time."), unsafe_allow_html=True)
            if ai_articles:
                a = ai_articles[0]
                st.markdown(briefing_card("Biggest AI Opportunity", f"<strong>{a['title']}</strong><br>{a.get('short_summary','')[:200]}"), unsafe_allow_html=True)
            if market_risk:
                r = market_risk[0]
                st.markdown(briefing_card("Biggest Market / Geo Risk", f"<strong>{r['title']}</strong><br>{r.get('short_summary','')[:200]}"), unsafe_allow_html=True)
    else:
        st.info("No articles available. Run `python main.py` to collect intelligence.")
    st.markdown('<hr class="sd">', unsafe_allow_html=True)

    # Category sections
    def _render_section(title, items, max_items=5):
        if not items: return
        st.markdown(f"### {title}")
        st.caption(f"{len(items)} articles")
        for a in items[:max_items]:
            st.markdown(article_card(a), unsafe_allow_html=True)
        if len(items) > max_items:
            with st.expander(f"Show {len(items)-max_items} more"):
                for a in items[max_items:]:
                    st.markdown(article_card(a), unsafe_allow_html=True)

    _render_section("Breaking News", [a for a in filtered if a.get("urgency")=="breaking"])
    _render_section("AI News", [a for a in filtered if a.get("category")=="AI"])
    _render_section("AI Coding", [a for a in filtered if a.get("category")=="AI Coding"])
    _render_section("AI Trading", [a for a in filtered if a.get("category")=="AI Trading"])
    _render_section("Global News", [a for a in filtered if a.get("category")=="Global News"])
    _render_section("Geopolitics", [a for a in filtered if a.get("category")=="Geopolitics"])
    _render_section("Markets", [a for a in filtered if a.get("category")=="Markets"])
    _render_section("Energy", [a for a in filtered if a.get("category")=="Energy"])
    st.markdown('<hr class="sd">', unsafe_allow_html=True)

    # Trends & Insights
    st.markdown("### Trends & Insights")
    if filtered:
        ch1,ch2 = st.columns(2)
        with ch1:
            st.markdown("##### Category Distribution")
            cat_counts = Counter(a.get("category","Unknown") for a in filtered)
            df_cats = pd.DataFrame(cat_counts.most_common(10), columns=["Category","Count"])
            st.bar_chart(df_cats, x="Category", y="Count", color="#00D4FF")
        with ch2:
            st.markdown("##### Topic Frequency")
            tag_counter = Counter()
            for a in filtered:
                for t in a.get("tags",[]):
                    tag_counter[t] += 1
            if tag_counter:
                df_tags = pd.DataFrame(tag_counter.most_common(12), columns=["Topic","Count"])
                st.bar_chart(df_tags, x="Topic", y="Count", color="#FFB800", horizontal=True)
            else:
                st.info("No topic tags detected.")

# ========================= TAB 2: MACRO INTEL =============================
with tab_macro:

    if not briefing_data:
        st.info("No macro briefing available yet. Run `python main.py` to generate one.")
    else:
        b = briefing_data

        # --- Header metrics ---
        st.markdown('<hr class="sd">', unsafe_allow_html=True)
        m1,m2,m3,m4,m5 = st.columns(5)
        with m1: st.markdown(mc("Top Theme", b.get("top_theme","—"), "a"), unsafe_allow_html=True)
        with m2: st.markdown(mc("Risk Level", b.get("overall_risk_level","—").upper(), "r" if b.get("overall_risk_level")=="high" else "a" if b.get("overall_risk_level")=="medium" else "g"), unsafe_allow_html=True)
        with m3: st.markdown(mc("Confidence", f'{b.get("overall_confidence",0):.0%}', "b"), unsafe_allow_html=True)
        with m4: st.markdown(mc("Assets Impacted", len(b.get("asset_views",[])), "p"), unsafe_allow_html=True)
        with m5: st.markdown(mc("Rules Triggered", b.get("rule_triggers",0), "b"), unsafe_allow_html=True)
        st.markdown('<hr class="sd">', unsafe_allow_html=True)

        # --- Executive Summary ---
        st.markdown("### Executive Summary")
        es1, es2 = st.columns(2)
        with es1:
            st.markdown(briefing_card("What Happened", "<br>".join(f"• {h}" for h in b.get("what_happened",[]))), unsafe_allow_html=True)
            st.markdown(briefing_card("Market Reaction", b.get("market_reaction","")), unsafe_allow_html=True)
            st.markdown(briefing_card("My Market Read", b.get("market_read","")), unsafe_allow_html=True)
        with es2:
            st.markdown(briefing_card("Probable Direction", b.get("probable_direction","")), unsafe_allow_html=True)
            st.markdown(briefing_card("Why It Matters", b.get("why_it_matters","")), unsafe_allow_html=True)
            watch = b.get("what_to_watch",[])
            st.markdown(briefing_card("What To Watch Now", "<br>".join(f"• {w}" for w in watch) if watch else "No specific watch items."), unsafe_allow_html=True)

        # Conclusion
        st.markdown(briefing_card("Conclusion", b.get("conclusion","")), unsafe_allow_html=True)
        st.markdown('<hr class="sd">', unsafe_allow_html=True)

        # --- Scenario Analysis ---
        st.markdown("### Scenario Analysis")
        scenarios = b.get("scenarios",{})
        sc1,sc2,sc3 = st.columns(3)
        with sc1: st.markdown(scenario_card("Bull Case", scenarios.get("bull_case","—"), "bull"), unsafe_allow_html=True)
        with sc2: st.markdown(scenario_card("Base Case", scenarios.get("base_case","—"), "base"), unsafe_allow_html=True)
        with sc3: st.markdown(scenario_card("Risk Case", scenarios.get("risk_case","—"), "risk"), unsafe_allow_html=True)
        st.markdown('<hr class="sd">', unsafe_allow_html=True)

        # --- Asset Breakdown ---
        asset_views = b.get("asset_views",[])

        # Filters for macro tab
        st.markdown("### Asset-Class Breakdown")

        acol1, acol2, acol3 = st.columns(3)
        with acol1:
            f_asset_dir = st.multiselect("Direction", options=["up","down","volatile","neutral"], default=[], placeholder="All directions", key="macro_dir")
        with acol2:
            all_asset_labels = sorted(set(v.get("label","") for v in asset_views))
            f_asset_class = st.multiselect("Asset class", options=all_asset_labels, default=[], placeholder="All assets", key="macro_asset")
        with acol3:
            f_min_conf = st.slider("Min confidence", 0.0, 1.0, 0.0, 0.05, key="macro_conf")

        # Apply macro filters
        fv = asset_views
        if f_asset_dir: fv = [v for v in fv if v.get("direction") in f_asset_dir]
        if f_asset_class: fv = [v for v in fv if v.get("label") in f_asset_class]
        if f_min_conf > 0: fv = [v for v in fv if v.get("confidence",0) >= f_min_conf]

        if fv:
            # Render in two columns
            left_col, right_col = st.columns(2)
            for i, v in enumerate(fv):
                with left_col if i % 2 == 0 else right_col:
                    st.markdown(asset_card_html(v), unsafe_allow_html=True)
        else:
            st.info("No asset views match the current filters.")

        st.markdown('<hr class="sd">', unsafe_allow_html=True)

        # --- Theme Distribution ---
        all_themes = b.get("all_themes",[])
        if all_themes:
            st.markdown("### Active Themes")
            df_themes = pd.DataFrame(all_themes)
            if not df_themes.empty:
                st.bar_chart(df_themes, x="theme", y="count", color="#BB86FC")

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown('<hr class="sd">', unsafe_allow_html=True)
now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
refresh_status = f"Auto: {interval_label}" if refresh_seconds > 0 else "Manual"
st.markdown(
    f'<p style="text-align:center;color:#4A5568;font-size:.72rem;letter-spacing:.05em;padding:.5rem 0">'
    f'{len(all_articles)} articles &nbsp;·&nbsp; '
    f'{now_utc} UTC &nbsp;·&nbsp; '
    f'Refresh: {refresh_status} &nbsp;·&nbsp; '
    f'Mode: {"LLM" if settings.llm_enabled else "Rules"}'
    f'</p>',
    unsafe_allow_html=True,
)

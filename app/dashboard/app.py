"""
AI Chief Agent — Executive Intelligence Terminal.

Premium two-tab dashboard:
  1. Intelligence Feed — hero story, signal strip, articles, trends
  2. Macro Intelligence — institutional briefing, scenarios, asset views
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
    get_freshness_info,
    get_last_run,
    get_latest_briefing,
    get_qa_stats,
    get_run_count,
    init_db,
)

# ╔═════════════════════════════════════════════════════════════════════════╗
# ║  PAGE SETUP                                                           ║
# ╚═════════════════════════════════════════════════════════════════════════╝
st.set_page_config(page_title="AI Chief Agent", page_icon="🤖", layout="wide")
init_db()

# ╔═════════════════════════════════════════════════════════════════════════╗
# ║  DESIGN SYSTEM — CSS                                                  ║
# ║  Palette: navy #0A0E1A · blue #00D4FF · gold #FFB800                  ║
# ║  Bullish #00E676 · Bearish #FF5252 · Purple #BB86FC                   ║
# ╚═════════════════════════════════════════════════════════════════════════╝
st.markdown("""
<style>
/* ── Reset & globals ──────────────────────────────────────────────────── */
.block-container{padding-top:.8rem;max-width:1440px}
html,body,[data-testid="stAppViewContainer"]{background:#0A0E1A!important}
[data-testid="stHeader"]{background:transparent!important}
[data-testid="stBottomBlockContainer"]{background:#0A0E1A!important}

/* ── Typography scale ─────────────────────────────────────────────────── */
h1{font-size:1.1rem!important;color:#E8ECF1!important;font-weight:700!important}
h2{font-size:1rem!important;color:#E8ECF1!important;font-weight:700!important}
h3{font-size:.95rem!important;color:#D0D8E4!important;font-weight:600!important}

/* ── Sidebar ──────────────────────────────────────────────────────────── */
[data-testid="stSidebar"]{background:linear-gradient(180deg,#060A14 0%,#0A0E1A 100%)!important;border-right:1px solid #122040}
[data-testid="stSidebar"] hr{border-color:#122040!important;margin:.8rem 0!important}
.sb-hdr{font-size:.65rem;text-transform:uppercase;letter-spacing:.1em;color:#3D5A80;font-weight:700;margin:1rem 0 .4rem 0}

/* ── Tabs ─────────────────────────────────────────────────────────────── */
[data-testid="stTabs"]{background:#0A0E1A}
[data-testid="stTabs"] button{
  font-size:.8rem;font-weight:700;letter-spacing:.06em;text-transform:uppercase;
  padding:.65rem 1.6rem;color:#3D5A80;
  border:1px solid transparent;border-bottom:2px solid transparent;border-radius:0;
  transition:all .2s ease;
}
[data-testid="stTabs"] button[aria-selected="true"]{
  color:#00D4FF;border-bottom:2px solid #00D4FF;
  background:linear-gradient(180deg,rgba(0,212,255,.04) 0%,transparent 100%);
}
[data-testid="stTabs"] button:hover:not([aria-selected="true"]){color:#6B9CC0}
[data-testid="stTabs"] [role="tablist"]{border-bottom:1px solid #122040;gap:0}

/* ── Dividers ─────────────────────────────────────────────────────────── */
.sd{border:none;height:1px;background:linear-gradient(90deg,transparent 0%,#122040 20%,#1E3A5F 50%,#122040 80%,transparent 100%);margin:2.2rem 0}
.sd-sm{border:none;height:1px;background:#122040;margin:1.2rem 0}

/* ── Section header ───────────────────────────────────────────────────── */
.sh{margin:0 0 1.2rem 0;padding-bottom:.6rem;border-bottom:1px solid #122040}
.sh h2{margin:0!important;padding:0!important;font-size:1rem!important;font-weight:700!important;color:#E8ECF1!important;letter-spacing:-.01em!important}
.sh .sub{font-size:.68rem;color:#3D5A80;text-transform:uppercase;letter-spacing:.08em;margin-top:.15rem}

/* ── Command header ───────────────────────────────────────────────────── */
.cmd-hdr{display:flex;align-items:baseline;justify-content:space-between;padding:.6rem 0 .8rem 0;border-bottom:1px solid #122040;margin-bottom:1rem}
.cmd-hdr .title{font-size:1.4rem;font-weight:800;color:#E8ECF1;letter-spacing:-.02em}
.cmd-hdr .title span{color:#00D4FF}
.cmd-hdr .meta{font-size:.65rem;color:#3D5A80;letter-spacing:.06em;text-transform:uppercase}

/* ── Signal strip ─────────────────────────────────────────────────────── */
.sig-strip{
  display:flex;flex-wrap:wrap;gap:.5rem;
  padding:.75rem 1rem;margin:1rem 0 1.5rem 0;
  background:linear-gradient(135deg,#0D1425 0%,#0A1020 100%);
  border:1px solid #122040;border-radius:10px;
}
.sig-pill{
  display:inline-flex;align-items:center;gap:.35rem;
  padding:.3rem .7rem;border-radius:6px;font-size:.68rem;font-weight:600;
  letter-spacing:.03em;border:1px solid;
}
.sig-pill .dot{width:6px;height:6px;border-radius:50%;flex-shrink:0}
.sig-pill.s-hi{color:#00E676;border-color:rgba(0,230,118,.2);background:rgba(0,230,118,.06)}
.sig-pill.s-hi .dot{background:#00E676;box-shadow:0 0 6px rgba(0,230,118,.5)}
.sig-pill.s-elev{color:#FFB800;border-color:rgba(255,184,0,.2);background:rgba(255,184,0,.06)}
.sig-pill.s-elev .dot{background:#FFB800;box-shadow:0 0 6px rgba(255,184,0,.5)}
.sig-pill.s-vol{color:#FF5252;border-color:rgba(255,82,82,.2);background:rgba(255,82,82,.06)}
.sig-pill.s-vol .dot{background:#FF5252;box-shadow:0 0 6px rgba(255,82,82,.5)}
.sig-pill.s-low{color:#3D5A80;border-color:rgba(61,90,128,.25);background:rgba(61,90,128,.06)}
.sig-pill.s-low .dot{background:#3D5A80}
.sig-pill.s-info{color:#6B9CC0;border-color:rgba(107,156,192,.2);background:rgba(107,156,192,.06)}
.sig-pill.s-info .dot{background:#00D4FF;box-shadow:0 0 4px rgba(0,212,255,.4)}

/* ── KPI card ─────────────────────────────────────────────────────────── */
.kpi{
  background:linear-gradient(160deg,#0F1B30 0%,#0B1222 100%);
  border:1px solid #152238;border-radius:12px;
  padding:1.2rem 1rem 1rem;text-align:center;position:relative;overflow:hidden;
  box-shadow:0 4px 24px rgba(0,0,0,.4);
  transition:transform .2s ease,box-shadow .2s ease;
}
.kpi:hover{transform:translateY(-3px);box-shadow:0 8px 32px rgba(0,0,0,.5)}
.kpi::before{content:"";position:absolute;top:0;left:0;right:0;height:3px;border-radius:12px 12px 0 0}
.kpi.kpi-b::before{background:linear-gradient(90deg,#00D4FF,#0099CC)}
.kpi.kpi-g::before{background:linear-gradient(90deg,#00E676,#00B85C)}
.kpi.kpi-r::before{background:linear-gradient(90deg,#FF5252,#CC3D3D)}
.kpi.kpi-a::before{background:linear-gradient(90deg,#FFB800,#CC9300)}
.kpi.kpi-p::before{background:linear-gradient(90deg,#BB86FC,#9B60E0)}
.kpi .lb{font-size:.6rem;color:#3D5A80;text-transform:uppercase;letter-spacing:.1em;font-weight:600;margin-bottom:.4rem}
.kpi .vl{font-size:1.9rem;font-weight:800;color:#E8ECF1;line-height:1.15}
.kpi .vl.g{color:#00E676} .kpi .vl.r{color:#FF5252} .kpi .vl.b{color:#00D4FF}
.kpi .vl.a{color:#FFB800} .kpi .vl.p{color:#BB86FC}

/* ── Hero card (top story) ────────────────────────────────────────────── */
.hero{
  background:linear-gradient(145deg,#0F1B30 0%,#0B1525 100%);
  border:1px solid #1E3A5F;border-left:4px solid #00D4FF;
  border-radius:14px;padding:1.8rem 2rem;margin-bottom:1.2rem;
  box-shadow:0 4px 30px rgba(0,212,255,.06),0 2px 16px rgba(0,0,0,.4);
  position:relative;overflow:hidden;
}
.hero::after{content:"";position:absolute;top:0;right:0;width:200px;height:100%;background:radial-gradient(ellipse at top right,rgba(0,212,255,.04) 0%,transparent 70%);pointer-events:none}
.hero .label{font-size:.65rem;font-weight:700;text-transform:uppercase;letter-spacing:.1em;color:#00D4FF;margin-bottom:.6rem;display:flex;align-items:center;gap:.4rem}
.hero .label .pulse{display:inline-block;width:7px;height:7px;border-radius:50%;background:#00D4FF;box-shadow:0 0 8px rgba(0,212,255,.6);animation:pulse-b 2s ease-in-out infinite}
.hero h3{margin:0 0 .5rem 0!important;font-size:1.25rem!important;font-weight:800!important;color:#E8ECF1!important;line-height:1.3!important}
.hero h3 a{color:#E8ECF1!important;text-decoration:none!important;transition:color .15s}
.hero h3 a:hover{color:#00D4FF!important}
.hero .meta{font-size:.72rem;color:#4A6A8A;margin-bottom:.7rem;display:flex;align-items:center;gap:.5rem;flex-wrap:wrap}
.hero .body{color:#A0B4CC;font-size:.9rem;line-height:1.65;margin-bottom:.6rem}
.hero .wim{color:#FFB800;font-size:.82rem;font-style:italic;padding:.5rem 0 .5rem .8rem;border-left:2px solid rgba(255,184,0,.3);margin-bottom:.6rem}
.hero .chips{display:flex;flex-wrap:wrap;gap:.35rem}
@keyframes pulse-b{0%,100%{opacity:1}50%{opacity:.4}}

/* ── Secondary briefing cards (breaking / AI opp / geo risk) ──────────── */
.sec-card{
  background:linear-gradient(145deg,#0F1B30 0%,#0B1222 100%);
  border:1px solid #152238;border-radius:12px;padding:1.2rem 1.3rem;
  box-shadow:0 2px 16px rgba(0,0,0,.35);height:100%;
  transition:border-color .2s ease,box-shadow .2s ease;
}
.sec-card:hover{border-color:#1E3A5F;box-shadow:0 4px 24px rgba(0,0,0,.5)}
.sec-card .label{font-size:.62rem;font-weight:700;text-transform:uppercase;letter-spacing:.08em;margin-bottom:.5rem;display:flex;align-items:center;gap:.35rem}
.sec-card .label.l-brk{color:#FF5252}
.sec-card .label.l-ai{color:#00D4FF}
.sec-card .label.l-risk{color:#FFB800}
.sec-card h4{margin:0 0 .35rem 0;color:#E8ECF1;font-size:.95rem;font-weight:700;line-height:1.3}
.sec-card p{margin:0;color:#7A90A8;font-size:.82rem;line-height:1.55}

/* ── Article card ─────────────────────────────────────────────────────── */
.ac{
  background:linear-gradient(160deg,#0F1B30 0%,#0B1222 100%);
  border:1px solid #152238;border-radius:12px;
  padding:1.2rem 1.4rem;margin-bottom:.8rem;
  box-shadow:0 2px 12px rgba(0,0,0,.3);
  transition:border-color .25s ease,box-shadow .25s ease;
}
.ac:hover{border-color:#1E3A5F;box-shadow:0 4px 20px rgba(0,212,255,.04)}
.ac .ac-top{display:flex;align-items:flex-start;justify-content:space-between;gap:.8rem;margin-bottom:.4rem}
.ac h4{margin:0;color:#E8ECF1;font-size:.95rem;font-weight:700;line-height:1.35;flex:1}
.ac h4 a{color:#E8ECF1!important;text-decoration:none;transition:color .15s}
.ac h4 a:hover{color:#00D4FF!important}
.ac .ac-score{font-size:.72rem;font-weight:700;color:#00D4FF;white-space:nowrap;padding:.15rem .5rem;border:1px solid rgba(0,212,255,.2);border-radius:5px;background:rgba(0,212,255,.06)}
.ac .meta{font-size:.68rem;color:#4A6A8A;margin-bottom:.55rem}
.ac .summary{color:#8899AA;font-size:.84rem;line-height:1.6;margin-bottom:.5rem}
.ac .wim{color:#FFB800;font-size:.8rem;font-style:italic;padding:.4rem 0 .4rem .7rem;border-left:2px solid rgba(255,184,0,.25);margin-bottom:.5rem}
.ac .chips{display:flex;flex-wrap:wrap;gap:.3rem;margin-top:.3rem}

/* ── Chip / badge system ──────────────────────────────────────────────── */
.chip{display:inline-block;padding:.15rem .5rem;border-radius:5px;font-size:.65rem;font-weight:600;letter-spacing:.02em;border:1px solid}
.chip-cat{color:#6BDDFF;border-color:rgba(0,212,255,.15);background:rgba(0,212,255,.06)}
.chip-tag{color:#7A90A8;border-color:rgba(122,144,168,.15);background:rgba(122,144,168,.06)}
.chip-brk{color:#FF5252;border-color:rgba(255,82,82,.25);background:rgba(255,82,82,.08);animation:pulse-red 2s ease-in-out infinite}
.chip-hi{color:#FFB800;border-color:rgba(255,184,0,.2);background:rgba(255,184,0,.06)}
.chip-med{color:#00D4FF;border-color:rgba(0,212,255,.15);background:rgba(0,212,255,.05)}
.chip-lo{color:#3D6B5A;border-color:rgba(0,230,118,.12);background:rgba(0,230,118,.04)}
@keyframes pulse-red{0%,100%{box-shadow:0 0 3px rgba(255,82,82,.15)}50%{box-shadow:0 0 10px rgba(255,82,82,.3)}}

/* ── Briefing card (macro intel) ──────────────────────────────────────── */
.brief{
  background:linear-gradient(145deg,#0F1B30 0%,#0B1525 100%);
  border:1px solid #152238;border-left:3px solid #FFB800;
  border-radius:12px;padding:1.3rem 1.5rem;margin-bottom:.8rem;
  box-shadow:0 2px 16px rgba(0,0,0,.3);
  transition:border-color .2s ease;
}
.brief:hover{border-color:#1E3A5F}
.brief h4{margin:0 0 .5rem 0;color:#FFB800;font-size:.7rem;text-transform:uppercase;letter-spacing:.08em;font-weight:700}
.brief p{margin:0;color:#A0B4CC;font-size:.86rem;line-height:1.65}
.brief p strong{color:#D0D8E4}

/* ── Asset card ───────────────────────────────────────────────────────── */
.asc{
  background:linear-gradient(160deg,#0F1B30 0%,#0B1222 100%);
  border:1px solid #152238;border-radius:12px;
  padding:1.3rem 1.4rem;margin-bottom:.8rem;
  box-shadow:0 2px 16px rgba(0,0,0,.3);
  transition:border-color .2s ease;
}
.asc:hover{border-color:#1E3A5F}
.asc .hdr{display:flex;align-items:center;gap:.6rem;margin-bottom:.7rem;padding-bottom:.6rem;border-bottom:1px solid #152238}
.asc .hdr .emoji{font-size:1.4rem}
.asc .hdr .name{font-size:1rem;font-weight:800;color:#E8ECF1;flex:1}
.asc .dir{display:inline-block;padding:.2rem .65rem;border-radius:6px;font-size:.7rem;font-weight:700;letter-spacing:.04em;border:1px solid}
.asc .dir.up{color:#00E676;border-color:rgba(0,230,118,.25);background:rgba(0,230,118,.08)}
.asc .dir.down{color:#FF5252;border-color:rgba(255,82,82,.25);background:rgba(255,82,82,.08)}
.asc .dir.volatile{color:#FFB800;border-color:rgba(255,184,0,.25);background:rgba(255,184,0,.08)}
.asc .dir.neutral{color:#6B7C93;border-color:rgba(107,124,147,.2);background:rgba(107,124,147,.06)}
.asc .row{font-size:.82rem;color:#7A90A8;margin-bottom:.35rem;line-height:1.5}
.asc .row strong{color:#A0B4CC;font-weight:600}
.asc .conf{font-size:.7rem;color:#3D5A80;margin-top:.5rem;padding-top:.5rem;border-top:1px solid #152238}
.asc .headlines{margin-top:.5rem;padding:0;list-style:none}
.asc .headlines li{font-size:.75rem;color:#4A6A8A;margin-bottom:.2rem;padding-left:.8rem;position:relative}
.asc .headlines li::before{content:"";position:absolute;left:0;top:.4rem;width:4px;height:4px;border-radius:50%;background:#00D4FF}

/* ── Scenario card ────────────────────────────────────────────────────── */
.sc{
  background:linear-gradient(160deg,#0F1B30 0%,#0B1222 100%);
  border:1px solid #152238;border-radius:12px;
  padding:1.2rem 1.3rem;margin-bottom:.7rem;
  box-shadow:0 2px 12px rgba(0,0,0,.25);
  transition:border-color .2s ease;
}
.sc:hover{border-color:#1E3A5F}
.sc .lbl{font-size:.68rem;font-weight:700;text-transform:uppercase;letter-spacing:.08em;margin-bottom:.4rem}
.sc .lbl.bull{color:#00E676} .sc .lbl.base{color:#00D4FF} .sc .lbl.risk{color:#FF5252}
.sc p{margin:0;color:#7A90A8;font-size:.82rem;line-height:1.6}
.sc:has(.lbl.bull){border-left:3px solid rgba(0,230,118,.35)}
.sc:has(.lbl.base){border-left:3px solid rgba(0,212,255,.35)}
.sc:has(.lbl.risk){border-left:3px solid rgba(255,82,82,.35)}

/* ── Expander ─────────────────────────────────────────────────────────── */
[data-testid="stExpander"]{border:1px solid #152238!important;border-radius:10px!important;background:#0B1222!important}
[data-testid="stExpander"] summary{font-size:.78rem;color:#3D5A80;font-weight:600}
[data-testid="stExpander"] summary:hover{color:#00D4FF}

/* ── Footer ───────────────────────────────────────────────────────────── */
.ftr{text-align:center;color:#2A3A50;font-size:.65rem;letter-spacing:.06em;padding:.8rem 0;text-transform:uppercase}
</style>
""", unsafe_allow_html=True)


# ╔═════════════════════════════════════════════════════════════════════════╗
# ║  HTML HELPERS                                                         ║
# ╚═════════════════════════════════════════════════════════════════════════╝

def kpi(label, value, color="b"):
    c = f" {color}" if color else ""
    return (
        f'<div class="kpi kpi-{color}">'
        f'<div class="lb">{label}</div>'
        f'<div class="vl{c}">{value}</div>'
        f'</div>'
    )


def urgency_chip(u):
    cls = {"breaking": "chip-brk", "high": "chip-hi", "medium": "chip-med", "low": "chip-lo"}.get(u, "chip-lo")
    return f'<span class="chip {cls}">{u.upper()}</span>'


def signal_pill(label, value, level):
    return f'<span class="sig-pill s-{level}"><span class="dot"></span>{label}: {value}</span>'


def hero_card(a):
    """Full-width featured story card."""
    title = a.get("title", "Untitled")
    url = a.get("url", "")
    th = f'<a href="{url}" target="_blank">{title}</a>' if url else title
    src = a.get("source", "")
    ts = a.get("published_at", "")[:16].replace("T", " ")
    score = a.get("relevance_score", 0)
    uc = urgency_chip(a.get("urgency", "low"))
    summary = a.get("short_summary", "")
    wim = a.get("why_it_matters", "")
    wim_html = f'<div class="wim">Why it matters: {wim}</div>' if wim else ""
    tags = a.get("tags", [])
    cat = a.get("category", "")
    chips = f'<span class="chip chip-cat">{cat}</span>' if cat else ""
    chips += "".join(f'<span class="chip chip-tag">{t}</span>' for t in tags[:4])
    return (
        f'<div class="hero">'
        f'<div class="label"><span class="pulse"></span> TOP STORY</div>'
        f'<h3>{th}</h3>'
        f'<div class="meta">{src} &middot; {ts} &middot; {uc} &middot; Relevance: {score:.0%}</div>'
        f'<div class="body">{summary}</div>'
        f'{wim_html}'
        f'<div class="chips">{chips}</div>'
        f'</div>'
    )


def secondary_card(label, label_cls, a):
    """Compact secondary briefing card."""
    if not a:
        return (
            f'<div class="sec-card">'
            f'<div class="label {label_cls}">{label}</div>'
            f'<h4>No stories at this time</h4>'
            f'<p>—</p></div>'
        )
    title = a.get("title", "")
    summary = a.get("short_summary", "")[:180]
    return (
        f'<div class="sec-card">'
        f'<div class="label {label_cls}">{label}</div>'
        f'<h4>{title}</h4>'
        f'<p>{summary}</p></div>'
    )


def _time_ago(iso_ts: str) -> str:
    """Convert ISO timestamp to '2h ago' style label."""
    if not iso_ts:
        return ""
    try:
        dt = datetime.fromisoformat(iso_ts.replace("Z", "+00:00"))
        delta = datetime.now(timezone.utc) - dt
        hours = delta.total_seconds() / 3600
        if hours < 1:
            return f"{int(delta.total_seconds() / 60)}m ago"
        if hours < 24:
            return f"{int(hours)}h ago"
        return f"{int(hours / 24)}d ago"
    except (ValueError, TypeError):
        return ""


def article_card(a):
    """Standard article card with chip system and freshness."""
    title = a.get("title", "Untitled")
    url = a.get("url", "")
    th = f'<a href="{url}" target="_blank">{title}</a>' if url else title
    src = a.get("source", "Unknown")
    ts = a.get("published_at", "")[:16].replace("T", " ")
    age = _time_ago(a.get("published_at", ""))
    age_html = f' &middot; <span style="color:#3D5A80">{age}</span>' if age else ""
    score = a.get("relevance_score", 0)
    uc = urgency_chip(a.get("urgency", "low"))
    summary = a.get("short_summary", "")
    wim = a.get("why_it_matters", "")
    wim_html = f'<div class="wim">Why it matters: {wim}</div>' if wim else ""
    cat = a.get("category", "")
    region = a.get("region", "")
    tags = a.get("tags", [])
    chips = f'<span class="chip chip-cat">{cat}</span>' if cat else ""
    if region and region != "Global":
        chips += f'<span class="chip chip-tag">{region}</span>'
    chips += "".join(f'<span class="chip chip-tag">{t}</span>' for t in tags[:3])
    return (
        f'<div class="ac">'
        f'<div class="ac-top"><h4>{th}</h4><span class="ac-score">{score:.0%}</span></div>'
        f'<div class="meta">{src} &middot; {ts}{age_html} &middot; {uc}</div>'
        f'<div class="summary">{summary}</div>'
        f'{wim_html}'
        f'<div class="chips">{chips}</div>'
        f'</div>'
    )


def briefing_card(title, body):
    return f'<div class="brief"><h4>{title}</h4><p>{body}</p></div>'


def asset_card_html(v):
    d = v["direction"]
    dcls = {"up": "up", "down": "down", "volatile": "volatile"}.get(d, "neutral")
    headlines_li = "".join(f"<li>{h}</li>" for h in v.get("supporting_headlines", [])[:3])
    headlines_html = f'<ul class="headlines">{headlines_li}</ul>' if headlines_li else ""
    themes = ", ".join(v.get("driving_themes", []))
    return (
        f'<div class="asc">'
        f'<div class="hdr"><span class="emoji">{v["emoji"]}</span>'
        f'<span class="name">{v["label"]}</span>'
        f'<span class="dir {dcls}">{d.upper()}</span></div>'
        f'<div class="row"><strong>Immediate:</strong> {v["immediate_reaction"]}</div>'
        f'<div class="row"><strong>Short-term:</strong> {v["short_term_direction"]}</div>'
        f'<div class="row"><strong>Risk trigger:</strong> {v["risk_reversal_trigger"]}</div>'
        f'<div class="row"><strong>Why it matters:</strong> {v["why_this_matters"]}</div>'
        f'<div class="row"><strong>Drivers:</strong> {themes}</div>'
        f'<div class="conf">Confidence: {v["confidence"]:.0%} &middot; Signal: {v["signal_strength"]}</div>'
        f'{headlines_html}'
        f'</div>'
    )


def scenario_card(label, text, cls):
    return f'<div class="sc"><div class="lbl {cls}">{label}</div><p>{text}</p></div>'


def section_header(title, subtitle=""):
    sub = f'<div class="sub">{subtitle}</div>' if subtitle else ""
    return f'<div class="sh"><h2>{title}</h2>{sub}</div>'


def _parse_date(iso):
    if not iso:
        return None
    try:
        return datetime.fromisoformat(iso.replace("Z", "+00:00")).date()
    except (ValueError, TypeError):
        return None


# ╔═════════════════════════════════════════════════════════════════════════╗
# ║  LOAD DATA                                                            ║
# ╚═════════════════════════════════════════════════════════════════════════╝
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
freshness = get_freshness_info()

# Compute signal values from articles
_cat_counts = Counter(a.get("category", "") for a in all_articles)
_ai_count = _cat_counts.get("AI", 0) + _cat_counts.get("AI Coding", 0) + _cat_counts.get("AI Trading", 0)
_geo_count = _cat_counts.get("Geopolitics", 0)
_market_count = _cat_counts.get("Markets", 0)
_energy_count = _cat_counts.get("Energy", 0)
_breaking_count = sum(1 for a in all_articles if a.get("urgency") == "breaking")
_source_count = len(db_sources)


# ╔═════════════════════════════════════════════════════════════════════════╗
# ║  SIDEBAR                                                              ║
# ╚═════════════════════════════════════════════════════════════════════════╝
with st.sidebar:
    st.markdown('<div class="sb-hdr">Refresh</div>', unsafe_allow_html=True)
    _rc1, _rc2 = st.columns([1, 1])
    with _rc1:
        if st.button("Refresh Now", use_container_width=True, type="primary"):
            st.rerun()
    with _rc2:
        auto_refresh_on = st.toggle("Auto", value=False, key="_auto_refresh_toggle")

    INTERVAL_OPTIONS = {"Manual only": 0, "1 minute": 60, "5 minutes": 300, "15 minutes": 900}
    if auto_refresh_on:
        interval_label = st.selectbox(
            "Interval", options=list(INTERVAL_OPTIONS.keys())[1:],
            index=0, key="_refresh_interval",
        )
        refresh_seconds = INTERVAL_OPTIONS[interval_label]
    else:
        interval_label = "Manual only"
        refresh_seconds = 0

    now_for_display = datetime.now(timezone.utc).strftime("%H:%M:%S UTC")
    st.caption(f"Loaded: {now_for_display}")

    st.markdown('<div class="sb-hdr">Intelligence Filters</div>', unsafe_allow_html=True)
    f_categories = st.multiselect("Category", options=db_categories, default=[], placeholder="All categories")
    f_regions = st.multiselect("Region", options=db_regions, default=[], placeholder="All regions")
    f_sources = st.multiselect("Source", options=db_sources, default=[], placeholder="All sources")
    f_urgency = st.multiselect("Urgency", options=["breaking", "high", "medium", "low"], default=[], placeholder="All levels")
    f_relevance = st.slider("Min relevance", 0.0, 1.0, 0.0, 0.05)
    dates = [_parse_date(a.get("published_at", "")) for a in all_articles]
    valid_dates = [d for d in dates if d]
    if valid_dates:
        f_date_range = st.date_input("Date range", value=(min(valid_dates), max(valid_dates)),
                                     min_value=min(valid_dates), max_value=max(valid_dates))
    else:
        f_date_range = None
    f_keyword = st.text_input("Keyword search", placeholder="Search titles & summaries...")

    st.markdown('<div class="sb-hdr">System</div>', unsafe_allow_html=True)
    mode_label = "LLM" if settings.llm_enabled else "Rules"
    news_label = "NewsAPI + RSS" if settings.newsapi_enabled else "RSS only"
    st.caption(f"Agent: **{mode_label}** · Providers: **{news_label}**")
    st.caption(f"Articles: **{total_articles}** · Runs: **{total_runs}**")


# ╔═════════════════════════════════════════════════════════════════════════╗
# ║  AUTO-REFRESH FRAGMENT                                                ║
# ╚═════════════════════════════════════════════════════════════════════════╝
if refresh_seconds > 0:
    @st.fragment(run_every=timedelta(seconds=refresh_seconds))
    def _auto_refresher():
        if "_arf_ts" not in st.session_state:
            st.session_state._arf_ts = time.time()
            return
        if time.time() - st.session_state._arf_ts >= refresh_seconds * 0.8:
            st.session_state._arf_ts = time.time()
            st.rerun(scope="app")
    _auto_refresher()


# ╔═════════════════════════════════════════════════════════════════════════╗
# ║  COMMAND CENTER HEADER                                                ║
# ╚═════════════════════════════════════════════════════════════════════════╝
sweep_ts = last_run["created_at"][:16].replace("T", " ") + " UTC" if last_run else "—"
hours_ago = freshness["hours_since_sweep"]
age_str = f"{hours_ago:.1f}h ago" if hours_ago is not None else "never"
st.markdown(
    f'<div class="cmd-hdr">'
    f'<div class="title">AI <span>Chief Agent</span></div>'
    f'<div class="meta">Sweep: {sweep_ts} ({age_str}) &nbsp;·&nbsp; {mode_label} mode &nbsp;·&nbsp; {news_label}</div>'
    f'</div>',
    unsafe_allow_html=True,
)

# Stale data warning
if freshness["is_stale"]:
    st.warning(
        f"Data may be stale — last sweep was {hours_ago:.1f} hours ago "
        f"({freshness['last_sweep_article_count']} articles). "
        f"Run `python main.py` to fetch fresh intelligence.",
        icon="⚠️",
    )


# ╔═════════════════════════════════════════════════════════════════════════╗
# ║  SIGNAL STRIP                                                         ║
# ╚═════════════════════════════════════════════════════════════════════════╝
ai_level = "hi" if _ai_count >= 5 else "elev" if _ai_count >= 2 else "low"
ai_label = "HIGH" if _ai_count >= 5 else "MODERATE" if _ai_count >= 2 else "LOW"
geo_level = "vol" if _geo_count >= 5 else "elev" if _geo_count >= 2 else "low"
geo_label = "ELEVATED" if _geo_count >= 2 else "CALM"
mkt_level = "elev" if _market_count >= 3 else "low"
mkt_label = "ACTIVE" if _market_count >= 3 else "QUIET"
nrg_level = "elev" if _energy_count >= 2 else "low"
nrg_label = "SENSITIVE" if _energy_count >= 2 else "STABLE"
brk_level = "vol" if _breaking_count >= 2 else "elev" if _breaking_count >= 1 else "low"

st.markdown(
    '<div class="sig-strip">'
    + signal_pill("AI PULSE", ai_label, ai_level)
    + signal_pill("GEO RISK", geo_label, geo_level)
    + signal_pill("MARKETS", mkt_label, mkt_level)
    + signal_pill("ENERGY", nrg_label, nrg_level)
    + signal_pill("BREAKING", str(_breaking_count), brk_level)
    + signal_pill("SOURCES", str(_source_count), "info")
    + signal_pill("LAST SWEEP", age_str, "vol" if freshness["is_stale"] else "info")
    + signal_pill("NEW ARTICLES", str(freshness["last_sweep_article_count"]), "info")
    + '</div>',
    unsafe_allow_html=True,
)


# ╔═════════════════════════════════════════════════════════════════════════╗
# ║  TABS                                                                 ║
# ╚═════════════════════════════════════════════════════════════════════════╝
tab_feed, tab_macro = st.tabs(["INTELLIGENCE FEED", "MACRO INTELLIGENCE"])


# ═══════════════════════════ TAB 1: FEED ═════════════════════════════════
with tab_feed:

    # Apply filters
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
    filtered.sort(key=lambda a: a.get("relevance_score", 0), reverse=True)

    # ── KPI cards ──
    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        st.markdown(kpi("Total Articles", total_articles, "b"), unsafe_allow_html=True)
    with k2:
        st.markdown(kpi("Pipeline Runs", total_runs, "p"), unsafe_allow_html=True)
    with k3:
        st.markdown(kpi("QA Passed", qa_stats["passed"], "g"), unsafe_allow_html=True)
    with k4:
        st.markdown(kpi("QA Failed", qa_stats["failed"], "r"), unsafe_allow_html=True)
    with k5:
        st.markdown(kpi("Showing", f'{len(filtered)}/{total_articles}', "a"), unsafe_allow_html=True)

    st.markdown('<hr class="sd">', unsafe_allow_html=True)

    # ── Most Important Right Now ──
    st.markdown(section_header("Most Important Right Now", "Priority intelligence from the latest sweep"), unsafe_allow_html=True)

    if filtered:
        # Hero: top story (full width)
        st.markdown(hero_card(filtered[0]), unsafe_allow_html=True)

        # Secondary row: breaking / AI opportunity / geo risk
        breaking_list = [a for a in filtered if a.get("urgency") == "breaking"]
        ai_list = [a for a in filtered if a.get("category") in ("AI", "AI Coding", "AI Trading")]
        risk_list = [a for a in filtered if a.get("market_impact") == "high"]

        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            st.markdown(secondary_card("BREAKING", "l-brk", breaking_list[0] if breaking_list else None), unsafe_allow_html=True)
        with sc2:
            st.markdown(secondary_card("AI OPPORTUNITY", "l-ai", ai_list[0] if ai_list else None), unsafe_allow_html=True)
        with sc3:
            st.markdown(secondary_card("MARKET / GEO RISK", "l-risk", risk_list[0] if risk_list else None), unsafe_allow_html=True)
    else:
        st.info("No articles match current filters. Run `python main.py` to collect intelligence.")

    st.markdown('<hr class="sd">', unsafe_allow_html=True)

    # ── Category sections ──
    def _render_section(title, items, max_items=5):
        if not items:
            return
        st.markdown(section_header(title, f"{len(items)} articles"), unsafe_allow_html=True)
        for a in items[:max_items]:
            st.markdown(article_card(a), unsafe_allow_html=True)
        if len(items) > max_items:
            with st.expander(f"Show {len(items) - max_items} more"):
                for a in items[max_items:]:
                    st.markdown(article_card(a), unsafe_allow_html=True)

    _render_section("Breaking News", [a for a in filtered if a.get("urgency") == "breaking"])
    _render_section("AI News", [a for a in filtered if a.get("category") == "AI"])
    _render_section("AI Coding", [a for a in filtered if a.get("category") == "AI Coding"])
    _render_section("AI Trading", [a for a in filtered if a.get("category") == "AI Trading"])
    _render_section("Global News", [a for a in filtered if a.get("category") == "Global News"])
    _render_section("Geopolitics", [a for a in filtered if a.get("category") == "Geopolitics"])
    _render_section("Markets", [a for a in filtered if a.get("category") == "Markets"])
    _render_section("Energy", [a for a in filtered if a.get("category") == "Energy"])

    st.markdown('<hr class="sd">', unsafe_allow_html=True)

    # ── Trends & Insights ──
    st.markdown(section_header("Trends & Insights", "Distribution analysis"), unsafe_allow_html=True)
    if filtered:
        ch1, ch2 = st.columns(2)
        with ch1:
            st.markdown("##### Category Distribution")
            cat_counts = Counter(a.get("category", "Unknown") for a in filtered)
            df_cats = pd.DataFrame(cat_counts.most_common(10), columns=["Category", "Count"])
            st.bar_chart(df_cats, x="Category", y="Count", color="#00D4FF")
        with ch2:
            st.markdown("##### Topic Frequency")
            tag_counter = Counter()
            for a in filtered:
                for t in a.get("tags", []):
                    tag_counter[t] += 1
            if tag_counter:
                df_tags = pd.DataFrame(tag_counter.most_common(12), columns=["Topic", "Count"])
                st.bar_chart(df_tags, x="Topic", y="Count", color="#FFB800", horizontal=True)
            else:
                st.info("No topic tags detected.")


# ═══════════════════════ TAB 2: MACRO INTEL ══════════════════════════════
with tab_macro:

    if not briefing_data:
        st.info("No macro briefing available yet. Run `python main.py` to generate one.")
    else:
        b = briefing_data

        # ── Macro KPIs ──
        m1, m2, m3, m4, m5 = st.columns(5)
        with m1:
            st.markdown(kpi("Top Theme", b.get("top_theme", "—"), "a"), unsafe_allow_html=True)
        with m2:
            rl = b.get("overall_risk_level", "low")
            rc = "r" if rl == "high" else "a" if rl == "medium" else "g"
            st.markdown(kpi("Risk Level", rl.upper(), rc), unsafe_allow_html=True)
        with m3:
            st.markdown(kpi("Confidence", f'{b.get("overall_confidence", 0):.0%}', "b"), unsafe_allow_html=True)
        with m4:
            st.markdown(kpi("Assets Hit", len(b.get("asset_views", [])), "p"), unsafe_allow_html=True)
        with m5:
            st.markdown(kpi("Rules Fired", b.get("rule_triggers", 0), "b"), unsafe_allow_html=True)

        st.markdown('<hr class="sd">', unsafe_allow_html=True)

        # ── Executive Summary ──
        st.markdown(section_header("Executive Summary", "Macro intelligence briefing"), unsafe_allow_html=True)
        es1, es2 = st.columns(2)
        with es1:
            st.markdown(briefing_card("What Happened", "<br>".join(f"&bull; {h}" for h in b.get("what_happened", []))), unsafe_allow_html=True)
            st.markdown(briefing_card("Market Reaction", b.get("market_reaction", "")), unsafe_allow_html=True)
            st.markdown(briefing_card("My Market Read", b.get("market_read", "")), unsafe_allow_html=True)
        with es2:
            st.markdown(briefing_card("Probable Direction", b.get("probable_direction", "")), unsafe_allow_html=True)
            st.markdown(briefing_card("Why It Matters", b.get("why_it_matters", "")), unsafe_allow_html=True)
            watch = b.get("what_to_watch", [])
            st.markdown(briefing_card("What To Watch Now", "<br>".join(f"&bull; {w}" for w in watch) if watch else "No specific items."), unsafe_allow_html=True)

        st.markdown(briefing_card("Conclusion", b.get("conclusion", "")), unsafe_allow_html=True)

        st.markdown('<hr class="sd">', unsafe_allow_html=True)

        # ── Scenario Analysis ──
        st.markdown(section_header("Scenario Analysis", "Probabilistic outcome mapping"), unsafe_allow_html=True)
        sc1, sc2, sc3 = st.columns(3)
        scenarios = b.get("scenarios", {})
        with sc1:
            st.markdown(scenario_card("Bull Case", scenarios.get("bull_case", "—"), "bull"), unsafe_allow_html=True)
        with sc2:
            st.markdown(scenario_card("Base Case", scenarios.get("base_case", "—"), "base"), unsafe_allow_html=True)
        with sc3:
            st.markdown(scenario_card("Risk Case", scenarios.get("risk_case", "—"), "risk"), unsafe_allow_html=True)

        st.markdown('<hr class="sd">', unsafe_allow_html=True)

        # ── Asset Breakdown ──
        asset_views = b.get("asset_views", [])
        st.markdown(section_header("Asset-Class Breakdown", f"{len(asset_views)} assets impacted"), unsafe_allow_html=True)

        acol1, acol2, acol3 = st.columns(3)
        with acol1:
            f_asset_dir = st.multiselect("Direction", options=["up", "down", "volatile", "neutral"], default=[], placeholder="All", key="macro_dir")
        with acol2:
            all_asset_labels = sorted(set(v.get("label", "") for v in asset_views))
            f_asset_class = st.multiselect("Asset", options=all_asset_labels, default=[], placeholder="All", key="macro_asset")
        with acol3:
            f_min_conf = st.slider("Min confidence", 0.0, 1.0, 0.0, 0.05, key="macro_conf")

        fv = asset_views
        if f_asset_dir:
            fv = [v for v in fv if v.get("direction") in f_asset_dir]
        if f_asset_class:
            fv = [v for v in fv if v.get("label") in f_asset_class]
        if f_min_conf > 0:
            fv = [v for v in fv if v.get("confidence", 0) >= f_min_conf]

        if fv:
            left_col, right_col = st.columns(2)
            for i, v in enumerate(fv):
                with left_col if i % 2 == 0 else right_col:
                    st.markdown(asset_card_html(v), unsafe_allow_html=True)
        else:
            st.info("No asset views match filters.")

        st.markdown('<hr class="sd">', unsafe_allow_html=True)

        # ── Theme Distribution ──
        all_themes = b.get("all_themes", [])
        if all_themes:
            st.markdown(section_header("Active Themes", "Detected macro narratives"), unsafe_allow_html=True)
            df_themes = pd.DataFrame(all_themes)
            if not df_themes.empty:
                st.bar_chart(df_themes, x="theme", y="count", color="#BB86FC")


# ╔═════════════════════════════════════════════════════════════════════════╗
# ║  FOOTER                                                               ║
# ╚═════════════════════════════════════════════════════════════════════════╝
st.markdown('<hr class="sd">', unsafe_allow_html=True)
now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
refresh_status = f"Auto: {interval_label}" if refresh_seconds > 0 else "Manual"
st.markdown(
    f'<div class="ftr">'
    f'{len(all_articles)} articles &nbsp;&middot;&nbsp; '
    f'{now_utc} UTC &nbsp;&middot;&nbsp; '
    f'Refresh: {refresh_status} &nbsp;&middot;&nbsp; '
    f'{mode_label} mode'
    f'</div>',
    unsafe_allow_html=True,
)

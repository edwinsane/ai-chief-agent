"""
AI Chief Agent — Global Intelligence Command Center.

Three-tab premium dashboard:
  1. Intelligence Feed — hero, actionable panels, articles, Plotly charts
  2. World Intel Map — Plotly globe with event markers
  3. Macro Intelligence — briefing, scenarios, assets, predictions
"""

import json, sys, time
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.core.config import settings  # noqa: E402
from app.core.geo_coords import infer_coordinates  # noqa: E402
from app.core.predictions import generate_outlook  # noqa: E402
from app.storage.database import (  # noqa: E402
    get_article_count, get_articles, get_briefings,
    get_distinct_categories, get_distinct_regions, get_distinct_sources,
    get_freshness_info, get_last_run, get_latest_briefing,
    get_qa_stats, get_run_count, init_db,
)

# ═══════════════════════ SETUP ═══════════════════════════════════════════
st.set_page_config(page_title="AI Chief Agent", page_icon="🤖", layout="wide")
init_db()

# Plotly dark template
_PLT = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#6B9CC0", size=11),
    margin=dict(l=0, r=0, t=30, b=0),
    colorway=["#00D4FF", "#FFB800", "#00E676", "#FF5252", "#BB86FC",
              "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7"],
)

# ═══════════════════════ CSS ═════════════════════════════════════════════
st.markdown("""<style>
.block-container{padding-top:.6rem;max-width:1480px}
html,body,[data-testid="stAppViewContainer"]{background:#060A12!important}
[data-testid="stHeader"]{background:transparent!important}
[data-testid="stBottomBlockContainer"]{background:#060A12!important}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#050810 0%,#060A12 100%)!important;border-right:1px solid #0F1A2E}
[data-testid="stSidebar"] hr{border-color:#0F1A2E!important;margin:.6rem 0!important}
[data-testid="stTabs"] button{font-size:.72rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;padding:.55rem 1.4rem;color:#2A4060;border:none;border-bottom:2px solid transparent;border-radius:0;transition:all .2s}
[data-testid="stTabs"] button[aria-selected="true"]{color:#00D4FF;border-bottom-color:#00D4FF;background:linear-gradient(180deg,rgba(0,212,255,.03) 0%,transparent 100%)}
[data-testid="stTabs"] button:hover:not([aria-selected="true"]){color:#4A7090}
[data-testid="stTabs"] [role="tablist"]{border-bottom:1px solid #0F1A2E;gap:0}
[data-testid="stExpander"]{border:1px solid #0F1A2E!important;border-radius:8px!important;background:#080D18!important}
[data-testid="stExpander"] summary{font-size:.75rem;color:#2A4060;font-weight:600}
[data-testid="stExpander"] summary:hover{color:#00D4FF}

.sd{border:none;height:1px;background:linear-gradient(90deg,transparent,#0F1A2E 25%,#1A3050 50%,#0F1A2E 75%,transparent);margin:1.8rem 0}
.sb-hdr{font-size:.58rem;text-transform:uppercase;letter-spacing:.12em;color:#1A3050;font-weight:700;margin:.8rem 0 .3rem 0}

/* command header */
.cmd{display:flex;align-items:baseline;justify-content:space-between;padding:.4rem 0 .6rem;border-bottom:1px solid #0F1A2E;margin-bottom:.6rem}
.cmd .t{font-size:1.3rem;font-weight:800;color:#D0D8E4;letter-spacing:-.02em}.cmd .t span{color:#00D4FF}
.cmd .m{font-size:.6rem;color:#1A3050;letter-spacing:.06em;text-transform:uppercase}

/* signal strip */
.sig{display:flex;flex-wrap:wrap;gap:.4rem;padding:.55rem .8rem;margin:.5rem 0 1rem;background:#080D18;border:1px solid #0F1A2E;border-radius:8px}
.sp{display:inline-flex;align-items:center;gap:.3rem;padding:.22rem .55rem;border-radius:5px;font-size:.6rem;font-weight:700;letter-spacing:.03em;border:1px solid}
.sp .d{width:5px;height:5px;border-radius:50%;flex-shrink:0}
.sp.hi{color:#00E676;border-color:rgba(0,230,118,.18);background:rgba(0,230,118,.04)}.sp.hi .d{background:#00E676;box-shadow:0 0 5px rgba(0,230,118,.5)}
.sp.el{color:#FFB800;border-color:rgba(255,184,0,.18);background:rgba(255,184,0,.04)}.sp.el .d{background:#FFB800;box-shadow:0 0 5px rgba(255,184,0,.5)}
.sp.cr{color:#FF5252;border-color:rgba(255,82,82,.18);background:rgba(255,82,82,.04)}.sp.cr .d{background:#FF5252;box-shadow:0 0 5px rgba(255,82,82,.5)}
.sp.lo{color:#1A3050;border-color:rgba(26,48,80,.3);background:rgba(26,48,80,.04)}.sp.lo .d{background:#1A3050}
.sp.nf{color:#4A7090;border-color:rgba(74,112,144,.18);background:rgba(74,112,144,.04)}.sp.nf .d{background:#00D4FF;box-shadow:0 0 4px rgba(0,212,255,.3)}

/* KPI */
.k{background:linear-gradient(160deg,#0A1020 0%,#080D18 100%);border:1px solid #0F1A2E;border-radius:10px;padding:1rem .8rem;text-align:center;position:relative;overflow:hidden;box-shadow:0 3px 16px rgba(0,0,0,.4);transition:transform .2s,box-shadow .2s}
.k:hover{transform:translateY(-2px);box-shadow:0 6px 24px rgba(0,0,0,.5)}
.k::before{content:"";position:absolute;top:0;left:0;right:0;height:2px;border-radius:10px 10px 0 0}
.k.kb::before{background:#00D4FF}.k.kg::before{background:#00E676}.k.kr::before{background:#FF5252}.k.ka::before{background:#FFB800}.k.kp::before{background:#BB86FC}
.k .kl{font-size:.55rem;color:#1A3050;text-transform:uppercase;letter-spacing:.1em;font-weight:600;margin-bottom:.3rem}
.k .kv{font-size:1.6rem;font-weight:800;line-height:1.15}
.k .kv.b{color:#00D4FF}.k .kv.g{color:#00E676}.k .kv.r{color:#FF5252}.k .kv.a{color:#FFB800}.k .kv.p{color:#BB86FC}.k .kv.w{color:#D0D8E4}

/* hero */
.hero{background:linear-gradient(145deg,#0A1020 0%,#080D18 100%);border:1px solid #0F1A2E;border-left:3px solid #00D4FF;border-radius:12px;padding:1.4rem 1.6rem;margin-bottom:1rem;box-shadow:0 3px 20px rgba(0,212,255,.04);position:relative;overflow:hidden}
.hero::after{content:"";position:absolute;top:0;right:0;width:180px;height:100%;background:radial-gradient(ellipse at top right,rgba(0,212,255,.03) 0%,transparent 70%);pointer-events:none}
.hero .hl{font-size:.58rem;font-weight:700;text-transform:uppercase;letter-spacing:.1em;color:#00D4FF;margin-bottom:.5rem;display:flex;align-items:center;gap:.35rem}
.hero .hl .p{display:inline-block;width:6px;height:6px;border-radius:50%;background:#00D4FF;box-shadow:0 0 7px rgba(0,212,255,.6);animation:pb 2s ease-in-out infinite}
.hero h3{margin:0 0 .4rem!important;font-size:1.15rem!important;font-weight:800!important;color:#D0D8E4!important;line-height:1.3!important}
.hero h3 a{color:#D0D8E4!important;text-decoration:none!important}.hero h3 a:hover{color:#00D4FF!important}
.hero .mt{font-size:.65rem;color:#2A4060;margin-bottom:.5rem}
.hero .bd{color:#6B9CC0;font-size:.84rem;line-height:1.6;margin-bottom:.5rem}
.hero .wm{color:#FFB800;font-size:.78rem;font-style:italic;padding:.4rem 0 .4rem .7rem;border-left:2px solid rgba(255,184,0,.25);margin-bottom:.5rem}
@keyframes pb{0%,100%{opacity:1}50%{opacity:.35}}

/* secondary card */
.sc2{background:#0A1020;border:1px solid #0F1A2E;border-radius:10px;padding:1rem 1.1rem;box-shadow:0 2px 12px rgba(0,0,0,.3);height:100%;transition:border-color .2s}
.sc2:hover{border-color:#1A3050}
.sc2 .sl{font-size:.55rem;font-weight:700;text-transform:uppercase;letter-spacing:.08em;margin-bottom:.4rem;display:flex;align-items:center;gap:.3rem}
.sc2 .sl.lb{color:#FF5252}.sc2 .sl.la{color:#00D4FF}.sc2 .sl.lr{color:#FFB800}.sc2 .sl.lm{color:#BB86FC}.sc2 .sl.le{color:#00E676}
.sc2 h4{margin:0 0 .3rem;color:#D0D8E4;font-size:.88rem;font-weight:700;line-height:1.3}
.sc2 p{margin:0;color:#4A6A8A;font-size:.78rem;line-height:1.5}

/* article card */
.ac{background:#0A1020;border:1px solid #0F1A2E;border-radius:10px;padding:1rem 1.2rem;margin-bottom:.65rem;transition:border-color .2s,box-shadow .2s}
.ac:hover{border-color:#1A3050;box-shadow:0 3px 16px rgba(0,212,255,.03)}
.ac .at{display:flex;align-items:flex-start;justify-content:space-between;gap:.6rem;margin-bottom:.3rem}
.ac h4{margin:0;color:#D0D8E4;font-size:.88rem;font-weight:700;line-height:1.3;flex:1}
.ac h4 a{color:#D0D8E4!important;text-decoration:none}.ac h4 a:hover{color:#00D4FF!important}
.ac .as{font-size:.65rem;font-weight:700;color:#00D4FF;white-space:nowrap;padding:.12rem .4rem;border:1px solid rgba(0,212,255,.18);border-radius:4px;background:rgba(0,212,255,.04)}
.ac .mt{font-size:.62rem;color:#2A4060;margin-bottom:.4rem}
.ac .bd{color:#4A6A8A;font-size:.8rem;line-height:1.55;margin-bottom:.4rem}
.ac .wm{color:#FFB800;font-size:.75rem;font-style:italic;padding:.3rem 0 .3rem .6rem;border-left:2px solid rgba(255,184,0,.2);margin-bottom:.4rem}
.ac .ch{display:flex;flex-wrap:wrap;gap:.25rem;margin-top:.25rem}

/* chips */
.c{display:inline-block;padding:.12rem .4rem;border-radius:4px;font-size:.58rem;font-weight:600;letter-spacing:.02em;border:1px solid}
.cc{color:#4ECDC4;border-color:rgba(0,212,255,.12);background:rgba(0,212,255,.04)}
.ct{color:#4A6A8A;border-color:rgba(74,106,138,.12);background:rgba(74,106,138,.04)}
.cb{color:#FF5252;border-color:rgba(255,82,82,.2);background:rgba(255,82,82,.06);animation:pr 2s ease-in-out infinite}
.chi{color:#FFB800;border-color:rgba(255,184,0,.15);background:rgba(255,184,0,.04)}
.cm{color:#00D4FF;border-color:rgba(0,212,255,.12);background:rgba(0,212,255,.04)}
.cl{color:#1A3A50;border-color:rgba(0,230,118,.1);background:rgba(0,230,118,.03)}
@keyframes pr{0%,100%{box-shadow:0 0 2px rgba(255,82,82,.1)}50%{box-shadow:0 0 8px rgba(255,82,82,.25)}}

/* briefing */
.bf{background:#0A1020;border:1px solid #0F1A2E;border-left:3px solid #FFB800;border-radius:10px;padding:1.1rem 1.3rem;margin-bottom:.65rem;transition:border-color .2s}
.bf:hover{border-color:#1A3050}
.bf h4{margin:0 0 .4rem;color:#FFB800;font-size:.62rem;text-transform:uppercase;letter-spacing:.08em;font-weight:700}
.bf p{margin:0;color:#6B9CC0;font-size:.82rem;line-height:1.6}.bf p strong{color:#A0B4CC}

/* asset card */
.asc{background:#0A1020;border:1px solid #0F1A2E;border-radius:10px;padding:1.1rem 1.2rem;margin-bottom:.65rem;transition:border-color .2s}
.asc:hover{border-color:#1A3050}
.asc .hd{display:flex;align-items:center;gap:.5rem;margin-bottom:.5rem;padding-bottom:.4rem;border-bottom:1px solid #0F1A2E}
.asc .hd .em{font-size:1.2rem}.asc .hd .nm{font-size:.9rem;font-weight:800;color:#D0D8E4;flex:1}
.asc .dr{display:inline-block;padding:.15rem .5rem;border-radius:5px;font-size:.62rem;font-weight:700;letter-spacing:.04em;border:1px solid}
.asc .dr.up{color:#00E676;border-color:rgba(0,230,118,.2);background:rgba(0,230,118,.06)}
.asc .dr.dn{color:#FF5252;border-color:rgba(255,82,82,.2);background:rgba(255,82,82,.06)}
.asc .dr.vl{color:#FFB800;border-color:rgba(255,184,0,.2);background:rgba(255,184,0,.06)}
.asc .dr.nt{color:#4A6A8A;border-color:rgba(74,106,138,.15);background:rgba(74,106,138,.04)}
.asc .rw{font-size:.78rem;color:#4A6A8A;margin-bottom:.25rem;line-height:1.45}.asc .rw strong{color:#6B9CC0;font-weight:600}
.asc .cf{font-size:.65rem;color:#1A3050;margin-top:.4rem;padding-top:.4rem;border-top:1px solid #0F1A2E}

/* scenario */
.sn{background:#0A1020;border:1px solid #0F1A2E;border-radius:10px;padding:1rem 1.1rem;margin-bottom:.6rem;transition:border-color .2s}
.sn:hover{border-color:#1A3050}
.sn .lb{font-size:.62rem;font-weight:700;text-transform:uppercase;letter-spacing:.08em;margin-bottom:.3rem}
.sn .lb.bu{color:#00E676}.sn .lb.ba{color:#00D4FF}.sn .lb.ri{color:#FF5252}
.sn p{margin:0;color:#4A6A8A;font-size:.78rem;line-height:1.55}
.sn:has(.lb.bu){border-left:2px solid rgba(0,230,118,.3)}
.sn:has(.lb.ba){border-left:2px solid rgba(0,212,255,.3)}
.sn:has(.lb.ri){border-left:2px solid rgba(255,82,82,.3)}

/* prediction card */
.pd{background:#0A1020;border:1px solid #0F1A2E;border-radius:10px;padding:.9rem 1rem;margin-bottom:.5rem;transition:border-color .2s}
.pd:hover{border-color:#1A3050}
.pd .pl{font-size:.55rem;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:#2A4060;margin-bottom:.25rem}
.pd .pv{font-size:1rem;font-weight:800;margin-bottom:.2rem}
.pd .pv.hi{color:#00E676}.pd .pv.el{color:#FFB800}.pd .pv.cr{color:#FF5252}.pd .pv.lo{color:#2A4060}.pd .pv.nf{color:#4A7090}
.pd .pp{font-size:.7rem;color:#4A6A8A;line-height:1.45;margin:0}
.pd .ps{font-size:.6rem;color:#1A3050;margin-top:.2rem}

/* section header */
.sh{margin:0 0 1rem;padding-bottom:.5rem;border-bottom:1px solid #0F1A2E}
.sh h2{margin:0!important;padding:0!important;font-size:.9rem!important;font-weight:700!important;color:#D0D8E4!important;letter-spacing:-.01em!important}
.sh .su{font-size:.58rem;color:#1A3050;text-transform:uppercase;letter-spacing:.08em;margin-top:.1rem}

.ftr{text-align:center;color:#1A3050;font-size:.58rem;letter-spacing:.06em;padding:.6rem 0;text-transform:uppercase}
</style>""", unsafe_allow_html=True)

# ═══════════════════════ HELPERS ═════════════════════════════════════════

def _kpi(label, value, color="b"):
    return f'<div class="k k{color}"><div class="kl">{label}</div><div class="kv {color}">{value}</div></div>'

def _pill(label, value, level):
    return f'<span class="sp {level}"><span class="d"></span>{label}: {value}</span>'

def _uchip(u):
    cls={"breaking":"cb","high":"chi","medium":"cm","low":"cl"}.get(u,"cl")
    return f'<span class="c {cls}">{u.upper()}</span>'

def _time_ago(iso):
    if not iso: return ""
    try:
        dt=datetime.fromisoformat(iso.replace("Z","+00:00"))
        h=(datetime.now(timezone.utc)-dt).total_seconds()/3600
        if h<1: return f"{int(h*60)}m ago"
        if h<24: return f"{int(h)}h ago"
        return f"{int(h/24)}d ago"
    except: return ""

def _hero(a):
    t=a.get("title","");u=a.get("url","");th=f'<a href="{u}" target="_blank">{t}</a>' if u else t
    s=a.get("source","");ts=a.get("published_at","")[:16].replace("T"," ");age=_time_ago(a.get("published_at",""))
    sc=a.get("relevance_score",0);uc=_uchip(a.get("urgency","low"))
    sm=a.get("short_summary","");wim=a.get("why_it_matters","")
    wh=f'<div class="wm">Why it matters: {wim}</div>' if wim else ""
    cat=a.get("category","");tags=a.get("tags",[])
    ch=f'<span class="c cc">{cat}</span>' if cat else ""
    r=a.get("region","");ch+=f'<span class="c ct">{r}</span>' if r and r!="Global" else ""
    ch+="".join(f'<span class="c ct">{x}</span>' for x in tags[:3])
    return f'<div class="hero"><div class="hl"><span class="p"></span>TOP STORY</div><h3>{th}</h3><div class="mt">{s} · {ts} · {age} · {uc} · {sc:.0%}</div><div class="bd">{sm}</div>{wh}<div class="ch">{ch}</div></div>'

def _sec(label, cls, a):
    if not a: return f'<div class="sc2"><div class="sl {cls}">{label}</div><h4>No stories</h4><p>—</p></div>'
    return f'<div class="sc2"><div class="sl {cls}">{label}</div><h4>{a["title"]}</h4><p>{a.get("short_summary","")[:160]}</p></div>'

def _ac(a):
    t=a.get("title","");u=a.get("url","");th=f'<a href="{u}" target="_blank">{t}</a>' if u else t
    s=a.get("source","");ts=a.get("published_at","")[:16].replace("T"," ");age=_time_ago(a.get("published_at",""))
    sc=a.get("relevance_score",0);uc=_uchip(a.get("urgency","low"))
    sm=a.get("short_summary","");wim=a.get("why_it_matters","")
    wh=f'<div class="wm">Why it matters: {wim}</div>' if wim else ""
    cat=a.get("category","");tags=a.get("tags",[]);r=a.get("region","")
    ch=f'<span class="c cc">{cat}</span>' if cat else ""
    ch+=f'<span class="c ct">{r}</span>' if r and r!="Global" else ""
    ch+="".join(f'<span class="c ct">{x}</span>' for x in tags[:3])
    return f'<div class="ac"><div class="at"><h4>{th}</h4><span class="as">{sc:.0%}</span></div><div class="mt">{s} · {ts} · {age} · {uc}</div><div class="bd">{sm}</div>{wh}<div class="ch">{ch}</div></div>'

def _bf(title,body): return f'<div class="bf"><h4>{title}</h4><p>{body}</p></div>'

def _asc(v):
    d=v["direction"];dc={"up":"up","down":"dn","volatile":"vl"}.get(d,"nt")
    th=", ".join(v.get("driving_themes",[]))
    return f'<div class="asc"><div class="hd"><span class="em">{v["emoji"]}</span><span class="nm">{v["label"]}</span><span class="dr {dc}">{d.upper()}</span></div><div class="rw"><strong>Immediate:</strong> {v["immediate_reaction"]}</div><div class="rw"><strong>Short-term:</strong> {v["short_term_direction"]}</div><div class="rw"><strong>Risk trigger:</strong> {v["risk_reversal_trigger"]}</div><div class="rw"><strong>Drivers:</strong> {th}</div><div class="cf">Confidence: {v["confidence"]:.0%} · Signal: {v["signal_strength"]}</div></div>'

def _sn(label,text,cls): return f'<div class="sn"><div class="lb {cls}">{label}</div><p>{text}</p></div>'

def _pd(label,level,detail,score):
    lc={"HIGH":"cr","ELEVATED":"el","STRONG":"hi","MODERATE":"el","RISK-OFF LIKELY":"cr","VOLATILE":"el","RISK-ON BIAS":"hi","NEUTRAL":"lo","QUIET":"lo","LOW":"lo","NO DATA":"lo"}.get(level,"nf")
    return f'<div class="pd"><div class="pl">{label}</div><div class="pv {lc}">{level}</div><div class="pp">{detail}</div><div class="ps">Score: {score:.0%}</div></div>'

def _sh(t,s=""): return f'<div class="sh"><h2>{t}</h2>{"<div class=\"su\">"+s+"</div>" if s else ""}</div>'

def _parse_date(iso):
    if not iso: return None
    try: return datetime.fromisoformat(iso.replace("Z","+00:00")).date()
    except: return None

def _plotly_dark(fig):
    fig.update_layout(**_PLT)
    return fig

# ═══════════════════════ LOAD DATA ═══════════════════════════════════════
all_articles=get_articles(limit=500);total_articles=get_article_count()
total_runs=get_run_count();last_run=get_last_run();qa=get_qa_stats()
db_cats=get_distinct_categories();db_src=get_distinct_sources();db_reg=get_distinct_regions()
brow=get_latest_briefing();bdata=brow["data"] if brow else {}
fresh=get_freshness_info();outlook=generate_outlook(all_articles)

cc=Counter(a.get("category","") for a in all_articles)
_ai=cc.get("AI",0)+cc.get("AI Coding",0)+cc.get("AI Trading",0)
_geo=cc.get("Geopolitics",0)+cc.get("Military / Security",0)
_brk=sum(1 for a in all_articles if a.get("urgency")=="breaking")
age=fresh["hours_since_sweep"]

# ═══════════════════════ SIDEBAR ═════════════════════════════════════════
with st.sidebar:
    st.markdown('<div class="sb-hdr">Refresh</div>',unsafe_allow_html=True)
    r1,r2=st.columns([1,1])
    with r1:
        if st.button("Refresh Now",use_container_width=True,type="primary"): st.rerun()
    with r2: aro=st.toggle("Auto",value=False,key="_art")
    IO={"Manual":0,"1 min":60,"5 min":300,"15 min":900}
    if aro:
        il=st.selectbox("Interval",list(IO.keys())[1:],index=0,key="_ri");rs=IO[il]
    else: il="Manual";rs=0
    st.caption(f"Loaded: {datetime.now(timezone.utc).strftime('%H:%M:%S UTC')}")
    st.markdown('<div class="sb-hdr">Filters</div>',unsafe_allow_html=True)
    fc=st.multiselect("Category",db_cats,default=[],placeholder="All")
    fr=st.multiselect("Region",db_reg,default=[],placeholder="All")
    fs=st.multiselect("Source",db_src,default=[],placeholder="All")
    fu=st.multiselect("Urgency",["breaking","high","medium","low"],default=[],placeholder="All")
    frl=st.slider("Min relevance",0.0,1.0,0.0,0.05)
    dd=[_parse_date(a.get("published_at","")) for a in all_articles];vd=[d for d in dd if d]
    fdr=st.date_input("Date range",(min(vd),max(vd)),min_value=min(vd),max_value=max(vd)) if vd else None
    fk=st.text_input("Keyword",placeholder="Search...")
    st.markdown('<div class="sb-hdr">System</div>',unsafe_allow_html=True)
    ml="LLM" if settings.llm_enabled else "Rules";nl="NewsAPI+RSS" if settings.newsapi_enabled else "RSS"
    st.caption(f"Agent: **{ml}** · Src: **{nl}**")
    st.caption(f"Articles: **{total_articles}** · Runs: **{total_runs}**")

# auto-refresh
if rs>0:
    @st.fragment(run_every=timedelta(seconds=rs))
    def _arf():
        if "_at" not in st.session_state: st.session_state._at=time.time();return
        if time.time()-st.session_state._at>=rs*.8: st.session_state._at=time.time();st.rerun(scope="app")
    _arf()

# ═══════════════════════ HEADER ══════════════════════════════════════════
sts=last_run["created_at"][:16].replace("T"," ")+" UTC" if last_run else "—"
ags=f"{age:.1f}h ago" if age is not None else "never"
st.markdown(f'<div class="cmd"><div class="t">AI <span>Chief Agent</span></div><div class="m">Sweep: {sts} ({ags}) · {ml} · {nl}</div></div>',unsafe_allow_html=True)
if fresh["is_stale"]: st.warning(f"Data may be stale — last sweep {ags} ({fresh['last_sweep_article_count']} articles). Run `python main.py`.",icon="⚠️")

# signal strip
al="hi" if _ai>=5 else "el" if _ai>=2 else "lo";av="HIGH" if _ai>=5 else "MOD" if _ai>=2 else "LOW"
gl="cr" if _geo>=5 else "el" if _geo>=2 else "lo";gv="ELEVATED" if _geo>=2 else "CALM"
bl="cr" if _brk>=2 else "el" if _brk>=1 else "lo"
el=outlook["escalation_risk"]["level"][:4];ec="cr" if el in("HIGH","ELEV") else "el" if el=="MODE" else "lo"
ml2=outlook["market_reaction"]["level"][:8];mc2="cr" if "OFF" in ml2 else "el" if "VOL" in ml2 else "hi" if "ON" in ml2 else "lo"
st.markdown('<div class="sig">'+_pill("AI PULSE",av,al)+_pill("GEO RISK",gv,gl)+_pill("ESCALATION",outlook["escalation_risk"]["level"],ec)+_pill("MARKETS",outlook["market_reaction"]["level"],mc2)+_pill("BREAKING",str(_brk),bl)+_pill("SWEEP",ags,"cr" if fresh["is_stale"] else "nf")+_pill("ARTICLES",str(fresh["last_sweep_article_count"]),"nf")+'</div>',unsafe_allow_html=True)

# ═══════════════════════ TABS ════════════════════════════════════════════
t1,t2,t3=st.tabs(["INTELLIGENCE FEED","WORLD INTEL MAP","MACRO INTELLIGENCE"])

# filter
flt=all_articles
if fc: flt=[a for a in flt if a.get("category") in fc]
if fr: flt=[a for a in flt if a.get("region") in fr]
if fs: flt=[a for a in flt if a.get("source") in fs]
if fu: flt=[a for a in flt if a.get("urgency") in fu]
if frl>0: flt=[a for a in flt if (a.get("relevance_score") or 0)>=frl]
if fdr and isinstance(fdr,tuple) and len(fdr)==2:
    flt=[a for a in flt if (d:=_parse_date(a.get("published_at",""))) and fdr[0]<=d<=fdr[1]]
if fk: kw=fk.lower();flt=[a for a in flt if kw in (a.get("title","")+a.get("short_summary","")).lower()]
flt.sort(key=lambda a:a.get("relevance_score",0),reverse=True)

# ══════════════════════ TAB 1: FEED ══════════════════════════════════════
with t1:
    # KPIs
    k1,k2,k3,k4,k5=st.columns(5)
    with k1: st.markdown(_kpi("Articles",total_articles,"b"),unsafe_allow_html=True)
    with k2: st.markdown(_kpi("Runs",total_runs,"p"),unsafe_allow_html=True)
    with k3: st.markdown(_kpi("QA Pass",qa["passed"],"g"),unsafe_allow_html=True)
    with k4: st.markdown(_kpi("QA Fail",qa["failed"],"r"),unsafe_allow_html=True)
    with k5: st.markdown(_kpi("Showing",f'{len(flt)}/{total_articles}',"a"),unsafe_allow_html=True)

    # Predictive outlook
    st.markdown('<hr class="sd">',unsafe_allow_html=True)
    st.markdown(_sh("Next 6H / 24H Outlook","Predictive intelligence from current signals"),unsafe_allow_html=True)
    o=outlook
    p1,p2,p3,p4,p5=st.columns(5)
    with p1: st.markdown(_pd("Escalation Risk",o["escalation_risk"]["level"],o["escalation_risk"]["detail"],o["escalation_risk"]["score"]),unsafe_allow_html=True)
    with p2: st.markdown(_pd("Market Reaction",o["market_reaction"]["level"],o["market_reaction"]["detail"],o["market_reaction"]["score"]),unsafe_allow_html=True)
    with p3: st.markdown(_pd("AI Momentum",o["ai_momentum"]["level"],o["ai_momentum"]["detail"],o["ai_momentum"]["score"]),unsafe_allow_html=True)
    with p4: st.markdown(_pd("Supply Chain",o["supply_chain_risk"]["level"],o["supply_chain_risk"]["detail"],o["supply_chain_risk"]["score"]),unsafe_allow_html=True)
    with p5: st.markdown(_pd("Energy Sens.",o["energy_sensitivity"]["level"],o["energy_sensitivity"]["detail"],o["energy_sensitivity"]["score"]),unsafe_allow_html=True)

    # Watchlist
    wl=o.get("watchlist",[])
    if wl:
        with st.expander(f"Watchlist ({len(wl)} items) · Confidence: {o['overall_confidence']:.0%}"):
            for w in wl: st.markdown(f"- {w}")

    # Hero + actionable panels
    st.markdown('<hr class="sd">',unsafe_allow_html=True)
    st.markdown(_sh("Most Important Right Now","Priority intelligence"),unsafe_allow_html=True)
    if flt:
        st.markdown(_hero(flt[0]),unsafe_allow_html=True)
        brk=[a for a in flt if a.get("urgency")=="breaking"]
        ail=[a for a in flt if a.get("category") in ("AI","AI Coding","AI Trading")]
        mrl=[a for a in flt if a.get("market_impact")=="high"]
        gpl=[a for a in flt if a.get("category") in ("Geopolitics","Military / Security")]
        x1,x2,x3,x4=st.columns(4)
        with x1: st.markdown(_sec("BREAKING","lb",brk[0] if brk else None),unsafe_allow_html=True)
        with x2: st.markdown(_sec("AI OPPORTUNITY","la",ail[0] if ail else None),unsafe_allow_html=True)
        with x3: st.markdown(_sec("MARKET RISK","lr",mrl[0] if mrl else None),unsafe_allow_html=True)
        with x4: st.markdown(_sec("GEO CATALYST","lm",gpl[0] if gpl else None),unsafe_allow_html=True)
    else: st.info("No articles. Run `python main.py`.")

    # Category sections
    st.markdown('<hr class="sd">',unsafe_allow_html=True)
    def _rs(title,items,mx=4):
        if not items: return
        st.markdown(_sh(title,f"{len(items)} articles"),unsafe_allow_html=True)
        for a in items[:mx]: st.markdown(_ac(a),unsafe_allow_html=True)
        if len(items)>mx:
            with st.expander(f"Show {len(items)-mx} more"):
                for a in items[mx:]: st.markdown(_ac(a),unsafe_allow_html=True)

    for cat in ["Breaking News","AI","AI Coding","AI Trading","Geopolitics","Military / Security","Markets","Crypto","Energy","Shipping / Supply Chain","Natural Disasters","Global News"]:
        items=[a for a in flt if a.get("category")==cat] if cat!="Breaking News" else [a for a in flt if a.get("urgency")=="breaking"]
        _rs(cat,items)

    # Plotly charts
    st.markdown('<hr class="sd">',unsafe_allow_html=True)
    st.markdown(_sh("Analytics","Distribution & trends"),unsafe_allow_html=True)
    if flt:
        c1,c2=st.columns(2)
        with c1:
            cc2=Counter(a.get("category","?") for a in flt)
            df=pd.DataFrame(cc2.most_common(12),columns=["Category","Count"])
            fig=px.bar(df,x="Count",y="Category",orientation="h",title="Category Distribution")
            st.plotly_chart(_plotly_dark(fig),use_container_width=True)
        with c2:
            tc=Counter(t for a in flt for t in a.get("tags",[]))
            if tc:
                df2=pd.DataFrame(tc.most_common(12),columns=["Topic","Count"])
                fig2=px.bar(df2,x="Count",y="Topic",orientation="h",title="Topic Frequency")
                st.plotly_chart(_plotly_dark(fig2),use_container_width=True)
        c3,c4=st.columns(2)
        with c3:
            uc=Counter(a.get("urgency","low") for a in flt)
            df3=pd.DataFrame(list(uc.items()),columns=["Urgency","Count"])
            colors={"breaking":"#FF5252","high":"#FFB800","medium":"#00D4FF","low":"#1A3050"}
            fig3=px.pie(df3,values="Count",names="Urgency",title="Urgency Distribution",color="Urgency",color_discrete_map=colors,hole=.4)
            st.plotly_chart(_plotly_dark(fig3),use_container_width=True)
        with c4:
            rc=Counter(a.get("region","Global") for a in flt)
            df4=pd.DataFrame(rc.most_common(8),columns=["Region","Count"])
            fig4=px.bar(df4,x="Count",y="Region",orientation="h",title="Region Impact")
            st.plotly_chart(_plotly_dark(fig4),use_container_width=True)

# ══════════════════════ TAB 2: WORLD MAP ═════════════════════════════════
with t2:
    st.markdown(_sh("World Intelligence Map","Global event distribution"),unsafe_allow_html=True)
    if flt:
        map_data=[]
        for a in flt:
            lat,lon=infer_coordinates(a)
            urg=a.get("urgency","low")
            sz={"breaking":14,"high":10,"medium":7,"low":5}.get(urg,5)
            map_data.append({"lat":lat,"lon":lon,"title":a["title"][:80],"category":a.get("category",""),"urgency":urg,"region":a.get("region",""),"relevance":a.get("relevance_score",0),"size":sz,"source":a.get("source","")})
        mdf=pd.DataFrame(map_data)
        cat_colors={"AI":"#00D4FF","AI Coding":"#4ECDC4","AI Trading":"#45B7D1","Geopolitics":"#FFB800","Military / Security":"#FF5252","Markets":"#BB86FC","Crypto":"#96CEB4","Energy":"#FFEAA7","Shipping / Supply Chain":"#FF6B6B","Natural Disasters":"#E17055","Global News":"#636e72","Breaking News":"#FF5252","Sanctions":"#fd79a8","Infrastructure":"#a29bfe"}
        fig_map=px.scatter_geo(mdf,lat="lat",lon="lon",color="category",size="size",hover_name="title",hover_data={"urgency":True,"region":True,"relevance":":.0%","lat":False,"lon":False,"size":False},title="",color_discrete_map=cat_colors,size_max=16)
        fig_map.update_geos(bgcolor="rgba(0,0,0,0)",landcolor="#0A1525",oceancolor="#060A12",lakecolor="#060A12",coastlinecolor="#1A3050",countrycolor="#0F1A2E",showframe=False,projection_type="natural earth")
        fig_map.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font=dict(color="#6B9CC0",size=10),margin=dict(l=0,r=0,t=10,b=0),height=500,legend=dict(bgcolor="rgba(0,0,0,0)",font=dict(size=9)))
        st.plotly_chart(fig_map,use_container_width=True)

        # Region breakdown
        st.markdown('<hr class="sd">',unsafe_allow_html=True)
        st.markdown(_sh("Regional Breakdown","Event concentration by region"),unsafe_allow_html=True)
        rc2=Counter(a.get("region","Global") for a in flt)
        rcols=st.columns(min(len(rc2),7))
        for i,(reg,cnt) in enumerate(rc2.most_common(7)):
            with rcols[i]: st.markdown(_kpi(reg,cnt,"b"),unsafe_allow_html=True)
    else: st.info("No articles to map.")

# ══════════════════════ TAB 3: MACRO INTEL ═══════════════════════════════
with t3:
    if not bdata:
        st.info("No macro briefing. Run `python main.py`.")
    else:
        b=bdata
        m1,m2,m3,m4,m5=st.columns(5)
        with m1: st.markdown(_kpi("Theme",b.get("top_theme","—"),"a"),unsafe_allow_html=True)
        with m2:
            rl=b.get("overall_risk_level","low");rc="r" if rl=="high" else "a" if rl=="medium" else "g"
            st.markdown(_kpi("Risk",rl.upper(),rc),unsafe_allow_html=True)
        with m3: st.markdown(_kpi("Confidence",f'{b.get("overall_confidence",0):.0%}',"b"),unsafe_allow_html=True)
        with m4: st.markdown(_kpi("Assets",len(b.get("asset_views",[])),"p"),unsafe_allow_html=True)
        with m5: st.markdown(_kpi("Rules",b.get("rule_triggers",0),"b"),unsafe_allow_html=True)
        st.markdown('<hr class="sd">',unsafe_allow_html=True)

        st.markdown(_sh("Executive Summary","Macro intelligence briefing"),unsafe_allow_html=True)
        e1,e2=st.columns(2)
        with e1:
            st.markdown(_bf("What Happened","<br>".join(f"&bull; {h}" for h in b.get("what_happened",[]))),unsafe_allow_html=True)
            st.markdown(_bf("Market Reaction",b.get("market_reaction","")),unsafe_allow_html=True)
            st.markdown(_bf("My Market Read",b.get("market_read","")),unsafe_allow_html=True)
        with e2:
            st.markdown(_bf("Probable Direction",b.get("probable_direction","")),unsafe_allow_html=True)
            st.markdown(_bf("Why It Matters",b.get("why_it_matters","")),unsafe_allow_html=True)
            wt=b.get("what_to_watch",[])
            st.markdown(_bf("What To Watch","<br>".join(f"&bull; {w}" for w in wt) if wt else "—"),unsafe_allow_html=True)
        st.markdown(_bf("Conclusion",b.get("conclusion","")),unsafe_allow_html=True)
        st.markdown('<hr class="sd">',unsafe_allow_html=True)

        st.markdown(_sh("Scenario Analysis","Probabilistic outcomes"),unsafe_allow_html=True)
        sc=b.get("scenarios",{})
        s1,s2,s3=st.columns(3)
        with s1: st.markdown(_sn("Bull Case",sc.get("bull_case","—"),"bu"),unsafe_allow_html=True)
        with s2: st.markdown(_sn("Base Case",sc.get("base_case","—"),"ba"),unsafe_allow_html=True)
        with s3: st.markdown(_sn("Risk Case",sc.get("risk_case","—"),"ri"),unsafe_allow_html=True)
        st.markdown('<hr class="sd">',unsafe_allow_html=True)

        av=b.get("asset_views",[])
        st.markdown(_sh("Asset Breakdown",f"{len(av)} assets"),unsafe_allow_html=True)
        ac1,ac2,ac3=st.columns(3)
        with ac1: fad=st.multiselect("Direction",["up","down","volatile","neutral"],default=[],placeholder="All",key="md")
        with ac2:
            als=sorted(set(v.get("label","") for v in av))
            fac=st.multiselect("Asset",als,default=[],placeholder="All",key="ma")
        with ac3: fmc=st.slider("Min confidence",0.0,1.0,0.0,0.05,key="mc")
        fv=av
        if fad: fv=[v for v in fv if v.get("direction") in fad]
        if fac: fv=[v for v in fv if v.get("label") in fac]
        if fmc>0: fv=[v for v in fv if v.get("confidence",0)>=fmc]
        if fv:
            lc,rc=st.columns(2)
            for i,v in enumerate(fv):
                with lc if i%2==0 else rc: st.markdown(_asc(v),unsafe_allow_html=True)
        else: st.info("No assets match.")
        st.markdown('<hr class="sd">',unsafe_allow_html=True)

        at=b.get("all_themes",[])
        if at:
            st.markdown(_sh("Active Themes","Detected narratives"),unsafe_allow_html=True)
            df_t=pd.DataFrame(at)
            if not df_t.empty:
                fig_t=px.bar(df_t,x="count",y="theme",orientation="h",title="Theme Distribution")
                st.plotly_chart(_plotly_dark(fig_t),use_container_width=True)

# ═══════════════════════ FOOTER ══════════════════════════════════════════
st.markdown('<hr class="sd">',unsafe_allow_html=True)
now_utc=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
rfs=f"Auto: {il}" if rs>0 else "Manual"
st.markdown(f'<div class="ftr">{len(all_articles)} articles · {now_utc} UTC · Refresh: {rfs} · {ml} mode</div>',unsafe_allow_html=True)

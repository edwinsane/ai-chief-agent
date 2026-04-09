"""
AI Chief Agent — Executive Dashboard.

Dark-themed monitoring UI with filters, metric cards, insights charts,
and a table + detail panel for browsing agent run history.

Run locally:   streamlit run app/dashboard/app.py
Run on VPS:    ./run_dashboard.sh
"""

import json
import sys
from collections import Counter
from datetime import datetime, date, timezone
from pathlib import Path

import pandas as pd
import streamlit as st

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.core.config import settings  # noqa: E402
from app.storage.database import (  # noqa: E402
    get_all_runs,
    get_distinct_topics,
    get_last_run,
    get_qa_stats,
    get_run_count,
    init_db,
)

# ---------------------------------------------------------------------------
# Page config & DB init
# ---------------------------------------------------------------------------
st.set_page_config(page_title="AI Chief Agent", page_icon="🤖", layout="wide")
init_db()

# ---------------------------------------------------------------------------
# Custom CSS — dark executive styling
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    /* --- auto-refresh ---------------------------------------------------- */
    meta[http-equiv="refresh"] { display: none; }

    /* --- global ---------------------------------------------------------- */
    .block-container { padding-top: 1.5rem; }
    h1, h2, h3 { letter-spacing: -0.02em; }

    /* --- metric cards ---------------------------------------------------- */
    .metric-card {
        background: #1A1F2B;
        border: 1px solid #2A2F3B;
        border-radius: 10px;
        padding: 1.1rem 1.3rem;
        text-align: center;
    }
    .metric-card .label {
        font-size: 0.78rem;
        color: #8B95A5;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 0.25rem;
    }
    .metric-card .value {
        font-size: 1.6rem;
        font-weight: 700;
        color: #E2E8F0;
    }
    .metric-card .value.green  { color: #48BB78; }
    .metric-card .value.red    { color: #FC8181; }
    .metric-card .value.blue   { color: #63B3ED; }
    .metric-card .value.amber  { color: #F6AD55; }

    /* --- QA badges ------------------------------------------------------- */
    .qa-pass {
        display: inline-block;
        background: #22543D;
        color: #48BB78;
        padding: 0.15rem 0.6rem;
        border-radius: 4px;
        font-size: 0.82rem;
        font-weight: 600;
    }
    .qa-fail {
        display: inline-block;
        background: #742A2A;
        color: #FC8181;
        padding: 0.15rem 0.6rem;
        border-radius: 4px;
        font-size: 0.82rem;
        font-weight: 600;
    }

    /* --- detail panel ---------------------------------------------------- */
    .detail-section {
        background: #1A1F2B;
        border: 1px solid #2A2F3B;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
    }
    .detail-section h4 {
        margin: 0 0 0.4rem 0;
        font-size: 0.85rem;
        color: #8B95A5;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .detail-section p {
        margin: 0;
        color: #C8CDD3;
        line-height: 1.55;
    }

    /* --- divider --------------------------------------------------------- */
    .section-divider {
        border: none;
        border-top: 1px solid #2A2F3B;
        margin: 1.8rem 0;
    }

    /* --- sidebar refinements --------------------------------------------- */
    [data-testid="stSidebar"] {
        background: #0E1117;
        border-right: 1px solid #1E2330;
    }
    </style>

    <!-- auto-refresh every 30 s -->
    <meta http-equiv="refresh" content="30">
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _metric_card(label: str, value: str | int, color: str = "") -> str:
    """Return HTML for a single metric card."""
    cls = f" {color}" if color else ""
    return (
        f'<div class="metric-card">'
        f'<div class="label">{label}</div>'
        f'<div class="value{cls}">{value}</div>'
        f"</div>"
    )


def _parse_result(raw: str | None) -> dict:
    """Safely parse the JSON result column."""
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return {}


def _format_ts(iso: str) -> str:
    """'2026-04-08T19:22:22...' -> '2026-04-08  19:22 UTC'"""
    return iso[:16].replace("T", "  ") + " UTC"


def _parse_date(iso: str) -> date:
    """Extract date from ISO timestamp."""
    return datetime.fromisoformat(iso).date()


# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
all_runs = get_all_runs()
total_runs = get_run_count()
last_run = get_last_run()
qa_stats = get_qa_stats()
topics = get_distinct_topics()

# Build a list of dicts with parsed fields for easy filtering
run_records: list[dict] = []
for r in all_runs:
    parsed = _parse_result(r["result"])
    run_records.append(
        {
            "id": r["id"],
            "topic": r["topic"],
            "created_at": r["created_at"],
            "date": _parse_date(r["created_at"]),
            "qa_passed": parsed.get("qa_passed", False),
            "research": parsed.get("research_results", ""),
            "trends": parsed.get("trend_results", ""),
            "qa_notes": parsed.get("qa_notes", ""),
            "raw": parsed,
        }
    )

# ---------------------------------------------------------------------------
# HEADER
# ---------------------------------------------------------------------------
st.markdown("## AI Chief Agent")
st.caption("Executive monitoring dashboard")

# ---------------------------------------------------------------------------
# 1. METRIC CARDS
# ---------------------------------------------------------------------------
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

cols = st.columns(5)

with cols[0]:
    st.markdown(_metric_card("Total Runs", total_runs, "blue"), unsafe_allow_html=True)
with cols[1]:
    ts = _format_ts(last_run["created_at"]) if last_run else "—"
    st.markdown(_metric_card("Latest Run", ts), unsafe_allow_html=True)
with cols[2]:
    topic_val = last_run["topic"] if last_run else "—"
    st.markdown(_metric_card("Latest Topic", topic_val, "amber"), unsafe_allow_html=True)
with cols[3]:
    st.markdown(_metric_card("QA Passed", qa_stats["passed"], "green"), unsafe_allow_html=True)
with cols[4]:
    st.markdown(_metric_card("QA Failed", qa_stats["failed"], "red"), unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# 2. SIDEBAR FILTERS
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### Filters")

    # Topic filter
    selected_topics = st.multiselect(
        "Topic",
        options=topics,
        default=[],
        placeholder="All topics",
    )

    # Date range filter
    if run_records:
        all_dates = [r["date"] for r in run_records]
        min_date, max_date = min(all_dates), max(all_dates)
    else:
        min_date = max_date = date.today()

    date_range = st.date_input(
        "Date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    # QA status filter
    qa_filter = st.radio(
        "QA Status",
        options=["All", "Passed", "Failed"],
        horizontal=True,
    )

    # Keyword search
    keyword = st.text_input("Keyword search", placeholder="Search inside results...")

    st.markdown("---")
    mode = "LLM" if settings.llm_enabled else "Stub"
    st.caption(f"Agent mode: **{mode}**")

# ---------------------------------------------------------------------------
# Apply filters
# ---------------------------------------------------------------------------
filtered = run_records

if selected_topics:
    filtered = [r for r in filtered if r["topic"] in selected_topics]

if isinstance(date_range, tuple) and len(date_range) == 2:
    d_start, d_end = date_range
    filtered = [r for r in filtered if d_start <= r["date"] <= d_end]

if qa_filter == "Passed":
    filtered = [r for r in filtered if r["qa_passed"]]
elif qa_filter == "Failed":
    filtered = [r for r in filtered if not r["qa_passed"]]

if keyword:
    kw = keyword.lower()
    filtered = [
        r
        for r in filtered
        if kw in r["research"].lower()
        or kw in r["trends"].lower()
        or kw in r["qa_notes"].lower()
        or kw in r["topic"].lower()
    ]

# ---------------------------------------------------------------------------
# 3. RESULTS — table + detail panel
# ---------------------------------------------------------------------------
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
st.markdown("### Run Results")
st.caption(f"{len(filtered)} of {total_runs} runs shown")

if filtered:
    # Build a display dataframe
    table_data = []
    for r in filtered:
        qa_label = "Passed" if r["qa_passed"] else "Failed"
        table_data.append(
            {
                "ID": r["id"],
                "Topic": r["topic"],
                "Date": _format_ts(r["created_at"]),
                "QA": qa_label,
            }
        )

    df = pd.DataFrame(table_data)

    col_table, col_detail = st.columns([2, 3])

    with col_table:
        selection = st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row",
        )

        # Determine selected row
        selected_idx = None
        if selection and selection.selection and selection.selection.rows:
            selected_idx = selection.selection.rows[0]

    with col_detail:
        if selected_idx is not None and selected_idx < len(filtered):
            rec = filtered[selected_idx]

            # Topic headline
            st.markdown(f"#### {rec['topic']}")
            ts_display = _format_ts(rec["created_at"])
            qa_badge = (
                '<span class="qa-pass">QA PASSED</span>'
                if rec["qa_passed"]
                else '<span class="qa-fail">QA FAILED</span>'
            )
            st.markdown(
                f"Run #{rec['id']}  &middot;  {ts_display}  &middot;  {qa_badge}",
                unsafe_allow_html=True,
            )

            st.markdown("")

            # Research summary
            st.markdown(
                f'<div class="detail-section">'
                f"<h4>Research Summary</h4>"
                f"<p>{rec['research']}</p>"
                f"</div>",
                unsafe_allow_html=True,
            )

            # Trend analysis
            st.markdown(
                f'<div class="detail-section">'
                f"<h4>Trend Analysis</h4>"
                f"<p>{rec['trends']}</p>"
                f"</div>",
                unsafe_allow_html=True,
            )

            # QA notes
            st.markdown(
                f'<div class="detail-section">'
                f"<h4>QA Notes</h4>"
                f"<p>{rec['qa_notes']}</p>"
                f"</div>",
                unsafe_allow_html=True,
            )
        else:
            st.info("Select a row from the table to view run details.")
else:
    st.info("No runs match the current filters.")

# ---------------------------------------------------------------------------
# 4. INSIGHTS
# ---------------------------------------------------------------------------
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
st.markdown("### Insights")

if run_records:
    col_chart1, col_chart2 = st.columns(2)

    # --- Runs per day (bar chart) ---
    with col_chart1:
        st.markdown("##### Runs per Day")
        date_counts = Counter(r["date"].isoformat() for r in run_records)
        df_dates = pd.DataFrame(
            sorted(date_counts.items()), columns=["Date", "Runs"]
        )
        df_dates["Date"] = pd.to_datetime(df_dates["Date"])
        st.bar_chart(df_dates, x="Date", y="Runs", color="#4A90D9")

    # --- Top topics (horizontal bar) ---
    with col_chart2:
        st.markdown("##### Top Topics")
        topic_counts = Counter(r["topic"] for r in run_records)
        top = topic_counts.most_common(10)
        df_topics = pd.DataFrame(top, columns=["Topic", "Runs"])
        st.bar_chart(df_topics, x="Topic", y="Runs", color="#F6AD55", horizontal=True)

    # --- Quick stats row ---
    st.markdown("")
    s1, s2, s3 = st.columns(3)
    with s1:
        st.markdown(
            _metric_card("Unique Topics", len(topics), "blue"),
            unsafe_allow_html=True,
        )
    with s2:
        recent = [r["topic"] for r in run_records[:5]]
        st.markdown(
            _metric_card("Most Recent Topic", recent[0] if recent else "—", "amber"),
            unsafe_allow_html=True,
        )
    with s3:
        if topic_counts:
            top_topic, top_count = topic_counts.most_common(1)[0]
            st.markdown(
                _metric_card("Most Analyzed", f"{top_topic} ({top_count}x)", "green"),
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                _metric_card("Most Analyzed", "—"),
                unsafe_allow_html=True,
            )
else:
    st.info("Run the pipeline at least once to see insights.")

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
st.caption(f"Dashboard refreshed at {now_utc} UTC  ·  Auto-refresh: 30 s  ·  Agent mode: {'LLM' if settings.llm_enabled else 'Stub'}")

import pandas as pd
import streamlit as st
import altair as alt

from src.ui import (
    html_title,
    html_subtitle,
    html_section,
    html_explain,
    html_badge,
    metric_tile,
)
from src.data_loader import load_kpi_csv


st.set_page_config(page_title="Bowling Analysis | IPL Strategy Dashboard", layout="wide")


# ============================================================
# GLOBAL UI STYLING (keep same feel as Tab 4)
# ============================================================

st.markdown(
    """
    <style>
    div[data-testid="stDataFrame"] * {
        font-size: 14px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def apply_altair_theme(chart: alt.Chart) -> alt.Chart:
    """
    Global Altair styling (same approach as Tab 4).
    """
    return (
        chart.configure_axis(
            labelFontSize=14,
            labelColor="#2f3e46",
            titleFontSize=14,
            titleColor="#2f3e46",
        )
        .configure_legend(
            labelFontSize=13,
            labelColor="#2f3e46",
            titleFontSize=13,
            titleColor="#2f3e46",
        )
    )


# ============================================================
# TAB 5: Bowling Analysis (FAST - KPI file)
# ============================================================

html_title("Bowling Analysis")
html_subtitle(
    "Analyze wicket-taking impact, economy control, and reliability using precomputed season + region bowling KPIs."
)
st.markdown("")


# -----------------------------
# Load KPI file (DO NOT change loader utility)
# -----------------------------
KPI_GROUP = "sub_kpis"
KPI_DOMAIN = "bowling"
KPI_FILE = "bowling_master_final_1801.csv"


try:
    bowl = load_kpi_csv(KPI_GROUP, KPI_DOMAIN, KPI_FILE)
except FileNotFoundError:
    html_section("Bowling KPI File Not Found")
    html_explain("This tab depends on a precomputed KPI CSV which is not available in the expected folder yet.")

    st.error(f"Missing file: data/KPIs/{KPI_GROUP}/{KPI_DOMAIN}/{KPI_FILE}")

    st.info(
        "Next action: generate this KPI file (tab5_bowling_master.csv) using your KPI build notebook, "
        "then rerun this tab."
    )
    st.stop()



# -----------------------------
# Filters (simple only)
# -----------------------------
html_section("Filters")
html_explain("Adjust scope and stability controls to keep bowling insights fair and comparable.")

c1, c2, c3, c4 = st.columns([1.2, 1.2, 1.2, 1.2])

with c1:
    region_choice = st.selectbox(
        "Venue Region",
        ["All Venues", "India", "Overseas"],
        index=0,
        key="tab5_region",
    )

with c2:
    # Season list depends on region scope (same pattern as Tab 4)
    if region_choice == "All Venues":
        season_list = sorted(
            bowl["season"].unique().tolist(), key=lambda x: (x != "All Time", x)
        )
    else:
        season_list = sorted(
            bowl[bowl["venue_region"] == region_choice]["season"].unique().tolist(),
            key=lambda x: (x != "All Time", x),
        )

    season_choice = st.selectbox(
        "Season",
        season_list,
        index=0,
        key="tab5_season",
    )

with c3:
    min_balls = st.selectbox(
        "Min balls bowled",
        [0, 30, 60, 120, 250],
        index=2,
        key="tab5_min_balls",
    )

with c4:
    top_n = st.selectbox(
        "Top Bowlers",
        [5, 10, 15],
        index=0,
        key="tab5_topn",
    )


# -----------------------------
# Apply filters (Step 1 = scope + stability only)
# -----------------------------
bowl_scope = bowl.copy()

if region_choice != "All Venues":
    bowl_scope = bowl_scope[bowl_scope["venue_region"] == region_choice].copy()

bowl_scope = bowl_scope[bowl_scope["season"] == season_choice].copy()

# Stability control placeholder (we confirm the right column in Step 2)
if "balls" in bowl_scope.columns:
    bowl_scope = bowl_scope[bowl_scope["balls"] >= int(min_balls)].copy()

html_badge(
    f"Showing: <b>{region_choice}</b> • <b>{season_choice}</b> • Min balls: <b>{min_balls}</b>"
)

if len(bowl_scope) == 0:
    st.warning("No bowlers match the selected filters. Try lowering the minimum balls filter.")
    st.stop()


# -----------------------------
# Summary tiles (sanity check only)
# -----------------------------
html_section("Bowling Summary (Sanity Check)")
html_explain("This confirms KPI loading + filters work before we build charts and leaderboards.")

a, b, c, d = st.columns(4)

with a:
    metric_tile(f"{bowl_scope['bowler'].nunique():,}", "Bowlers in scope after filters.")

with b:
    metric_tile(f"{len(bowl_scope):,}", "Rows (KPI records) in scope.")

with c:
    if "balls" in bowl_scope.columns:
        metric_tile(f"{int(bowl_scope['balls'].sum()):,}", "Total balls in scope.")
    else:
        metric_tile("—", "Total balls in scope.")

with d:
    metric_tile(f"{top_n}", "Top N control (used in charts next steps).")

st.divider()


# -----------------------------
# Data preview (sanity)
# -----------------------------
html_section("Data Preview")
html_explain("Quick preview of the bowling KPI dataset structure for Tab 5 (first 25 rows).")

st.dataframe(bowl_scope.head(25), use_container_width=True)

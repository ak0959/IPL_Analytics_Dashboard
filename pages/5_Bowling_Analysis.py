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
# Theme selector (keep same feel as Tab 4)
# -----------------------------
theme_choice = st.selectbox(
    "Theme",
    ["Light", "Classic (Bold)", "Greyscale"],
    index=0,
    key="tab5_theme",
)

THEMES = {
    "Light": {
        "blue": "#4f93c7",
        "green": "#5bb85b",
        "orange": "#ff9a45",
        "red": "#e05a5b",
        "purple": "#ad8ad0",
        "teal": "#55b3a8",
        "slate": "#87919a",
    },
    "Classic (Bold)": {
        "blue": "#1f77b4",
        "green": "#2ca02c",
        "orange": "#ff7f0e",
        "red": "#d62728",
        "purple": "#9467bd",
        "teal": "#2a9d8f",
        "slate": "#6c757d",
    },
    "Greyscale": {
        "blue": "#6c757d",
        "green": "#adb5bd",
        "orange": "#87919a",
        "red": "#57666d",
        "purple": "#a3adb6",
        "teal": "#c1c7cd",
        "slate": "#2f3e46",
    },
}

TAB5_COLORS = THEMES[theme_choice]


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
        "Next action: generate the bowling KPI master file, commit it to GitHub, "
        "then rerun this tab."
    )
    st.stop()

# Basic cleanup
bowl["venue_region"] = bowl["venue_region"].astype(str).str.strip()
bowl["season"] = bowl["season"].astype(str).str.strip()
bowl["bowler"] = bowl["bowler"].astype(str).str.strip()


# -----------------------------
# Coverage disclaimer (important)
# -----------------------------
st.caption(
    "Note: All metrics are computed only from matches available in this dataset. "
    "‘All Time’ refers to all seasons present in the source data, and may not match official IPL records."
)

# Show dataset season range (excluding All Time)
season_numeric = pd.to_numeric(bowl[bowl["season"] != "All Time"]["season"], errors="coerce")
if season_numeric.notna().any():
    st.caption(
        f"Dataset coverage: seasons {int(season_numeric.min())} → {int(season_numeric.max())} (plus All Time rollups)."
    )

st.markdown("")


# ============================================================
# Filters (simple only)
# ============================================================
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
# Apply filters
# -----------------------------
bowl_scope = bowl.copy()

if region_choice != "All Venues":
    bowl_scope = bowl_scope[bowl_scope["venue_region"] == region_choice].copy()

bowl_scope = bowl_scope[bowl_scope["season"] == season_choice].copy()
bowl_scope = bowl_scope[bowl_scope["balls"] >= int(min_balls)].copy()

html_badge(
    f"Showing: <b>{region_choice}</b> • <b>{season_choice}</b> • Min balls: <b>{min_balls}</b>"
)

if len(bowl_scope) == 0:
    st.warning("No bowlers match the selected filters. Try lowering the minimum balls filter.")
    st.stop()


# -----------------------------
# Summary tiles (sanity check)
# -----------------------------
html_section("Bowling Summary")
html_explain("Quick summary of bowlers and volume in the selected scope.")

a, b, c, d = st.columns(4)

with a:
    metric_tile(
        f"{bowl_scope['bowler'].nunique():,}",
        "Bowlers in scope after filters.",
        value_color=TAB5_COLORS["blue"],
    )

with b:
    metric_tile(
        f"{int(bowl_scope['wickets'].sum()):,}",
        "Total wickets taken by this bowler group.",
        value_color=TAB5_COLORS["purple"],
    )

with c:
    metric_tile(
        f"{float(bowl_scope['economy'].mean()):.2f}",
        "Average economy across bowlers in scope.",
        value_color=TAB5_COLORS["green"],
    )

with d:
    metric_tile(
        f"{min_balls}",
        "Minimum balls filter (stability control).",
        value_color=TAB5_COLORS["orange"],
    )

st.divider()


# ============================================================
# SECTION 1: Impact Leaders (Wickets)
# ============================================================

html_section("Impact Leaders (Wickets)")
html_explain("Who are the highest wicket-taking bowlers in the selected scope (after stability filters)?")

impact = (
    bowl_scope.sort_values("wickets", ascending=False)
    .head(int(top_n))
    .copy()
)

order_list = impact["bowler"].tolist()

# Dynamic chart height (same logic as Batting)
BASE_H = 180
ROW_H = 36
chart_h = int(BASE_H + (ROW_H * int(top_n)))

# Base bar
base_wkts = (
    alt.Chart(impact)
    .mark_bar()
    .encode(
        y=alt.Y("bowler:N", sort=order_list, title=""),
        x=alt.X("wickets:Q", title="Wickets"),
        color=alt.value(TAB5_COLORS["purple"]),
        tooltip=[
            alt.Tooltip("bowler:N", title="Bowler"),
            alt.Tooltip("wickets:Q", title="Wickets", format=",.0f"),
            alt.Tooltip("innings_bowled:Q", title="Innings", format=",.0f"),
            alt.Tooltip("balls:Q", title="Balls", format=",.0f"),
            alt.Tooltip("overs:Q", title="Overs", format=",.1f"),
            alt.Tooltip("economy:Q", title="Economy", format=".2f"),
            alt.Tooltip("bowling_strike_rate:Q", title="Strike Rate", format=".2f"),
            alt.Tooltip("dot_ball_pct:Q", title="Dot Ball %", format=".1f"),
            alt.Tooltip("boundary_ball_pct:Q", title="Boundary Ball %", format=".1f"),
            alt.Tooltip("pct_innings_3plus:Q", title="3+ Wkts Innings %", format=".1f"),
        ],
    )
    .properties(height=chart_h)
)

# Wicket labels INSIDE bar (big font)
wkt_labels = (
    alt.Chart(impact)
    .transform_calculate(x_pos="datum.wickets * 0.80")
    .mark_text(color="#1b1b1b", fontSize=18)
    .encode(
        y=alt.Y("bowler:N", sort=order_list, title=""),
        x=alt.X("x_pos:Q"),
        text=alt.Text("wickets:Q", format=",.0f"),
    )
)

impact_chart = apply_altair_theme(base_wkts + wkt_labels)
st.altair_chart(impact_chart, use_container_width=True)

with st.expander("📋 View Top Bowlers Table", expanded=False):
    table_cols = [
        "bowler",
        "wickets",
        "innings_bowled",
        "balls",
        "overs",
        "economy",
        "bowling_strike_rate",
        "dot_ball_pct",
        "boundary_ball_pct",
        "pct_innings_3plus",
    ]

    leaderboard = impact[table_cols].copy()

    leaderboard = leaderboard.rename(
        columns={
            "bowler": "Bowler",
            "wickets": "Wickets",
            "innings_bowled": "Innings",
            "balls": "Balls",
            "overs": "Overs",
            "economy": "Economy",
            "bowling_strike_rate": "Strike Rate",
            "dot_ball_pct": "Dot Ball %",
            "boundary_ball_pct": "Boundary Ball %",
            "pct_innings_3plus": "3+ Wkts Innings %",
        }
    )

    leaderboard["Overs"] = leaderboard["Overs"].round(1)
    leaderboard["Economy"] = leaderboard["Economy"].round(2)
    leaderboard["Strike Rate"] = leaderboard["Strike Rate"].round(2)
    leaderboard["Dot Ball %"] = leaderboard["Dot Ball %"].round(1)
    leaderboard["Boundary Ball %"] = leaderboard["Boundary Ball %"].round(1)
    leaderboard["3+ Wkts Innings %"] = leaderboard["3+ Wkts Innings %"].round(1)

    st.dataframe(leaderboard, use_container_width=True, hide_index=True)

st.divider()


# ============================================================
# Data Preview (temporary)
# ============================================================

html_section("Data Preview")
html_explain("Quick preview of the bowling KPI dataset structure for Tab 5 (first 25 rows).")

st.dataframe(bowl_scope.head(25), use_container_width=True)

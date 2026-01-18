import pandas as pd
import streamlit as st
import altair as alt

from src.ui import (
    html_section,
    html_explain,
    html_badge,
    info_box,
    metric_tile,
    PRIMARY_PALETTE,
)

from src.data_loader import load_master_balls


st.set_page_config(page_title="All Seasons – Quick Insights | IPL Strategy Dashboard", layout="wide")


# ============================================================
# Helpers
# ============================================================
def format_indian(n):
    try:
        n = int(float(n))
    except Exception:
        return str(n)

    s = str(abs(n))
    if len(s) <= 3:
        out = s
    else:
        out = s[-3:]
        s = s[:-3]
        while len(s) > 2:
            out = s[-2:] + "," + out
            s = s[:-2]
        if len(s) > 0:
            out = s + "," + out

    return "-" + out if n < 0 else out


def safe_str_series(s: pd.Series) -> pd.Series:
    return s.astype(str).fillna("").str.strip()


def apply_altair_theme(chart: alt.Chart) -> alt.Chart:
    return (
        chart.configure_axis(
            labelFontSize=13,
            titleFontSize=13,
            labelColor="#2f3e46",
            titleColor="#2f3e46",
        )
        .configure_legend(
            labelFontSize=12,
            titleFontSize=12,
            labelColor="#2f3e46",
            titleColor="#2f3e46",
        )
    )


def phase_from_over(over_number: int) -> str:
    """
    IPL standard phase mapping (0-indexed overs):
    - Powerplay: overs 0–5
    - Middle: overs 6–14
    - Death: overs 15–19
    """
    if over_number <= 5:
        return "Powerplay"
    if over_number <= 14:
        return "Middle"
    return "Death"


# ============================================================
# Page Header (modern + colorful)
# ============================================================
st.markdown(
    """
    <div style="
        background: linear-gradient(90deg, #3b82f6 0%, #9333ea 55%, #f97316 100%);
        padding: 18px 18px;
        border-radius: 18px;
        color: white;
        margin-bottom: 14px;
        box-shadow: 0px 8px 18px rgba(0,0,0,0.10);
    ">
        <div style="font-size: 2.05rem; font-weight: 900; line-height: 1.15;">
            🏏 All Seasons – Quick Insights
        </div>
        <div style="font-size: 1.05rem; opacity: 0.95; margin-top: 6px;">
            A fast snapshot of the IPL scoring environment across seasons and regions.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# Load balls master
# ============================================================
balls = load_master_balls().copy()

required_cols = [
    "match_id",
    "season_id",
    "venue_region",
    "over_number",
    "total_runs",
    "batter_runs",
    "extras",
    "is_wicket",
    "is_super_over",
]
missing = [c for c in required_cols if c not in balls.columns]
if missing:
    st.error(f"master2_balls_baseline is missing required columns: {missing}")
    st.stop()

# Normalize
balls["venue_region"] = safe_str_series(balls["venue_region"])
balls["season_id"] = pd.to_numeric(balls["season_id"], errors="coerce").astype("Int64")
balls["over_number"] = pd.to_numeric(balls["over_number"], errors="coerce")
balls["total_runs"] = pd.to_numeric(balls["total_runs"], errors="coerce").fillna(0)
balls["batter_runs"] = pd.to_numeric(balls["batter_runs"], errors="coerce").fillna(0)
balls["extras"] = pd.to_numeric(balls["extras"], errors="coerce").fillna(0)
balls["is_wicket"] = pd.to_numeric(balls["is_wicket"], errors="coerce").fillna(0)

# Exclude super overs
balls = balls[balls["is_super_over"] == False].copy()


# ============================================================
# Filters
# ============================================================
html_section("🎛️ Filters")
html_explain("Use Venue Region + Season to adjust the scope.")

region_map = {
    "All Venues": None,
    "India": "India",
    "Overseas": "Overseas",
}

top1, top2, top3 = st.columns([1.25, 1.25, 2.5])

with top1:
    selected_region_label = st.selectbox(
        "Venue Region",
        options=list(region_map.keys()),
        index=0,
        key="tab1_region",
    )

scope_df = balls.copy()

if selected_region_label != "All Venues":
    scope_df = scope_df[scope_df["venue_region"] == region_map[selected_region_label]].copy()

season_list = sorted([int(x) for x in scope_df["season_id"].dropna().unique().tolist()])
season_options = ["All Time"] + season_list

with top2:
    selected_season = st.selectbox(
        "Season",
        options=season_options,
        index=0,
        key="tab1_season",
    )

with top3:
    st.markdown(
        "<div style='font-size: 1.02rem; color:#666; padding-top: 28px; line-height:1.45;'>"
        "This page summarizes the IPL environment using the selected scope."
        "</div>",
        unsafe_allow_html=True,
    )

if selected_season != "All Time":
    scope_df = scope_df[scope_df["season_id"] == int(selected_season)].copy()
    scope_label = f"{selected_region_label} • {selected_season}"
else:
    scope_label = f"{selected_region_label} • All Time"

html_badge(f"Showing: <b>{scope_label}</b>")


# ============================================================
# Quick Summary Tiles (volume + environment)
# ============================================================
html_section("📌 Quick Summary")
html_explain("A quick sense-check of match volume, scoring speed, and intensity.")

total_matches = int(scope_df["match_id"].nunique())
total_balls = int(len(scope_df))
total_runs = int(scope_df["total_runs"].sum())

run_rate = (total_runs / total_balls * 6) if total_balls > 0 else 0.0

boundaries = int(scope_df["batter_runs"].isin([4, 6]).sum())
boundary_pct = (boundaries / total_balls * 100) if total_balls > 0 else 0.0

dot_balls = int((scope_df["total_runs"] == 0).sum())
dot_ball_pct = (dot_balls / total_balls * 100) if total_balls > 0 else 0.0

extras_runs = int(scope_df["extras"].sum())
extras_pct = (extras_runs / total_runs * 100) if total_runs > 0 else 0.0

wkts = int(scope_df["is_wicket"].sum())
wkts_per_match = (wkts / total_matches) if total_matches > 0 else 0.0

# Highest/Lowest match totals in selection (match-level aggregation)
innings_totals = (
    scope_df.groupby(["match_id", "innings"], as_index=False)
    .agg(
        innings_runs=("total_runs", "sum"),
        innings_balls=("match_id", "size"),
    )
)

# valid innings filter (avoid tiny partial innings)
innings_totals_valid = innings_totals[innings_totals["innings_balls"] >= 48].copy()

highest_score = int(innings_totals_valid["innings_runs"].max()) if len(innings_totals_valid) else 0
lowest_score = int(innings_totals_valid["innings_runs"].min()) if len(innings_totals_valid) else 0


a, b, c = st.columns(3)
d, e, f = st.columns(3)

with a:
    metric_tile(format_indian(total_matches), "Matches included in this selection.", value_color=PRIMARY_PALETTE[0])

with b:
    metric_tile(f"{run_rate:.2f}", "Overall run rate (runs per over).", value_color=PRIMARY_PALETTE[1])

with c:
    metric_tile(format_indian(highest_score), "Highest innings score in this scope.", value_color=PRIMARY_PALETTE[2])

with d:
    metric_tile(format_indian(lowest_score), "Lowest innings score in this scope.", value_color=PRIMARY_PALETTE[3])

with e:
    metric_tile(f"{extras_pct:.1f}%", "Extras share of total runs.", value_color=PRIMARY_PALETTE[0])

with f:
    metric_tile(f"{wkts_per_match:.1f}", "Average wickets per match.", value_color=PRIMARY_PALETTE[1])

st.divider()


# ============================================================
# Runs Split by Phase (always visible)
# ============================================================
html_section("🧩 Runs Split by Phase")
html_explain("Shows where most runs are scored: Powerplay, Middle overs, or Death.")

phase_df = scope_df.dropna(subset=["over_number"]).copy()
phase_df["phase"] = phase_df["over_number"].astype(int).apply(phase_from_over)

phase_agg = (
    phase_df.groupby("phase", as_index=False)
    .agg(total_runs=("total_runs", "sum"), balls=("phase", "size"))
)

phase_order = ["Powerplay", "Middle", "Death"]
phase_agg["phase"] = pd.Categorical(phase_agg["phase"], categories=phase_order, ordered=True)
phase_agg = phase_agg.sort_values("phase").copy()

total_phase_runs = float(phase_agg["total_runs"].sum())
phase_agg["run_share_pct"] = (phase_agg["total_runs"] / total_phase_runs * 100).fillna(0).round(2)

def pct_for(phase_name: str) -> float:
    row = phase_agg[phase_agg["phase"] == phase_name]
    if len(row) == 0:
        return 0.0
    return float(row["run_share_pct"].iloc[0])

p1, p2, p3 = st.columns(3)
with p1:
    metric_tile(f"{pct_for('Powerplay'):.2f}%", "Powerplay share (overs 0–5).", value_color=PRIMARY_PALETTE[2])
with p2:
    metric_tile(f"{pct_for('Middle'):.2f}%", "Middle overs share (overs 6–14).", value_color=PRIMARY_PALETTE[3])
with p3:
    metric_tile(f"{pct_for('Death'):.2f}%", "Death overs share (overs 15–19).", value_color=PRIMARY_PALETTE[1])

bar = (
    alt.Chart(phase_agg)
    .mark_bar()
    .encode(
        y=alt.Y("phase:N", title="", sort=phase_order),
        x=alt.X("total_runs:Q", title="Runs"),
        tooltip=[
            alt.Tooltip("phase:N", title="Phase"),
            alt.Tooltip("total_runs:Q", title="Runs", format=",.0f"),
            alt.Tooltip("run_share_pct:Q", title="Run Share %", format=".2f"),
        ],
    )
    .properties(height=190)
)

st.altair_chart(apply_altair_theme(bar), use_container_width=True)

st.divider()


# ============================================================
# Advanced Visuals (All Time only)
# ============================================================
advanced_allowed = selected_season == "All Time"

if not advanced_allowed:
    info_box("Advanced visuals are available only for <b>All Time</b>.")
    st.stop()

show_advanced = st.toggle("Show advanced visuals", value=True, key="tab1_toggle_advanced_alltime")

if not show_advanced:
    info_box("Turn this on to view season-level scoring trends.")
    st.stop()


# ============================================================
# Trend Chart (3 KPIs together) - All Time only
# ============================================================
html_section("📈 League Environment Trend (Season-by-Season)")
html_explain("Tracks pressure, boundary scoring, and wickets across seasons.")

trend_base = scope_df.dropna(subset=["season_id"]).copy()

season_kpis = (
    trend_base.groupby("season_id", as_index=False)
    .agg(
        matches=("match_id", "nunique"),
        balls=("match_id", "size"),
        boundaries=("batter_runs", lambda x: int((x.isin([4, 6])).sum())),
        dots=("total_runs", lambda x: int((x == 0).sum())),
        wickets=("is_wicket", "sum"),
    )
    .sort_values("season_id")
)

season_kpis["boundary_pct"] = (season_kpis["boundaries"] / season_kpis["balls"] * 100).fillna(0)
season_kpis["dot_ball_pct"] = (season_kpis["dots"] / season_kpis["balls"] * 100).fillna(0)
season_kpis["wkts_per_match"] = (season_kpis["wickets"] / season_kpis["matches"]).fillna(0)

long_df = pd.DataFrame(
    {
        "season_id": list(season_kpis["season_id"]) * 3,
        "metric": (["Boundary %"] * len(season_kpis))
        + (["Dot ball %"] * len(season_kpis))
        + (["Wickets per match"] * len(season_kpis)),
        "value": list(season_kpis["boundary_pct"])
        + list(season_kpis["dot_ball_pct"])
        + list(season_kpis["wkts_per_match"]),
    }
)

trend_chart = (
    alt.Chart(long_df)
    .mark_line(point=True)
    .encode(
        x=alt.X("season_id:Q", title="Season"),
        y=alt.Y("value:Q", title="Value"),
        color=alt.Color("metric:N", title="Metric"),
        tooltip=[
            alt.Tooltip("season_id:Q", title="Season"),
            alt.Tooltip("metric:N", title="Metric"),
            alt.Tooltip("value:Q", title="Value", format=".2f"),
        ],
    )
    .properties(height=330)
)

st.altair_chart(apply_altair_theme(trend_chart), use_container_width=True)

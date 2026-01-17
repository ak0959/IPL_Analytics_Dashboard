import os
import pandas as pd
import streamlit as st
import plotly.express as px

from src.ui import (
    html_title, html_subtitle, html_section, html_explain,
    html_badge, info_box, metric_tile, PRIMARY_PALETTE)
from src.data_loader import load_kpi_csv

st.set_page_config(page_title="Overview | IPL Strategy Dashboard", layout="wide")


# -----------------------------
# Indian number formatting
# -----------------------------
def format_indian(n):
    try:
        n = int(float(n))
    except:
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


# -----------------------------
# Header
# -----------------------------
html_title("All Seasons - Quick Insights")
html_subtitle("Snapshot of key metrics and scoring patterns across all IPL seasons.")
st.markdown("")


# -----------------------------
# Region controls
# -----------------------------
region_map = {
    "All Venues": "all",
    "India": "india",
    "Overseas": "overseas"
}

top1, top2, top3 = st.columns([1.2, 1.2, 2.6])

with top1:
    selected_region_label = st.selectbox(
        "Venue Region",
        options=list(region_map.keys()),
        index=0,
        key="region_overview_kpi"
    )
    region_key = region_map[selected_region_label]


# -----------------------------
# Load KPI files (region-aware)
# -----------------------------
overview_df = load_kpi_csv("master_kpis", "overview", f"kpi_overview_summary_{region_key}.csv")
runs_by_season = load_kpi_csv("master_kpis", "season", f"kpi_runs_by_season_{region_key}.csv")
runs_by_phase = load_kpi_csv("master_kpis", "phase", f"kpi_runs_by_phase_{region_key}.csv")

# Ensure numeric season
runs_by_season["season_id_x"] = pd.to_numeric(runs_by_season["season_id_x"], errors="coerce").astype("Int64")
runs_by_phase["season_id_x"] = pd.to_numeric(runs_by_phase["season_id_x"], errors="coerce").astype("Int64")

seasons = sorted([int(x) for x in runs_by_season["season_id_x"].dropna().unique().tolist()])
season_options = ["All Time"] + seasons

with top2:
    selected_season = st.selectbox(
        "Season",
        options=season_options,
        index=0,
        key="season_overview_kpi"
    )

with top3:
    st.markdown(
        "<div style='font-size: 1.02rem; color:#666; padding-top: 28px; line-height:1.4;'>"
        "Default is <b>All Venues</b> + <b>All Time</b>. Use filters to narrow your scope."
        "</div>",
        unsafe_allow_html=True
    )


# -----------------------------
# Apply season filter (fast)
# -----------------------------
if selected_season == "All Time":
    total_matches = int(overview_df.loc[0, "total_matches"])
    total_balls = int(overview_df.loc[0, "total_balls"])
    total_runs = int(overview_df.loc[0, "total_runs"])
    total_seasons = int(overview_df.loc[0, "total_seasons"])

    phase_scope = runs_by_phase.copy()
    scope_label = f"{selected_region_label} • All Time"
else:
    season_scope = runs_by_season[runs_by_season["season_id_x"] == int(selected_season)].copy()

    total_matches = int(season_scope["matches"].iloc[0]) if len(season_scope) else 0
    total_balls = int(season_scope["balls"].iloc[0]) if len(season_scope) else 0
    total_runs = int(season_scope["total_runs"].iloc[0]) if len(season_scope) else 0
    total_seasons = 1

    phase_scope = runs_by_phase[runs_by_phase["season_id_x"] == int(selected_season)].copy()
    scope_label = f"{selected_region_label} • {selected_season}"


html_badge(f"Showing: <b>{scope_label}</b>")


# -----------------------------
# Metric tiles
# -----------------------------
a, b, c, d = st.columns(4)

with a:
    metric_tile(format_indian(total_matches), "Total distinct matches in this scope.", value_color=PRIMARY_PALETTE[0])

with b:
    metric_tile(format_indian(total_balls), "Total deliveries across all matches.", value_color=PRIMARY_PALETTE[3])

with c:
    metric_tile(format_indian(total_runs), "Runs scored (batting + extras) across matches.", value_color=PRIMARY_PALETTE[1])

with d:
    metric_tile(format_indian(total_seasons), "Number of seasons covered in this selection.", value_color=PRIMARY_PALETTE[2])

st.divider()


# -----------------------------
# Advanced visuals toggle
# -----------------------------
show_advanced = st.toggle(
    "Show advanced visuals",
    value=False,
    key="toggle_overview_advanced_kpi"
)

if show_advanced:
    html_section("Trends & Patterns")
    html_explain("These visuals show how scoring changes over time and where runs typically come from.")

    # Trend by season (only All Time)
    if selected_season == "All Time":
        trend_df = runs_by_season.sort_values("season_id_x").copy()

        fig1 = px.line(
            trend_df,
            x="season_id_x",
            y="total_runs",
            markers=True,
            title="Runs trend by season",
            hover_data={
                "season_id_x": True,
                "total_runs": True,
                "matches": True,
                "balls": True,
                "batter_runs": True
            },
            labels={
                "season_id_x": "Season",
                "total_runs": "Total Runs",
                "matches": "Matches",
                "balls": "Balls",
                "batter_runs": "Batter Runs"
            },
            color_discrete_sequence=[PRIMARY_PALETTE[0]]
        )
        fig1.update_layout(height=320, margin=dict(l=10, r=10, t=60, b=10))
        st.plotly_chart(fig1, use_container_width=True)

        info_box(
            "<b>Key Insight</b> This trend highlights high-scoring eras and seasons where run output spikes. "
            "It helps compare seasons without going match-by-match."
        )

        st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)

    # Runs split by phase (donut + phase shares)
    if len(phase_scope) > 0:
        phase_agg = (
            phase_scope.groupby("phase", as_index=False)
            .agg(total_runs=("total_runs", "sum"), balls=("balls", "sum"))
        )

        if phase_agg["total_runs"].sum() > 0:
            phase_agg["run_share_pct"] = (phase_agg["total_runs"] / phase_agg["total_runs"].sum() * 100).round(2)
        else:
            phase_agg["run_share_pct"] = 0.0

        def pct_for(phase_name):
            row = phase_agg[phase_agg["phase"] == phase_name]
            if len(row) == 0:
                return 0.0
            return float(row["run_share_pct"].iloc[0])

        powerplay_pct = pct_for("Powerplay")
        middle_pct = pct_for("Middle")
        death_pct = pct_for("Death")

        p1, p2, p3 = st.columns(3)

        with p1:
            metric_tile(f"{powerplay_pct:.2f}%", "Powerplay share (overs 0–5).", value_color=PRIMARY_PALETTE[2])
        with p2:
            metric_tile(f"{middle_pct:.2f}%", "Middle overs share (overs 6–14).", value_color=PRIMARY_PALETTE[3])
        with p3:
            metric_tile(f"{death_pct:.2f}%", "Death overs share (overs 15–19).", value_color=PRIMARY_PALETTE[1])

        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

        vibgyor = [PRIMARY_PALETTE[2], PRIMARY_PALETTE[3], PRIMARY_PALETTE[1]]

        fig2 = px.pie(
            phase_agg,
            names="phase",
            values="total_runs",
            hole=0.62,
            title="Runs split by phase",
            color="phase",
            color_discrete_sequence=vibgyor
        )

        fig2.update_traces(
            textinfo="percent",
            textposition="inside",
            insidetextorientation="radial",
            hovertemplate="<b>%{label}</b><br>Total runs: %{value}<br>Share: %{percent}<extra></extra>"
        )

        fig2.update_layout(
            height=260,
            margin=dict(l=10, r=10, t=60, b=10),
            legend=dict(orientation="v")
        )

        cc1, cc2, cc3 = st.columns([1.2, 2.0, 1.2])
        with cc2:
            st.plotly_chart(fig2, use_container_width=True)

        info_box(
            "<b>Key Insight</b> The phase split shows where most runs come from. "
            "Teams can plan resources for Powerplay aggression, middle-overs control, or death-over finishing."
        )
    else:
        st.info("Phase split is not available for this selection.")

else:
    info_box(
        "Turn on <b>Show advanced visuals</b> to view scoring trends by season and phase distribution."
    )

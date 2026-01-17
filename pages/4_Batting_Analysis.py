import os
import pandas as pd
import streamlit as st
import plotly.express as px

from src.ui import (
    html_title, html_subtitle, html_section, html_explain,
    html_badge, info_box, metric_tile, PRIMARY_PALETTE
)
from src.data_loader import load_kpi_csv


st.set_page_config(page_title="Batting Analysis | IPL Strategy Dashboard", layout="wide")


# ============================================================
# TAB 4: Batting Analysis (FAST - KPI file)
# ============================================================

html_title("Batting Analysis")
html_subtitle("Explore impactful batters, scoring style, and phase-wise intent using precomputed season + region KPIs.")
st.markdown("")


# -----------------------------
# Load KPI file
# -----------------------------
bat = load_kpi_csv("sub_kpis", "batting", "tab4_batting_master.csv")

# Basic cleanup
bat["venue_region"] = bat["venue_region"].astype(str).str.strip()
bat["season"] = bat["season"].astype(str).str.strip()
bat["batter"] = bat["batter"].astype(str).str.strip()

# -----------------------------
# Filters
# -----------------------------
c1, c2, c3, c4 = st.columns([1.2, 1.2, 1.2, 1.2])

with c1:
    region_choice = st.selectbox(
        "Venue Region",
        ["All Venues", "India", "Overseas"],
        index=0,
        key="tab4_region"
    )

with c2:
    # season list depends on region scope
    if region_choice == "All Venues":
        season_list = sorted(bat["season"].unique().tolist(), key=lambda x: (x != "All Time", x))
    else:
        season_list = sorted(
            bat[bat["venue_region"] == region_choice]["season"].unique().tolist(),
            key=lambda x: (x != "All Time", x)
        )

    season_choice = st.selectbox(
        "Season",
        season_list,
        index=0,
        key="tab4_season"
    )

with c3:
    min_balls = st.selectbox(
        "Min balls faced",
        [0, 30, 60, 120, 250],
        index=2,
        key="tab4_min_balls"
    )

with c4:
    top_n = st.selectbox(
        "Top Batters",
        [10, 15, 20],
        index=0,
        key="tab4_topn"
    )

# -----------------------------
# Apply filters
# -----------------------------
bat_scope = bat.copy()

if region_choice != "All Venues":
    bat_scope = bat_scope[bat_scope["venue_region"] == region_choice].copy()

bat_scope = bat_scope[bat_scope["season"] == season_choice].copy()

bat_scope = bat_scope[bat_scope["balls"] >= int(min_balls)].copy()

html_badge(f"Showing: <b>{region_choice}</b> • <b>{season_choice}</b> • Min balls: <b>{min_balls}</b>")

if len(bat_scope) == 0:
    st.warning("No batters match the selected filters. Try lowering the minimum balls filter.")
    st.stop()


# -----------------------------
# Summary tiles (simple + recruiter-friendly)
# -----------------------------
total_batters = int(bat_scope["batter"].nunique())
total_runs = int(bat_scope["runs"].sum())
avg_sr = float(bat_scope["strike_rate"].mean())

a, b, c, d = st.columns(4)

with a:
    metric_tile(f"{total_batters}", "Batters in scope after filters.", value_color=PRIMARY_PALETTE[0])

with b:
    metric_tile(f"{total_runs:,}", "Total runs scored by this batter group.", value_color=PRIMARY_PALETTE[1])

with c:
    metric_tile(f"{avg_sr:.2f}", "Average strike rate across batters in scope.", value_color=PRIMARY_PALETTE[2])

with d:
    metric_tile(f"{min_balls}", "Minimum balls filter (stability control).", value_color=PRIMARY_PALETTE[3])

st.divider()


html_section("Most Impactful Batters")
html_explain("Question answered: who produces the most runs in the selected scope?")

impact = bat_scope.sort_values("runs", ascending=False).head(int(top_n)).copy()

fig = px.bar(
    impact.sort_values("runs", ascending=True),
    x="runs",
    y="batter",
    orientation="h",
    text="runs",
    hover_data={
        "runs": True,
        "balls": True,
        "strike_rate": True,
        "consistency_20_plus_pct": True,
        "avg_share_of_team_runs_pct": True
    },
    color_discrete_sequence=[PRIMARY_PALETTE[0]],
    height=520
)
fig.update_traces(textposition="outside")
fig.update_layout(
    margin=dict(l=10, r=10, t=10, b=10),
    yaxis_title="",
    xaxis_title="Runs",
    yaxis=dict(categoryorder="total ascending")
)

st.plotly_chart(fig, use_container_width=True)

info_box(
    "<b>So what?</b> This is a pure output leaderboard. "
    "It highlights the biggest run contributors in this scope before we evaluate style and phase intent."
)

html_section("Most Impactful Batters (Leaderboard)")
html_explain("Question answered: who ranks highest by runs, shown in a clean lightweight style?")

impact = bat_scope.sort_values("runs", ascending=False).head(int(top_n)).copy()
impact = impact.sort_values("runs", ascending=True)

fig = px.scatter(
    impact,
    x="runs",
    y="batter",
    size="runs",
    hover_name="batter",
    hover_data={
        "runs": True,
        "balls": True,
        "strike_rate": True,
        "consistency_20_plus_pct": True
    },
    color_discrete_sequence=[PRIMARY_PALETTE[1]],
    height=520
)

fig.update_layout(
    margin=dict(l=10, r=10, t=10, b=10),
    yaxis_title="",
    xaxis_title="Runs"
)

st.plotly_chart(fig, use_container_width=True)

info_box(
    "<b>So what?</b> Same ranking idea as a bar chart, but lighter visually. "
    "This works well if you want the page to feel less cluttered."
)

html_section("Impact Map: Output vs Tempo")
html_explain("Question answered: who scores big AND scores fast, with enough volume to trust the signal?")

impact = bat_scope.sort_values("runs", ascending=False).head(int(top_n)).copy()

fig = px.scatter(
    impact,
    x="strike_rate",
    y="runs",
    size="balls",
    hover_name="batter",
    hover_data={
        "runs": True,
        "balls": True,
        "strike_rate": True,
        "dot_ball_pct": True,
        "boundary_dependency_pct": True,
        "consistency_20_plus_pct": True
    },
    color_discrete_sequence=[PRIMARY_PALETTE[0]],
    height=520
)

fig.update_layout(
    margin=dict(l=10, r=10, t=10, b=10),
    xaxis_title="Strike Rate (scoring speed)",
    yaxis_title="Runs (output)"
)

st.plotly_chart(fig, use_container_width=True)

info_box(
    "<b>So what?</b> Top-right batters combine high output with high tempo. "
    "Bigger bubbles mean more balls faced, which increases confidence in the performance signal."
)

html_section("Impact Map: Output vs Consistency")
html_explain("Question answered: who scores big AND does it consistently across innings?")

impact = bat_scope.sort_values("runs", ascending=False).head(int(top_n)).copy()

fig = px.scatter(
    impact,
    x="consistency_20_plus_pct",
    y="runs",
    size="balls",
    hover_name="batter",
    hover_data={
        "runs": True,
        "balls": True,
        "strike_rate": True,
        "consistency_20_plus_pct": True,
        "runs_per_dismissal": True,
        "avg_share_of_team_runs_pct": True
    },
    color_discrete_sequence=[PRIMARY_PALETTE[2]],
    height=520
)

fig.update_layout(
    margin=dict(l=10, r=10, t=10, b=10),
    xaxis_title="Consistency (20+ scores %)",
    yaxis_title="Runs (output)"
)

st.plotly_chart(fig, use_container_width=True)

info_box(
    "<b>So what?</b> This highlights reliable run-makers. "
    "High runs + high consistency is the profile of a stable top-order contributor."
)

html_section("Elite Cluster (Quadrant View)")
html_explain("Question answered: who sits in the elite zone — high output AND high consistency?")

impact = bat_scope.sort_values("runs", ascending=False).head(int(top_n)).copy()

x_med = float(impact["consistency_20_plus_pct"].median())
y_med = float(impact["runs"].median())

fig = px.scatter(
    impact,
    x="consistency_20_plus_pct",
    y="runs",
    size="balls",
    hover_name="batter",
    hover_data={
        "runs": True,
        "balls": True,
        "strike_rate": True,
        "avg_share_of_team_runs_pct": True
    },
    color_discrete_sequence=[PRIMARY_PALETTE[3]],
    height=520
)

fig.add_vline(x=x_med, line_dash="dot")
fig.add_hline(y=y_med, line_dash="dot")

fig.update_layout(
    margin=dict(l=10, r=10, t=10, b=10),
    xaxis_title="Consistency (20+ scores %)",
    yaxis_title="Runs (output)"
)

st.plotly_chart(fig, use_container_width=True)

info_box(
    "<b>So what?</b> The top-right quadrant is the elite zone: high run output and high consistency. "
    "These are the safest batters to build lineups around."
)

html_section("Runs vs Strike Rate (Top Batters)")
html_explain("Question answered: among top run scorers, who also scores fast?")

impact = bat_scope.sort_values("runs", ascending=False).head(int(top_n)).copy()

# Reshape for grouped bar
long_df = pd.DataFrame({
    "batter": list(impact["batter"]) * 2,
    "metric": (["Runs"] * len(impact)) + (["Strike Rate"] * len(impact)),
    "value": list(impact["runs"]) + list(impact["strike_rate"])
})

fig = px.bar(
    long_df,
    x="value",
    y="batter",
    orientation="h",
    color="metric",
    barmode="group",
    color_discrete_sequence=[PRIMARY_PALETTE[0], PRIMARY_PALETTE[1]],
    height=540
)

fig.update_layout(
    margin=dict(l=10, r=10, t=10, b=10),
    yaxis_title="",
    xaxis_title="Value"
)

st.plotly_chart(fig, use_container_width=True)

info_box(
    "<b>So what?</b> Runs shows output. Strike Rate shows tempo. "
    "Use this to find batters who deliver both volume and speed."
)

html_section("Batter Profile Heatmap")
html_explain("Question answered: how do top batters compare across key batting traits in one view?")

impact = bat_scope.sort_values("runs", ascending=False).head(int(top_n)).copy()

hm = impact[[
    "batter",
    "runs",
    "strike_rate",
    "consistency_20_plus_pct",
    "dot_ball_pct",
    "boundary_dependency_pct",
    "strike_rotation_pct"
]].copy()

# Normalize columns for comparable heat intensity
cols_to_norm = ["runs", "strike_rate", "consistency_20_plus_pct", "dot_ball_pct",
                "boundary_dependency_pct", "strike_rotation_pct"]

for c in cols_to_norm:
    mn = hm[c].min()
    mx = hm[c].max()
    hm[c] = 0 if mx == mn else (hm[c] - mn) / (mx - mn)

hm_melt = hm.melt(id_vars=["batter"], var_name="metric", value_name="norm_value")

fig = px.imshow(
    hm_melt.pivot(index="batter", columns="metric", values="norm_value"),
    aspect="auto",
    height=520
)

fig.update_layout(
    margin=dict(l=10, r=10, t=10, b=10),
    xaxis_title="Metric",
    yaxis_title="Batter"
)

st.plotly_chart(fig, use_container_width=True)

info_box(
    "<b>So what?</b> This is a fast way to scan batter profiles. "
    "Brighter cells indicate stronger relative performance for that metric within the Top N."
)

html_section("Run Contribution Concentration (Pareto View)")
html_explain("Question answered: how concentrated is scoring — do a few batters dominate the run output?")

impact = bat_scope.sort_values("runs", ascending=False).copy()
impact["rank"] = range(1, len(impact) + 1)

total_runs_scope = impact["runs"].sum()
impact["run_share_pct"] = (impact["runs"] / total_runs_scope) * 100
impact["cum_share_pct"] = impact["run_share_pct"].cumsum()

pareto = impact.head(int(top_n)).copy()

fig = px.line(
    pareto,
    x="rank",
    y="cum_share_pct",
    markers=True,
    hover_data={"batter": True, "runs": True, "cum_share_pct": True},
    color_discrete_sequence=[PRIMARY_PALETTE[4]],
    height=420
)

fig.update_layout(
    margin=dict(l=10, r=10, t=10, b=10),
    xaxis_title="Batter rank (by runs)",
    yaxis_title="Cumulative run share (%)"
)

st.plotly_chart(fig, use_container_width=True)

info_box(
    "<b>So what?</b> If the curve rises steeply, a small set of batters contributes most of the runs. "
    "That can indicate a team depends heavily on a few key players."
)


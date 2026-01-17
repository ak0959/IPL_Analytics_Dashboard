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


st.set_page_config(page_title="Batting Analysis | IPL Strategy Dashboard", layout="wide")


# ============================================================
# GLOBAL UI STYLING (applies across Tab 4)
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
    Global Altair styling for Tab 4 charts (axis + legend).
    Ensures consistent formatting across the page.
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
# TAB 4: Batting Analysis (FAST - KPI file)
# ============================================================

html_title("Batting Analysis")
html_subtitle(
    "Explore impactful batters, scoring style, and phase-wise intent using precomputed season + region KPIs."
)
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
        key="tab4_region",
    )

with c2:
    if region_choice == "All Venues":
        season_list = sorted(
            bat["season"].unique().tolist(), key=lambda x: (x != "All Time", x)
        )
    else:
        season_list = sorted(
            bat[bat["venue_region"] == region_choice]["season"].unique().tolist(),
            key=lambda x: (x != "All Time", x),
        )

    season_choice = st.selectbox(
        "Season",
        season_list,
        index=0,
        key="tab4_season",
    )

with c3:
    min_balls = st.selectbox(
        "Min balls faced",
        [0, 30, 60, 120, 250],
        index=2,
        key="tab4_min_balls",
    )

with c4:
    top_n = st.selectbox(
        "Top Batters",
        [5, 10, 15],
        index=0,  # default = 5
        key="tab4_topn",
    )


# -----------------------------
# Theme selector (applies across Tab 4)
# -----------------------------
theme_choice = st.selectbox(
    "Theme",
    ["Light", "Classic (Bold)", "Greyscale"],
    index=0,
    key="tab4_theme",
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

TAB4_COLORS = THEMES[theme_choice]


# -----------------------------
# Apply filters
# -----------------------------
bat_scope = bat.copy()

if region_choice != "All Venues":
    bat_scope = bat_scope[bat_scope["venue_region"] == region_choice].copy()

bat_scope = bat_scope[bat_scope["season"] == season_choice].copy()
bat_scope = bat_scope[bat_scope["balls"] >= int(min_balls)].copy()

html_badge(
    f"Showing: <b>{region_choice}</b> • <b>{season_choice}</b> • Min balls: <b>{min_balls}</b>"
)

if len(bat_scope) == 0:
    st.warning("No batters match the selected filters. Try lowering the minimum balls filter.")
    st.stop()


# -----------------------------
# Dynamic chart height (master)
# -----------------------------
BASE_H = 180
ROW_H = 36
chart_h = int(BASE_H + (ROW_H * int(top_n)))


# -----------------------------
# Summary tiles
# -----------------------------
total_batters = int(bat_scope["batter"].nunique())
total_runs = int(bat_scope["runs"].sum())
avg_sr = float(bat_scope["strike_rate"].mean())

a, b, c, d = st.columns(4)

with a:
    metric_tile(
        f"{total_batters}",
        "Batters in scope after filters.",
        value_color=TAB4_COLORS["blue"],
    )

with b:
    metric_tile(
        f"{total_runs:,}",
        "Total runs scored by this batter group.",
        value_color=TAB4_COLORS["orange"],
    )

with c:
    metric_tile(
        f"{avg_sr:.2f}",
        "Average strike rate across batters in scope.",
        value_color=TAB4_COLORS["green"],
    )

with d:
    metric_tile(
        f"{min_balls}",
        "Minimum balls filter (stability control).",
        value_color=TAB4_COLORS["purple"],
    )

st.divider()


# ============================================================
# SECTION 1: Impact Leaders (Runs)
# ============================================================

html_section("Impact Leaders (Runs)")
html_explain("Question answered: who are the biggest run contributors in the selected scope?")

impact = (
    bat_scope.sort_values("runs", ascending=False)
    .head(int(top_n))
    .copy()
)

order_list = impact["batter"].tolist()

# Base purple bar
base_runs = (
    alt.Chart(impact)
    .mark_bar()
    .encode(
        y=alt.Y("batter:N", sort=order_list, title=""),
        x=alt.X("runs:Q", title="Runs"),
        color=alt.value(TAB4_COLORS["purple"]),
        tooltip=[
            alt.Tooltip("batter:N", title="Batter"),
            alt.Tooltip("runs:Q", title="Runs", format=",.0f"),
            alt.Tooltip("balls:Q", title="Balls", format=",.0f"),
            alt.Tooltip("strike_rate:Q", title="Strike Rate", format=".1f"),
            alt.Tooltip("consistency_20_plus_pct:Q", title="Consistency (20+ %)", format=".1f"),
            alt.Tooltip("avg_share_of_team_runs_pct:Q", title="Avg Share Team Runs (%)", format=".1f"),
        ],
    )
    .properties(height=chart_h)
)

# Runs label inside bar
runs_labels = (
    alt.Chart(impact)
    .transform_calculate(x_pos="datum.runs * 0.80")
    .mark_text(color="#1b1b1b", fontSize=18)
    .encode(
        y=alt.Y("batter:N", sort=order_list, title=""),
        x=alt.X("x_pos:Q"),
        text=alt.Text("runs:Q", format=",.0f"),
    )
)

impact_chart = apply_altair_theme(base_runs + runs_labels)
st.altair_chart(impact_chart, use_container_width=True)

with st.expander("📋 View Top Batters Table", expanded=False):
    leaderboard_cols = [
        "batter",
        "runs",
        "balls",
        "strike_rate",
        "consistency_20_plus_pct",
        "avg_share_of_team_runs_pct",
    ]

    leaderboard = impact[leaderboard_cols].copy()

    leaderboard = leaderboard.rename(
        columns={
            "batter": "Batter",
            "runs": "Runs",
            "balls": "Balls",
            "strike_rate": "Strike Rate",
            "consistency_20_plus_pct": "Consistency (20+ %)",
            "avg_share_of_team_runs_pct": "Avg Share of Team Runs (%)",
        }
    )

    leaderboard["Strike Rate"] = leaderboard["Strike Rate"].round(1)
    leaderboard["Consistency (20+ %)"] = leaderboard["Consistency (20+ %)"].round(1)
    leaderboard["Avg Share of Team Runs (%)"] = leaderboard["Avg Share of Team Runs (%)"].round(1)

    st.dataframe(leaderboard, use_container_width=True, hide_index=True)

st.divider()


# ============================================================
# SECTION 2: Scoring Mix (Stacked Runs + % labels inside)
# ============================================================

html_section("Scoring Mix: Boundary vs Non-Boundary Runs")
html_explain("Question answered: how much of each batter’s output comes from boundaries vs non-boundary scoring?")

# Local Top N for this chart only (compact)
dd1, dd2, dd3 = st.columns([1, 4, 4])
with dd1:
    top_n_mix = st.selectbox(
        "Top Batters",
        [5, 10, 15],
        index=[5, 10, 15].index(int(top_n)),
        key="tab4_topn_mix",
    )

mix_scope = (
    bat_scope.sort_values("runs", ascending=False)
    .head(int(top_n_mix))
    .copy()
)

mix_scope["non_boundary_runs"] = (mix_scope["runs"] - mix_scope["boundary_runs"]).clip(lower=0)
mix_scope["boundary_pct"] = (mix_scope["boundary_runs"] / mix_scope["runs"] * 100).fillna(0)
mix_scope["non_boundary_pct"] = (100 - mix_scope["boundary_pct"]).clip(lower=0)

# Runs stack data
stack_df = pd.DataFrame(
    {
        "batter": list(mix_scope["batter"]) * 2,
        "run_type": (["Boundary Runs"] * len(mix_scope)) + (["Non-Boundary Runs"] * len(mix_scope)),
        "runs": list(mix_scope["boundary_runs"]) + list(mix_scope["non_boundary_runs"]),
    }
)

# % label data (same 2 segments)
pct_df = pd.DataFrame(
    {
        "batter": list(mix_scope["batter"]) * 2,
        "run_type": (["Boundary Runs"] * len(mix_scope)) + (["Non-Boundary Runs"] * len(mix_scope)),
        "pct": list(mix_scope["boundary_pct"]) + list(mix_scope["non_boundary_pct"]),
    }
)

order_list_2 = mix_scope["batter"].tolist()

# Dynamic height for this chart only
chart_h_mix = int(BASE_H + (ROW_H * int(top_n_mix)))

# Base stacked runs bar
base_stack = (
    alt.Chart(stack_df)
    .mark_bar()
    .encode(
        y=alt.Y("batter:N", sort=order_list_2, title=""),
        x=alt.X("sum(runs):Q", title="Runs"),
        color=alt.Color(
            "run_type:N",
            title="",
            scale=alt.Scale(
                domain=["Boundary Runs", "Non-Boundary Runs"],
                range=[TAB4_COLORS["blue"], TAB4_COLORS["green"]],
            ),
        ),
        tooltip=[
            alt.Tooltip("batter:N", title="Batter"),
            alt.Tooltip("run_type:N", title="Type"),
            alt.Tooltip("sum(runs):Q", title="Runs", format=",.0f"),
        ],
    )
    .properties(height=chart_h_mix)
)

# --- % labels positioned INSIDE each segment (mapped to absolute runs scale)
pct_df2 = pct_df.copy()

runs_total_map = mix_scope.set_index("batter")["runs"].to_dict()
boundary_frac_map = (
    (mix_scope.set_index("batter")["boundary_runs"] / mix_scope.set_index("batter")["runs"])
    .fillna(0)
    .to_dict()
)

pct_df2["pct_frac"] = pct_df2["pct"] / 100.0


def segment_mid_abs(row):
    total = float(runs_total_map.get(row["batter"], 0))
    b = float(boundary_frac_map.get(row["batter"], 0))
    w = float(row["pct_frac"])

    start_frac = 0.0 if row["run_type"] == "Boundary Runs" else b
    mid_frac = start_frac + (w / 2)

    return total * mid_frac


pct_df2["x_mid_abs"] = pct_df2.apply(segment_mid_abs, axis=1)

labels = (
    alt.Chart(pct_df2)
    .mark_text(color="#1b1b1b", fontSize=18)
    .encode(
        y=alt.Y("batter:N", sort=order_list_2, title=""),
        x=alt.X("x_mid_abs:Q"),
        detail="run_type:N",
    )
    .transform_calculate(label="round(datum.pct) + '%'")
    .encode(text="label:N")
)

mix_chart = apply_altair_theme(base_stack + labels)
st.altair_chart(mix_chart, use_container_width=True)


bat_scope = bat_scope[bat_scope["balls"] >= int(min_balls)].copy()

st.divider()

# ============================================================
# SECTION 3: Reliability (Stable Run-Makers)
# ============================================================

html_section("Reliability: Stable Run-Makers")
html_explain("How stable and repeatable is batting impact across innings (with sample-size fairness)?")

# -----------------------------
# Ranking method selector
# -----------------------------
rank_method = st.radio(
    "Ranking Method (applies to all reliability charts)",
    ["Pure KPI (Metric only)", "Volume-adjusted (Metric × √balls)"],
    index=1,
    horizontal=True,
    key="tab4_sec3_rank_method",
)

with st.expander("ℹ️ Why we use volume-adjusted ranking (with examples)", expanded=False):
    st.markdown(
        """
**Why this matters**  
Reliability KPIs can look extreme for batters with limited sample size. For example, someone can show
very high consistency if they had a short run of strong innings.  

To keep the rankings fair, we allow two approaches:

**1) Pure KPI ranking**  
- Ranks batters only by the metric value  
- Example: highest Consistency (20+ %) ranks #1  
- Best when you want the “best metric value” without considering volume.

**2) Volume-adjusted ranking (recommended)**  
- Ranks batters by: **KPI × √balls**  
- Rewards strong performance **and** meaningful batting volume  
- √balls is used because it boosts stability, but avoids letting volume dominate too aggressively.

---

### Worked example (Consistency 20+ %)  
Assume in the selected scope:

**Sai Sudarshan**  
- Consistency = 79%  
- Balls = 1,279  
- √balls ≈ √1279 ≈ 35.76  
- Volume-adjusted score = 79 × 35.76 ≈ **2,825**

**Virat Kohli**  
- Consistency = 61%  
- Balls = 5,804  
- √balls ≈ √5804 ≈ 76.18  
- Volume-adjusted score = 61 × 76.18 ≈ **4,647**

✅ Even though Sai has the higher % consistency, Kohli ranks higher because the performance is proven across far more volume.

---

### Same idea for Runs per Dismissal  
If:
- Player A has Runs/Dismissal = 47 with 1,279 balls → score ≈ 47 × 35.76 = 1,681  
- Player B has Runs/Dismissal = 42 with 5,804 balls → score ≈ 42 × 76.18 = 3,199  

✅ Player B ranks higher due to much higher stability.
        """
    )


# --- Stability threshold (innings)
avg_innings = float(bat_scope["innings_played"].mean())
min_innings_threshold = int(round(avg_innings))

avg_runs_per_innings = float((bat_scope["runs"] / bat_scope["innings_played"]).mean())

st.caption(
    f"Stability filter: innings_played ≥ {min_innings_threshold} | Avg runs/innings ≈ {avg_runs_per_innings:.0f}"
)

stable_scope = bat_scope.copy()
stable_scope = stable_scope[stable_scope["innings_played"] >= min_innings_threshold].copy()

if len(stable_scope) == 0:
    st.warning("No batters meet the stability threshold in this scope.")
    st.stop()


def chart_style_for_topn(n: int) -> dict:
    if n <= 5:
        return {"angle": -25, "label_size": 12, "text_size": 16}
    if n <= 10:
        return {"angle": -45, "label_size": 11, "text_size": 14}
    return {"angle": -60, "label_size": 10, "text_size": 12}


def compute_rank_score(df: pd.DataFrame, metric_col: str) -> pd.DataFrame:
    """
    Adds a rank_score column depending on ranking method.
    Pure KPI -> rank_score = metric
    Volume-adjusted -> rank_score = metric × √balls
    """
    df = df.copy()

    if rank_method.startswith("Pure KPI"):
        df["rank_score"] = df[metric_col]
        return df

    # Volume-adjusted
    df["vol_weight"] = df["balls"] ** 0.5
    df["rank_score"] = df[metric_col] * df["vol_weight"]
    return df


FIXED_H = 340


# ============================================================
# ROW 1: Consistency + Runs per Dismissal
# ============================================================

row1_left, gap1, row1_right = st.columns([1, 0.12, 1])
with gap1:
    st.markdown("")


# -----------------------------
# Chart 1: Consistency (20+ %)
# -----------------------------
with row1_left:
    st.markdown("### Consistency (20+ Scores %)")

    top_n_cons = st.selectbox(
        "Top Batters",
        [5, 10, 15],
        index=0,
        key="tab4_topn_consistency_vertical_row",
    )
    style_cons = chart_style_for_topn(int(top_n_cons))

    cons_df = stable_scope[
        ["batter", "consistency_20_plus_pct", "innings_played", "runs", "balls"]
    ].copy()

    cons_df = compute_rank_score(cons_df, "consistency_20_plus_pct")

    cons_df = (
        cons_df.sort_values("rank_score", ascending=False)
        .head(int(top_n_cons))
        .copy()
    )

    # Sort descending by KPI for visual order
    cons_df = cons_df.sort_values("consistency_20_plus_pct", ascending=False).copy()
    order_cons = cons_df["batter"].tolist()

    base_cons = (
        alt.Chart(cons_df)
        .mark_bar()
        .encode(
            x=alt.X(
                "batter:N",
                sort=order_cons,
                title="",
                axis=alt.Axis(labelAngle=style_cons["angle"], labelFontSize=style_cons["label_size"]),
            ),
            y=alt.Y("consistency_20_plus_pct:Q", title="Consistency (20+ %)"),
            color=alt.value(TAB4_COLORS["teal"]),
            tooltip=[
                alt.Tooltip("batter:N", title="Batter"),
                alt.Tooltip("consistency_20_plus_pct:Q", title="Consistency (20+ %)", format=".0f"),
                alt.Tooltip("balls:Q", title="Balls", format=",.0f"),
                alt.Tooltip("innings_played:Q", title="Innings", format=",.0f"),
                alt.Tooltip("runs:Q", title="Runs", format=",.0f"),
            ],
        )
        .properties(height=FIXED_H)
    )

    cons_labels = (
        alt.Chart(cons_df)
        .transform_calculate(y_pos="datum.consistency_20_plus_pct * 0.65")
        .mark_text(color="#1b1b1b", fontSize=style_cons["text_size"])
        .encode(
            x=alt.X("batter:N", sort=order_cons, axis=alt.Axis(labelAngle=style_cons["angle"])),
            y=alt.Y("y_pos:Q"),
        )
        .transform_calculate(label="round(datum.consistency_20_plus_pct) + '%'")
        .encode(text="label:N")
    )

    st.altair_chart(apply_altair_theme(base_cons + cons_labels), use_container_width=True)
    st.caption("Higher = more frequent 20+ contributions across innings.")


# -----------------------------
# Chart 2: Runs per Dismissal
# -----------------------------
with row1_right:
    st.markdown("### Runs per Dismissal (Efficiency)")

    top_n_rpd = st.selectbox(
        "Top Batters",
        [5, 10, 15],
        index=0,
        key="tab4_topn_rpd_vertical_row",
    )
    style_rpd = chart_style_for_topn(int(top_n_rpd))

    rpd_df = stable_scope[
        ["batter", "runs_per_dismissal", "innings_played", "runs", "outs", "balls"]
    ].copy()

    rpd_df = rpd_df.dropna(subset=["runs_per_dismissal"]).copy()

    rpd_df = compute_rank_score(rpd_df, "runs_per_dismissal")

    rpd_df = (
        rpd_df.sort_values("rank_score", ascending=False)
        .head(int(top_n_rpd))
        .copy()
    )

    rpd_df = rpd_df.sort_values("runs_per_dismissal", ascending=False).copy()
    order_rpd = rpd_df["batter"].tolist()

    base_rpd = (
        alt.Chart(rpd_df)
        .mark_bar()
        .encode(
            x=alt.X(
                "batter:N",
                sort=order_rpd,
                title="",
                axis=alt.Axis(labelAngle=style_rpd["angle"], labelFontSize=style_rpd["label_size"]),
            ),
            y=alt.Y("runs_per_dismissal:Q", title="Runs per Dismissal"),
            color=alt.value(TAB4_COLORS["orange"]),
            tooltip=[
                alt.Tooltip("batter:N", title="Batter"),
                alt.Tooltip("runs_per_dismissal:Q", title="Runs/Dismissal", format=".0f"),
                alt.Tooltip("balls:Q", title="Balls", format=",.0f"),
                alt.Tooltip("innings_played:Q", title="Innings", format=",.0f"),
                alt.Tooltip("runs:Q", title="Runs", format=",.0f"),
                alt.Tooltip("outs:Q", title="Outs", format=",.0f"),
            ],
        )
        .properties(height=FIXED_H)
    )

    rpd_labels = (
        alt.Chart(rpd_df)
        .transform_calculate(y_pos="datum.runs_per_dismissal * 0.65")
        .mark_text(color="#1b1b1b", fontSize=style_rpd["text_size"])
        .encode(
            x=alt.X("batter:N", sort=order_rpd, axis=alt.Axis(labelAngle=style_rpd["angle"])),
            y=alt.Y("y_pos:Q"),
            text=alt.Text("runs_per_dismissal:Q", format=".0f"),
        )
    )

    st.altair_chart(apply_altair_theme(base_rpd + rpd_labels), use_container_width=True)
    st.caption("Higher = more runs scored per wicket (strong stability signal).")


st.divider()


# ============================================================
# ROW 2: Team Dependency + Strike Rate
# ============================================================

row2_left, gap2, row2_right = st.columns([1, 0.12, 1])
with gap2:
    st.markdown("")


# -----------------------------
# Chart 3: Team Dependency (%)
# -----------------------------
with row2_left:
    st.markdown("### Team Dependency (Avg Share of Team Runs %)")

    top_n_share = st.selectbox(
        "Top Batters",
        [5, 10, 15],
        index=0,
        key="tab4_topn_team_share_vertical_half",
    )
    style_share = chart_style_for_topn(int(top_n_share))

    share_df = stable_scope[
        ["batter", "avg_share_of_team_runs_pct", "innings_played", "runs", "balls"]
    ].copy()

    share_df = compute_rank_score(share_df, "avg_share_of_team_runs_pct")

    share_df = (
        share_df.sort_values("rank_score", ascending=False)
        .head(int(top_n_share))
        .copy()
    )

    share_df = share_df.sort_values("avg_share_of_team_runs_pct", ascending=False).copy()
    order_share = share_df["batter"].tolist()

    base_share = (
        alt.Chart(share_df)
        .mark_bar()
        .encode(
            x=alt.X(
                "batter:N",
                sort=order_share,
                title="",
                axis=alt.Axis(labelAngle=style_share["angle"], labelFontSize=style_share["label_size"]),
            ),
            y=alt.Y("avg_share_of_team_runs_pct:Q", title="Avg Share of Team Runs (%)"),
            color=alt.value(TAB4_COLORS["blue"]),
            tooltip=[
                alt.Tooltip("batter:N", title="Batter"),
                alt.Tooltip("avg_share_of_team_runs_pct:Q", title="Team Share (%)", format=".0f"),
                alt.Tooltip("balls:Q", title="Balls", format=",.0f"),
                alt.Tooltip("innings_played:Q", title="Innings", format=",.0f"),
                alt.Tooltip("runs:Q", title="Runs", format=",.0f"),
            ],
        )
        .properties(height=FIXED_H)
    )

    share_labels = (
        alt.Chart(share_df)
        .transform_calculate(y_pos="datum.avg_share_of_team_runs_pct * 0.65")
        .mark_text(color="#1b1b1b", fontSize=style_share["text_size"])
        .encode(
            x=alt.X("batter:N", sort=order_share, axis=alt.Axis(labelAngle=style_share["angle"])),
            y=alt.Y("y_pos:Q"),
        )
        .transform_calculate(label="round(datum.avg_share_of_team_runs_pct) + '%'")
        .encode(text="label:N")
    )

    st.altair_chart(apply_altair_theme(base_share + share_labels), use_container_width=True)
    st.caption("Higher = batter carries a larger share of team scoring.")

# -----------------------------
# Chart 4: Strike Rate (Tempo)
# -----------------------------
with row2_right:
    st.markdown("### Strike Rate (Tempo)")

    top_n_sr = st.selectbox(
        "Top Batters",
        [5, 10, 15],
        index=0,
        key="tab4_topn_strike_rate_vertical_half",
    )

    # ✅ NEW: display order selector (visual sorting)
    display_order_sr = st.radio(
        "Display Order",
        ["Ranking score (recommended)", "Raw strike rate"],
        index=0,
        horizontal=True,
        key="tab4_sr_display_order",
    )

    style_sr = chart_style_for_topn(int(top_n_sr))

    sr_df = stable_scope[
        ["batter", "strike_rate", "innings_played", "runs", "balls"]
    ].copy()

    # Apply ranking score (pure KPI or volume-adjusted)
    sr_df = compute_rank_score(sr_df, "strike_rate")

    # ✅ Top N membership always decided by rank_score
    sr_df = (
        sr_df.sort_values("rank_score", ascending=False)
        .head(int(top_n_sr))
        .copy()
    )

    # ✅ Display order (visual sorting)
    if display_order_sr == "Raw strike rate":
        sr_df = sr_df.sort_values("strike_rate", ascending=False).reset_index(drop=True)
    else:
        sr_df = sr_df.sort_values("rank_score", ascending=False).reset_index(drop=True)

    # ✅ FORCE ORDER for Altair using Pandas Categorical
    batter_order = sr_df["batter"].tolist()
    sr_df["batter_ordered"] = pd.Categorical(sr_df["batter"], categories=batter_order, ordered=True)

    base_sr = (
        alt.Chart(sr_df)
        .mark_bar()
        .encode(
            x=alt.X(
                "batter_ordered:N",
                sort=None,
                title="",
                axis=alt.Axis(
                    labelAngle=style_sr["angle"],
                    labelFontSize=style_sr["label_size"],
                ),
            ),
            y=alt.Y("strike_rate:Q", title="Strike Rate"),
            color=alt.value(TAB4_COLORS["purple"]),
            tooltip=[
                alt.Tooltip("batter:N", title="Batter"),
                alt.Tooltip("strike_rate:Q", title="Strike Rate", format=".0f"),
                alt.Tooltip("balls:Q", title="Balls", format=",.0f"),
                alt.Tooltip("innings_played:Q", title="Innings", format=",.0f"),
                alt.Tooltip("runs:Q", title="Runs", format=",.0f"),
                alt.Tooltip("rank_score:Q", title="Ranking Score", format=",.0f"),
            ],
        )
        .properties(height=FIXED_H)
    )

    sr_labels = (
        alt.Chart(sr_df)
        .transform_calculate(y_pos="datum.strike_rate * 0.65")
        .mark_text(color="#1b1b1b", fontSize=style_sr["text_size"])
        .encode(
            x=alt.X(
                "batter_ordered:N",
                sort=None,
                axis=alt.Axis(labelAngle=style_sr["angle"]),
            ),
            y=alt.Y("y_pos:Q"),
            text=alt.Text("strike_rate:Q", format=".0f"),
        )
    )

    st.altair_chart(apply_altair_theme(base_sr + sr_labels), use_container_width=True)
    st.caption("Higher = faster scoring tempo. Use ranking score for stability, raw SR for pure speed.")

st.divider()

# ============================================================
# SECTION 4: Boundaries Profile
# ============================================================

html_section("Boundaries Profile")
html_explain(
    "This section highlights boundary-scoring output and efficiency. "
    "We compare total fours/sixes and how frequently batters find boundaries per ball faced."
)

# -----------------------------
# Local controls (Boundaries Section)
# -----------------------------
c_bnd_1, c_bnd_2 = st.columns([1.2, 3.8])

with c_bnd_1:
    top_n_bnd = st.selectbox(
        "Top Batters",
        [5, 10, 15],
        index=[5, 10, 15].index(int(top_n)),
        key="tab4_sec4_topn_boundaries",
    )

# -----------------------------
# Auto stability threshold (innings)
# -----------------------------
avg_innings_bnd = float(bat_scope["innings_played"].mean())
median_innings_bnd = float(bat_scope["innings_played"].median())
min_innings_threshold_bnd = int(round(median_innings_bnd))

st.caption(
    f"Stability context: Avg innings ≈ {avg_innings_bnd:.0f} | "
    f"Median innings ≈ {median_innings_bnd:.0f} | "
    f"Applying: innings_played ≥ {min_innings_threshold_bnd}"
)

# ============================================================
# ROW 1 (Side-by-side): Total 4s + Balls per 4
# ============================================================

row_bnd_1_left, gap_bnd_1, row_bnd_1_right = st.columns([1, 0.12, 1])
with gap_bnd_1:
    st.markdown("")

# -----------------------------
# Left Chart: Total 4s
# -----------------------------
with row_bnd_1_left:
    st.markdown("### Total Fours (4s)")

    rank_method_fours = st.radio(
        "Ranking Method (Total 4s)",
        ["Pure KPI (Metric only)", "Volume-adjusted (Metric × √balls)"],
        index=1,
        horizontal=True,
        key="tab4_sec4_fours_rank_method",
    )

    fours_df = bat_scope[
        ["batter", "fours", "balls", "innings_played", "runs"]
    ].copy()

    fours_df["fours"] = fours_df["fours"].fillna(0).astype(int)

    # ✅ Stability filter (innings)
    fours_df = fours_df[fours_df["innings_played"] >= min_innings_threshold_bnd].copy()

    if len(fours_df) == 0:
        st.warning(
            "No batters meet the stability threshold for Total 4s in this scope. "
            "Try widening the scope or reducing Min balls faced."
        )
        st.stop()

    # Rank score
    if rank_method_fours.startswith("Pure KPI"):
        fours_df["rank_score"] = fours_df["fours"]
    else:
        fours_df["vol_weight"] = fours_df["balls"] ** 0.5
        fours_df["rank_score"] = fours_df["fours"] * fours_df["vol_weight"]

    # ✅ Membership decided by rank_score
    fours_df = (
        fours_df.sort_values("rank_score", ascending=False)
        .head(int(top_n_bnd))
        .copy()
    )

    # ✅ Visual order by raw KPI
    fours_df = fours_df.sort_values("fours", ascending=False).reset_index(drop=True)
    order_fours = fours_df["batter"].tolist()

    style_fours = chart_style_for_topn(int(top_n_bnd))

    base_fours = (
        alt.Chart(fours_df)
        .mark_bar()
        .encode(
            x=alt.X(
                "batter:N",
                sort=order_fours,
                title="",
                axis=alt.Axis(
                    labelAngle=style_fours["angle"],
                    labelFontSize=style_fours["label_size"],
                ),
            ),
            y=alt.Y("fours:Q", title="Total 4s"),
            color=alt.value(TAB4_COLORS["blue"]),
            tooltip=[
                alt.Tooltip("batter:N", title="Batter"),
                alt.Tooltip("fours:Q", title="Fours", format=",.0f"),
                alt.Tooltip("balls:Q", title="Balls", format=",.0f"),
                alt.Tooltip("innings_played:Q", title="Innings", format=",.0f"),
                alt.Tooltip("runs:Q", title="Runs", format=",.0f"),
                alt.Tooltip("rank_score:Q", title="Ranking Score", format=",.0f"),
            ],
        )
        .properties(height=FIXED_H)
    )

    fours_labels = (
        alt.Chart(fours_df)
        .transform_calculate(y_pos="datum.fours * 0.65")
        .mark_text(color="#1b1b1b", fontSize=style_fours["text_size"])
        .encode(
            x=alt.X(
                "batter:N",
                sort=order_fours,
                axis=alt.Axis(labelAngle=style_fours["angle"]),
            ),
            y=alt.Y("y_pos:Q"),
            text=alt.Text("fours:Q", format=",.0f"),
        )
    )

    st.altair_chart(apply_altair_theme(base_fours + fours_labels), use_container_width=True)
    st.caption("Higher = more boundary scoring via fours in the selected scope.")

# -----------------------------
# Right Chart: Balls per 4
# -----------------------------
with row_bnd_1_right:
    st.markdown("### Balls per 4 (4s Frequency)")

    rank_method_bpf = st.radio(
        "Ranking Method (Balls per 4)",
        ["Pure KPI (Metric only)", "Volume-adjusted (Metric × √balls)"],
        index=1,
        horizontal=True,
        key="tab4_sec4_balls_per_four_rank_method",
    )

    bpf_df = bat_scope[
        ["batter", "fours", "balls", "innings_played", "runs"]
    ].copy()

    bpf_df["fours"] = bpf_df["fours"].fillna(0).astype(int)

    # ✅ Stability filter (innings)
    bpf_df = bpf_df[bpf_df["innings_played"] >= int(min_innings_threshold_bnd)].copy()

    # Avoid divide-by-zero
    bpf_df = bpf_df[bpf_df["fours"] > 0].copy()

    if len(bpf_df) == 0:
        st.warning("No batters have at least 1 four (after innings stability filter) in this scope.")
        st.stop()

    # ✅ Data-driven stability: median balls faced
    median_balls_bpf = int(round(float(bpf_df["balls"].median())))
    min_balls_local = max(int(min_balls), median_balls_bpf)

    # ✅ Extra stability gate: minimum fours
    min_fours_threshold = 10

    bpf_df = bpf_df[bpf_df["balls"] >= int(min_balls_local)].copy()
    bpf_df = bpf_df[bpf_df["fours"] >= int(min_fours_threshold)].copy()

    if len(bpf_df) == 0:
        st.warning(
            "No batters meet the stability filters for Balls per 4 in this scope. "
            "Try widening scope or lowering Min balls faced."
        )
        st.stop()

    # KPI (lower is better)
    bpf_df["balls_per_four"] = (bpf_df["balls"] / bpf_df["fours"]).round(1)

    # Lower is better -> ranking uses negative proxy
    bpf_df["rank_proxy"] = -bpf_df["balls_per_four"]

    if rank_method_bpf.startswith("Pure KPI"):
        bpf_df["rank_score"] = bpf_df["rank_proxy"]
    else:
        bpf_df["vol_weight"] = bpf_df["balls"] ** 0.5
        bpf_df["rank_score"] = bpf_df["rank_proxy"] * bpf_df["vol_weight"]

    # ✅ Membership decided by rank_score
    bpf_df = (
        bpf_df.sort_values("rank_score", ascending=False)
        .head(int(top_n_bnd))
        .copy()
    )

    # ✅ Visual order by KPI (lowest first)
    bpf_df = bpf_df.sort_values("balls_per_four", ascending=True).reset_index(drop=True)
    order_bpf = bpf_df["batter"].tolist()

    style_bpf = chart_style_for_topn(int(top_n_bnd))

    base_bpf = (
        alt.Chart(bpf_df)
        .mark_bar()
        .encode(
            x=alt.X(
                "batter:N",
                sort=order_bpf,
                title="",
                axis=alt.Axis(
                    labelAngle=style_bpf["angle"],
                    labelFontSize=style_bpf["label_size"],
                ),
            ),
            y=alt.Y("balls_per_four:Q", title="Balls per 4"),
            color=alt.value(TAB4_COLORS["blue"]),
            tooltip=[
                alt.Tooltip("batter:N", title="Batter"),
                alt.Tooltip("balls_per_four:Q", title="Balls per 4", format=".1f"),
                alt.Tooltip("fours:Q", title="Total 4s", format=",.0f"),
                alt.Tooltip("balls:Q", title="Balls", format=",.0f"),
                alt.Tooltip("innings_played:Q", title="Innings", format=",.0f"),
                alt.Tooltip("runs:Q", title="Runs", format=",.0f"),
                alt.Tooltip("rank_score:Q", title="Ranking Score", format=",.0f"),
            ],
        )
        .properties(height=FIXED_H)
    )

    bpf_labels = (
        alt.Chart(bpf_df)
        .transform_calculate(y_pos="datum.balls_per_four * 0.65")
        .mark_text(color="#1b1d1b", fontSize=style_bpf["text_size"])
        .encode(
            x=alt.X(
                "batter:N",
                sort=order_bpf,
                axis=alt.Axis(labelAngle=style_bpf["angle"]),
            ),
            y=alt.Y("y_pos:Q"),
            text=alt.Text("balls_per_four:Q", format=".1f"),
        )
    )

    st.altair_chart(apply_altair_theme(base_bpf + bpf_labels), use_container_width=True)
    st.caption("Lower = a four is hit more frequently (faster boundary conversion via 4s).")


# ✅ Full-width explanation (keeps layout clean)
with st.expander("ℹ️ How to interpret Balls per 4 (and why stability filters matter)", expanded=False):
    st.markdown(
        f"""
**What this metric shows**  
**Balls per 4 = Balls faced ÷ Total 4s**  
Lower = the batter hits fours more frequently.

**Why stability filters are important**  
This metric can look artificially strong for batters with small boundary sample sizes.  
To keep the ranking credible, we apply stability checks before selecting the Top N:

- **innings_played ≥ {int(min_innings_threshold_bnd)}**  
- **balls ≥ {int(min_balls_local)}** (data-driven: max(global min balls, median balls = {int(median_balls_bpf)})  
- **total 4s ≥ {int(min_fours_threshold)}**

**Ranking logic**  
- *Pure KPI*: ranks by lowest Balls per 4  
- *Volume-adjusted*: ranks by **(−Balls per 4) × √balls** so efficiency must hold over volume
        """
    )

# ============================================================
# ROW 2 (Side-by-side): Total 6s + Balls per 6
# ============================================================

row_bnd_2_left, gap_bnd_2, row_bnd_2_right = st.columns([1, 0.12, 1])
with gap_bnd_2:
    st.markdown("")

# -----------------------------
# Left Chart: Total 6s
# -----------------------------
with row_bnd_2_left:
    st.markdown("### Total Sixes (6s)")

    rank_method_sixes = st.radio(
        "Ranking Method (Total 6s)",
        ["Pure KPI (Metric only)", "Volume-adjusted (Metric × √balls)"],
        index=1,
        horizontal=True,
        key="tab4_sec4_sixes_rank_method",
    )

    sixes_df = bat_scope[
        ["batter", "sixes", "balls", "innings_played", "runs"]
    ].copy()

    sixes_df["sixes"] = sixes_df["sixes"].fillna(0).astype(int)

    # ✅ Stability filter (innings)
    sixes_df = sixes_df[sixes_df["innings_played"] >= int(min_innings_threshold_bnd)].copy()

    if len(sixes_df) == 0:
        st.warning(
            "No batters meet the stability threshold for Total 6s in this scope. "
            "Try widening scope or reducing Min balls faced."
        )
        st.stop()

    # Rank score
    if rank_method_sixes.startswith("Pure KPI"):
        sixes_df["rank_score"] = sixes_df["sixes"]
    else:
        sixes_df["vol_weight"] = sixes_df["balls"] ** 0.5
        sixes_df["rank_score"] = sixes_df["sixes"] * sixes_df["vol_weight"]

    # ✅ Membership decided by rank_score
    sixes_df = (
        sixes_df.sort_values("rank_score", ascending=False)
        .head(int(top_n_bnd))
        .copy()
    )

    # ✅ Visual order by raw KPI
    sixes_df = sixes_df.sort_values("sixes", ascending=False).reset_index(drop=True)
    order_sixes = sixes_df["batter"].tolist()

    style_sixes = chart_style_for_topn(int(top_n_bnd))

    base_sixes = (
        alt.Chart(sixes_df)
        .mark_bar()
        .encode(
            x=alt.X(
                "batter:N",
                sort=order_sixes,
                title="",
                axis=alt.Axis(
                    labelAngle=style_sixes["angle"],
                    labelFontSize=style_sixes["label_size"],
                ),
            ),
            y=alt.Y("sixes:Q", title="Total 6s"),
            color=alt.value(TAB4_COLORS["slate"]),
            tooltip=[
                alt.Tooltip("batter:N", title="Batter"),
                alt.Tooltip("sixes:Q", title="Sixes", format=",.0f"),
                alt.Tooltip("balls:Q", title="Balls", format=",.0f"),
                alt.Tooltip("innings_played:Q", title="Innings", format=",.0f"),
                alt.Tooltip("runs:Q", title="Runs", format=",.0f"),
                alt.Tooltip("rank_score:Q", title="Ranking Score", format=",.0f"),
            ],
        )
        .properties(height=FIXED_H)
    )

    sixes_labels = (
        alt.Chart(sixes_df)
        .transform_calculate(y_pos="datum.sixes * 0.65")
        .mark_text(color="#1b1b1b", fontSize=style_sixes["text_size"])
        .encode(
            x=alt.X(
                "batter:N",
                sort=order_sixes,
                axis=alt.Axis(labelAngle=style_sixes["angle"]),
            ),
            y=alt.Y("y_pos:Q"),
            text=alt.Text("sixes:Q", format=",.0f"),
        )
    )

    st.altair_chart(apply_altair_theme(base_sixes + sixes_labels), use_container_width=True)
    st.caption("Higher = more power scoring via sixes in the selected scope.")


# -----------------------------
# Right Chart: Balls per 6
# -----------------------------
with row_bnd_2_right:
    st.markdown("### Balls per 6 (6s Frequency)")

    rank_method_bps = st.radio(
        "Ranking Method (Balls per 6)",
        ["Pure KPI (Metric only)", "Volume-adjusted (Metric × √balls)"],
        index=1,
        horizontal=True,
        key="tab4_sec4_balls_per_six_rank_method",
    )

    bps_df = bat_scope[
        ["batter", "sixes", "balls", "innings_played", "runs"]
    ].copy()

    bps_df["sixes"] = bps_df["sixes"].fillna(0).astype(int)

    # ✅ Stability filter (innings)
    bps_df = bps_df[bps_df["innings_played"] >= int(min_innings_threshold_bnd)].copy()

    # Avoid divide-by-zero
    bps_df = bps_df[bps_df["sixes"] > 0].copy()

    if len(bps_df) == 0:
        st.warning("No batters have at least 1 six (after innings stability filter) in this scope.")
        st.stop()

    # ✅ Data-driven stability: median balls faced
    median_balls_bps = int(round(float(bps_df["balls"].median())))
    min_balls_local_six = max(int(min_balls), median_balls_bps)

    # ✅ Extra stability gate: minimum sixes
    min_sixes_threshold = 5

    bps_df = bps_df[bps_df["balls"] >= int(min_balls_local_six)].copy()
    bps_df = bps_df[bps_df["sixes"] >= int(min_sixes_threshold)].copy()

    if len(bps_df) == 0:
        st.warning("No batters meet the stability filters for Balls per 6 in this scope.")
        st.stop()

    # KPI (lower is better)
    bps_df["balls_per_six"] = (bps_df["balls"] / bps_df["sixes"]).round(1)

    # Lower is better -> ranking uses negative proxy
    bps_df["rank_proxy"] = -bps_df["balls_per_six"]

    if rank_method_bps.startswith("Pure KPI"):
        bps_df["rank_score"] = bps_df["rank_proxy"]
    else:
        bps_df["vol_weight"] = bps_df["balls"] ** 0.5
        bps_df["rank_score"] = bps_df["rank_proxy"] * bps_df["vol_weight"]

    # ✅ Membership decided by rank_score
    bps_df = (
        bps_df.sort_values("rank_score", ascending=False)
        .head(int(top_n_bnd))
        .copy()
    )

    # ✅ Visual order by KPI (lowest first)
    bps_df = bps_df.sort_values("balls_per_six", ascending=True).reset_index(drop=True)
    order_bps = bps_df["batter"].tolist()

    style_bps = chart_style_for_topn(int(top_n_bnd))

    base_bps = (
        alt.Chart(bps_df)
        .mark_bar()
        .encode(
            x=alt.X(
                "batter:N",
                sort=order_bps,
                title="",
                axis=alt.Axis(
                    labelAngle=style_bps["angle"],
                    labelFontSize=style_bps["label_size"],
                ),
            ),
            y=alt.Y("balls_per_six:Q", title="Balls per 6"),
            color=alt.value(TAB4_COLORS["slate"]),
            tooltip=[
                alt.Tooltip("batter:N", title="Batter"),
                alt.Tooltip("balls_per_six:Q", title="Balls per 6", format=".1f"),
                alt.Tooltip("sixes:Q", title="Total 6s", format=",.0f"),
                alt.Tooltip("balls:Q", title="Balls", format=",.0f"),
                alt.Tooltip("innings_played:Q", title="Innings", format=",.0f"),
                alt.Tooltip("runs:Q", title="Runs", format=",.0f"),
                alt.Tooltip("rank_score:Q", title="Ranking Score", format=",.0f"),
            ],
        )
        .properties(height=FIXED_H)
    )

    bps_labels = (
        alt.Chart(bps_df)
        .transform_calculate(y_pos="datum.balls_per_six * 0.65")
        .mark_text(color="#1b1b1b", fontSize=style_bps["text_size"])
        .encode(
            x=alt.X(
                "batter:N",
                sort=order_bps,
                axis=alt.Axis(labelAngle=style_bps["angle"]),
            ),
            y=alt.Y("y_pos:Q"),
            text=alt.Text("balls_per_six:Q", format=".1f"),
        )
    )

    st.altair_chart(apply_altair_theme(base_bps + bps_labels), use_container_width=True)
    st.caption("Lower = a six is hit more frequently (faster power conversion via 6s).")


# ✅ Full-width explanation (keeps side-by-side alignment clean)
with st.expander("ℹ️ How to interpret Balls per 6 (and why stability filters matter)", expanded=False):
    st.markdown(
        f"""
**What this metric shows**  
**Balls per 6 = Balls faced ÷ Total 6s**  
Lower = the batter hits sixes more frequently.

**Why stability filters are important**  
This metric can be noisy in small samples. To keep rankings meaningful, we apply:

- **innings_played ≥ {int(min_innings_threshold_bnd)}**
- **balls ≥ {int(min_balls_local_six)}** (data-driven: max(global min balls, median balls = {int(median_balls_bps)})
- **total 6s ≥ {int(min_sixes_threshold)}**

**Ranking logic**  
- *Pure KPI*: ranks by lowest Balls per 6  
- *Volume-adjusted*: ranks by **(−Balls per 6) × √balls**
        """
    )

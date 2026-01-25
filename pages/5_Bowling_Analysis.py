import streamlit as st
import altair as alt
import pandas as pd
import numpy as np

import src.data_loader as dl


# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="Bowling Analysis", page_icon="🎯", layout="wide")


# -----------------------------
# COLORS (same as Tab 3/Tab 4)
# -----------------------------
LIGHT_RAINBOW = [
    "#6EE7B7",  # mint
    "#93C5FD",  # light blue
    "#FCD34D",  # warm yellow
    "#F9A8D4",  # soft pink
    "#A5B4FC",  # light indigo
    "#FDBA74",  # soft orange
    "#D8B4FE",  # soft purple
    "#7DD3FC",  # sky
    "#BEF264",  # lime
    "#FDA4AF",  # soft red
]

PASTEL_GREEN = "#6EE7B7"
PASTEL_RED = "#FDA4AF"
PASTEL_BLUE = "#93C5FD"
PASTEL_ORANGE = "#FDBA74"
PASTEL_PURPLE = "#D8B4FE"

KPI_BLUE = "#2563EB"
KPI_PURPLE = "#7C3AED"
KPI_DARK = "#111827"
KPI_ORANGE = "#F59E0B"
KPI_GREEN = "#16A34A"
KPI_RED = "#DC2626"


# -----------------------------
# KPI CARD (same component style)
# -----------------------------
def kpi_card(label, value, emoji="✅", value_color="#111", desc=""):
    desc_html = ""
    if desc:
        desc_html = f"""
        <div style="margin-top: 6px; font-size: 0.82rem; opacity: 0.70; line-height: 1.2;">
            {desc}
        </div>
        """

    st.markdown(
        f"""
        <div style="
            background: rgba(255,255,255,0.75);
            border: 1px solid rgba(0,0,0,0.06);
            border-radius: 18px;
            padding: 16px 16px 14px 16px;
            box-shadow: 0 8px 22px rgba(0,0,0,0.06);
            height: 124px;
        ">
            <div style="font-size: 1.60rem; font-weight: 850; line-height: 1; color:{value_color};">
                {value}
            </div>
            <div style="margin-top: 8px; font-size: 0.95rem; opacity: 0.78;">
                {emoji} {label}
            </div>
            {desc_html}
        </div>
        """,
        unsafe_allow_html=True
    )


# -----------------------------
# PAGE HEADER
# -----------------------------
st.markdown(
    """
    <div style="padding: 0.2rem 0 0.8rem 0;">
        <div style="font-size: 2.1rem; font-weight: 800;">🎯 Bowling Analysis</div>
        <div style="font-size: 1.05rem; opacity: 0.85;">
            KPI-first bowling performance with stability gates + experience buckets.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# -----------------------------
# LOAD DATA (masters only)
# -----------------------------
matches = dl.load_master_matches()
balls = dl.load_master_balls()

# baseline: remove super overs for standard analysis
balls = balls[balls["is_super_over"] == False].copy()


# -----------------------------
# Build base bowling dataset (minimal columns + flags)
# -----------------------------
df = balls.copy()

# ✅ locked rules
df["is_wide_ball"] = df["is_wide_ball"].fillna(False).astype(bool)
df["is_no_ball"] = df["is_no_ball"].fillna(False).astype(bool)

# wides are not legal deliveries
df["is_legal_ball"] = (~df["is_wide_ball"]).astype(int)

# bowler runs conceded = batter runs + wides + no-balls
# (byes/legbyes are already excluded in your baseline runs model)
df["wide_ball_runs"] = df["wide_ball_runs"].fillna(0).astype(int)
df["no_ball_runs"] = df["no_ball_runs"].fillna(0).astype(int)
df["batter_runs"] = df["batter_runs"].fillna(0).astype(int)

df["bowler_runs_conceded"] = df["batter_runs"] + df["wide_ball_runs"] + df["no_ball_runs"]

# dot balls (legal only)
df["is_dot_ball"] = ((df["batter_runs"] == 0) & (df["is_legal_ball"] == 1)).astype(int)

# boundary flags (legal only)
df["is_four"] = ((df["batter_runs"] == 4) & (df["is_legal_ball"] == 1)).astype(int)
df["is_six"] = ((df["batter_runs"] == 6) & (df["is_legal_ball"] == 1)).astype(int)

# bowler wickets (exclude run-outs etc)
# if wicket_kind is null => no wicket
# if wicket_kind in ["run out", "retired hurt", "obstructing the field"] => not bowler wicket
df["wicket_kind"] = df["wicket_kind"].astype("string")
df["is_wicket"] = df["is_wicket"].fillna(False).astype(bool)

NOT_BOWLER_WKTS = {"run out", "retired hurt", "obstructing the field"}

df["is_bowler_wicket"] = (
    (df["is_wicket"] == True) &
    (~df["wicket_kind"].str.lower().isin(NOT_BOWLER_WKTS))
).astype(int)

base = df[[
    "match_id", "season_id", "match_date", "venue", "venue_region",
    "innings", "team_bowling", "bowler",
    "over_number", "ball_number",
    "is_legal_ball",
    "bowler_runs_conceded",
    "is_bowler_wicket",
    "is_dot_ball",
    "is_four", "is_six",
    "is_wide_ball", "wide_ball_runs",
    "is_no_ball", "no_ball_runs"
]].copy()


# -----------------------------
# FILTERS (Region -> Season -> Top N)
# -----------------------------
c1, c2, c3 = st.columns([1.3, 1.1, 1.1], gap="large")

with c1:
    region = st.selectbox(
        "🌍 Region",
        options=["All"] + sorted(base["venue_region"].dropna().unique().tolist()),
        index=0
    )

base_f = base.copy()
if region != "All":
    base_f = base_f[base_f["venue_region"] == region]

with c2:
    season = st.selectbox(
        "📅 Season",
        options=["All"] + sorted(base_f["season_id"].dropna().unique().tolist()),
        index=0
    )

if season != "All":
    base_f = base_f[base_f["season_id"] == int(season)]

with c3:
    top_n = st.selectbox("🎯 Show Top", [5, 10], index=0)  # ✅ default Top 5



# -----------------------------
# SCOPE BADGE
# -----------------------------
st.markdown(
    f"""
    <div style="margin: 6px 0 14px 0;">
        <span style="
            display:inline-block;
            padding: 6px 10px;
            border-radius: 999px;
            border: 1px solid rgba(0,0,0,0.06);
            background: rgba(0,0,0,0.03);
            font-size: 0.9rem;
            opacity: 0.9;">
            📌 Showing: <b>{region}</b> · <b>{season}</b> · <b>Top {top_n}</b>
        </span>
    </div>
    """,
    unsafe_allow_html=True
)



# =========================
# SECTION 1: FUNDAMENTALS
# =========================
st.markdown("## 🧱 Fundamentals")
st.caption("Quick snapshot of bowling efficiency and control in the selected scope (stability gated).")

# -------------------------
# Pack (bowler summary)
# -------------------------
MIN_LEGAL_BALLS = 300
MIN_WKTS = 15

pack = (
    base_f.groupby("bowler", as_index=False)
          .agg(
              matches=("match_id", "nunique"),
              legal_balls=("is_legal_ball", "sum"),
              overs=("is_legal_ball", lambda x: x.sum() / 6),
              runs=("bowler_runs_conceded", "sum"),
              wkts=("is_bowler_wicket", "sum"),
              dots=("is_dot_ball", "sum"),
              fours=("is_four", "sum"),
              sixes=("is_six", "sum"),
              wide_runs=("wide_ball_runs", "sum"),
              noball_runs=("no_ball_runs", "sum"),
          )
)

pack["econ"] = pack["runs"] / pack["overs"]
pack["avg"] = np.where(pack["wkts"] > 0, pack["runs"] / pack["wkts"], np.nan)
pack["sr"] = np.where(pack["wkts"] > 0, pack["legal_balls"] / pack["wkts"], np.nan)
pack["dot_pct"] = np.where(pack["legal_balls"] > 0, (pack["dots"] / pack["legal_balls"]) * 100, np.nan)

def add_exp_bucket(m):
    if m <= 25:
        return "1–25"
    if m <= 50:
        return "26–50"
    if m <= 75:
        return "51–75"
    return "75+"

pack["exp_bucket"] = pack["matches"].apply(add_exp_bucket)

# Stability gates
pack_gated = pack[pack["legal_balls"] >= MIN_LEGAL_BALLS].copy()
pack_avg_sr = pack[(pack["legal_balls"] >= MIN_LEGAL_BALLS) & (pack["wkts"] >= MIN_WKTS)].copy()

# -------------------------
# KPI cards
# -------------------------
k1, k2, k3, k4 = st.columns(4, gap="large")

kpi_econ = pack_gated["econ"].mean() if len(pack_gated) else 0
kpi_avg = pack_avg_sr["avg"].mean() if len(pack_avg_sr) else 0
kpi_sr = pack_avg_sr["sr"].mean() if len(pack_avg_sr) else 0
kpi_dot = pack_gated["dot_pct"].mean() if len(pack_gated) else 0

with k1:
    kpi_card("ECON (runs/over)", f"{kpi_econ:.2f}", "💸", KPI_BLUE, desc="Lower is better")
with k2:
    kpi_card("Bowling AVG", f"{kpi_avg:.2f}", "🎯", KPI_GREEN, desc="Runs per wicket (lower is better)")
with k3:
    kpi_card("Strike Rate (SR)", f"{kpi_sr:.2f}", "⚡", KPI_ORANGE, desc="Balls per wicket (lower is better)")
with k4:
    kpi_card("Dot Ball %", f"{kpi_dot:.1f}%", "🧱", KPI_RED, desc="More dots = more pressure")


# -------------------------
# Best Economy chart — Pastel multi-color
# -------------------------
st.markdown(f"### 🌟 Top Wicket Takers (Top {top_n})")
st.caption(f"Stability gate: min legal balls = {MIN_LEGAL_BALLS}")

wkts_df = (
    pack_gated.sort_values(["wkts", "legal_balls"], ascending=[False, False])
             .head(top_n)
             .copy()
)



bars = (
    alt.Chart(wkts_df)
    .mark_bar()
    .encode(
        x=alt.X("wkts:Q", title="Wickets"),
        y=alt.Y("bowler:N", sort="-x", title="Bowler"),
        color=alt.Color(
            "bowler:N",
            scale=alt.Scale(range=LIGHT_RAINBOW),
            legend=None
        ),
        tooltip=[
            "bowler",
            "exp_bucket",
            "matches",
            "overs",
            alt.Tooltip("wkts:Q", title="Wkts"),
            alt.Tooltip("econ:Q", format=".2f", title="ECON"),
            alt.Tooltip("dot_pct:Q", format=".1f", title="Dot%"),
        ],
    )
)

labels = (
    alt.Chart(wkts_df)
    .mark_text(align="left", dx=4)
    .encode(
        x="wkts:Q",
        y=alt.Y("bowler:N", sort="-x"),
        text=alt.Text("wkts:Q"),
    )
)

wkts_chart = (bars + labels).properties(height=360)

# LOCKED RULE: layer first -> then configure
wkts_chart = wkts_chart.configure_axis(labelFontSize=12, titleFontSize=12).configure_title(fontSize=16)

st.altair_chart(wkts_chart, use_container_width=True)

# -----------------------------
# SECTION 1 EXPLAINER (dropdown)
# -----------------------------
with st.expander("📘 How to read this section (stability logic + KPI meaning)", expanded=False):
    st.markdown(
        f"""
### What this section shows
A quick snapshot of **bowling efficiency + control** in the selected scope (**{region} · {season}**).  
Leaderboards are **stability gated**, so rankings don’t get distorted by tiny samples.

---

## ✅ Fundamentals KPIs (what they mean)

**ECON (Economy Rate)**  
Runs conceded per over (lower = better).  
Formula: *(Runs Conceded / Overs)*

**AVG (Bowling Average)**  
Runs conceded per wicket (lower = better).  
Formula: *(Runs Conceded / Wickets)*  
Only meaningful when wicket count is stable.

**SR (Strike Rate)**  
Balls per wicket (lower = better).  
Formula: *(Legal Balls / Wickets)*

**Dot %**  
% of legal balls that are dot balls (higher = better).  
Formula: *(Dot Balls / Legal Balls) × 100*

---

## 🎯 Leaderboard: Most Wickets (Top {top_n})
This chart ranks bowlers by **total wickets taken** in the selected scope.  
We use this because wickets = direct match impact.

Tie-breaker logic:  
- If wickets are equal → higher **legal balls** ranks higher (more sustained contribution)

---

## ✅ Stability gates (LOCKED)
To avoid “small sample” noise, we apply:

**Wickets leaderboard gate**
- Minimum **{MIN_LEGAL_BALLS} legal balls** bowled

✅ Why this matters:  
A bowler with 6 wickets in 2 matches can look elite, but isn’t a stable comparison.

---

## Notes (dataset rules)
- **Legal balls** exclude wides  
- **Wickets credited to bowler** exclude run outs (and other non-bowler dismissals)
- **Dot balls** are counted only on **legal deliveries**

        """
    )

# =========================================================
# SECTION 2: PRESSURE & BOUNDARIES (Matches played filter)
# =========================================================
st.markdown("## 🧱 Pressure & Boundaries")
st.caption("Dot balls show control. Boundaries conceded show damage. Ranked with experience buckets + stability gated pack.")

# -----------------------------
# Controls (Rank by + Matches played)
# -----------------------------
c1, c2 = st.columns([1.2, 1.3], gap="large")

with c1:
    rank_metric = st.selectbox(
        "📌 Rank by",
        ["Dot Ball % ↑", "Boundary % Conceded ↓"],
        index=0,
        key="pb_rank_metric"
    )

with c2:
    exp_bucket = st.selectbox(
        "🎯 Matches played",
        [
            "All (all experience levels)",
            "1–25 (small sample)",
            "26–50 (emerging core)",
            "51–75 (proven regulars)",
            "75+ (elite longevity)",
        ],
        index=0,
        key="pb_exp_bucket"
    )

# -----------------------------
# Pack for this section
# Using pack_gated (199 rows) so Dot%/Boundary% are stable by default
# -----------------------------
pack_pb = pack_gated.copy()

# Map exp_bucket selection to actual value in data
exp_map = {
    "All (all experience levels)": "All",
    "1–25 (small sample)": "1–25",
    "26–50 (emerging core)": "26–50",
    "51–75 (proven regulars)": "51–75",
    "75+ (elite longevity)": "75+",
}

exp_choice = exp_map.get(exp_bucket, "All")

if exp_choice != "All":
    pack_pb = pack_pb[pack_pb["exp_bucket"] == exp_choice].copy()

# -----------------------------
# Ensure required columns exist
# -----------------------------
# Dot%
if "dot_pct" not in pack_pb.columns:
    pack_pb["dot_pct"] = np.where(
        pack_pb["legal_balls"] > 0,
        (pack_pb["dots"] / pack_pb["legal_balls"]) * 100,
        0
    )

# Boundary%
if "boundary_pct" not in pack_pb.columns:
    pack_pb["boundary_balls"] = pack_pb["fours"].fillna(0) + pack_pb["sixes"].fillna(0)
    pack_pb["boundary_pct"] = np.where(
        pack_pb["legal_balls"] > 0,
        (pack_pb["boundary_balls"] / pack_pb["legal_balls"]) * 100,
        0
    )

# -----------------------------
# Metric logic (your arrows)
# Dot Ball % ↑  => higher is better => DESC
# Boundary % ↓  => lower is better  => ASC
# -----------------------------
if rank_metric == "Dot Ball % ↑":
    metric_col = "dot_pct"
    metric_title = "Dot Ball %"
    x_title = "Dot Ball % (Higher is better)"
    sort_asc = False
    fmt = ".1f"
else:
    metric_col = "boundary_pct"
    metric_title = "Boundary % Conceded"
    x_title = "Boundary % Conceded (Lower is better)"
    sort_asc = True
    fmt = ".2f"

# -----------------------------
# Top N (uses top_n from page dropdown)
# -----------------------------
plot_df = (
    pack_pb.sort_values(metric_col, ascending=sort_asc)
          .head(top_n)
          .copy()
)

# lock order for Altair
plot_df["bowler_order"] = plot_df["bowler"]

# -----------------------------
# Chart
# -----------------------------
bars = (
    alt.Chart(plot_df)
    .mark_bar(cornerRadiusEnd=6)
    .encode(
        y=alt.Y("bowler_order:N", sort=None, title=""),
        x=alt.X(f"{metric_col}:Q", title=x_title),
        color=alt.Color(
            "bowler_order:N",
            scale=alt.Scale(range=LIGHT_RAINBOW),
            legend=None
        ),
        tooltip=[
            alt.Tooltip("bowler:N", title="Bowler"),
            alt.Tooltip("exp_bucket:N", title="Matches bucket"),
            alt.Tooltip("matches:Q", title="Matches"),
            alt.Tooltip("overs:Q", title="Overs", format=".1f"),
            alt.Tooltip("wkts:Q", title="Wkts"),
            alt.Tooltip("econ:Q", title="ECON", format=".2f"),
            alt.Tooltip("dot_pct:Q", title="Dot%", format=".1f"),
            alt.Tooltip("boundary_pct:Q", title="Boundary%", format=".2f"),
        ]
    )
)

labels = (
    alt.Chart(plot_df)
    .mark_text(align="left", dx=6, fontSize=12)
    .encode(
        y=alt.Y("bowler_order:N", sort=None),
        x=alt.X(f"{metric_col}:Q"),
        text=alt.Text(f"{metric_col}:Q", format=fmt),
    )
)

pb_chart = (bars + labels).properties(
    height=380,
    title=f"{metric_title} Leaders (Top {top_n})"
)

pb_chart = pb_chart.configure_axis(
    labelFontSize=12,
    titleFontSize=12
).configure_title(
    fontSize=16
)

st.altair_chart(pb_chart, use_container_width=True)

# -----------------------------
# Explanation dropdown (like Batting)
# -----------------------------
with st.expander("🧠 How to read this section", expanded=False):
    st.markdown(
        """
### What this section shows
This leaderboard highlights **bowling control vs damage**:

✅ **Dot Ball % ↑ (higher is better)**  
More dots = more pressure & better control.

✅ **Boundary % Conceded ↓ (lower is better)**  
Lower boundary frequency = fewer easy runs allowed.

### Why the “Matches played” filter exists
- **All** = includes everyone who passes stability gates  
- **75+** = elite longevity only (most reliable comparisons)  
- Lower buckets help find emerging specialists.
        """
    )

st.divider()

# ============================================================
# COMBINED SECTION: Phase Specialists (Powerplay / Middle / Death)
# ============================================================

st.markdown("## ⏱️ Phase Specialists")
st.caption("One combined leaderboard for Powerplay / Middle / Death with stable KPI-first ranking logic.")

# -----------------------------
# Phase mapping (LOCKED)
# -----------------------------
# over_number is 0-based:
# Powerplay = 0–5, Middle = 6–14, Death = 15–19
phase_df = base_f[base_f["is_legal_ball"] == 1].copy()

phase_df["phase"] = np.select(
    [
        phase_df["over_number"].between(0, 5),
        phase_df["over_number"].between(6, 14),
        phase_df["over_number"].between(15, 19),
    ],
    ["Powerplay", "Middle", "Death"],
    default="Other"
)

phase_df = phase_df[phase_df["phase"] != "Other"].copy()

# -----------------------------
# Pack: bowler x phase
# -----------------------------
phase_pack = (
    phase_df.groupby(["phase", "bowler"], as_index=False)
    .agg(
        matches=("match_id", "nunique"),
        legal_balls=("is_legal_ball", "sum"),
        runs=("bowler_runs_conceded", "sum"),
        wkts=("is_bowler_wicket", "sum"),
        dots=("is_dot_ball", "sum"),
    )
)

phase_pack["overs"] = phase_pack["legal_balls"] / 6
phase_pack["econ"] = np.where(phase_pack["overs"] > 0, phase_pack["runs"] / phase_pack["overs"], np.nan)
phase_pack["dot_pct"] = np.where(phase_pack["legal_balls"] > 0, (phase_pack["dots"] / phase_pack["legal_balls"]) * 100, np.nan)

# Experience bucket (same as Section 1)
phase_pack["exp_bucket"] = phase_pack["matches"].apply(add_exp_bucket)

# -----------------------------
# Stability gate (LOCKED)
# -----------------------------
MIN_PHASE_BALLS = 120
phase_gated = phase_pack[phase_pack["legal_balls"] >= MIN_PHASE_BALLS].copy()

# -----------------------------
# Controls (3 dropdowns side-by-side)
# -----------------------------
c1, c2, c3 = st.columns([1.2, 1.3, 1.3], gap="large")

with c1:
    phase_choice = st.selectbox(
        "⏱️ Phase Controllers",
        options=["Powerplay", "Middle", "Death"],
        index=0,
        key="combined_phase_choice"
    )

with c2:
    phase_rank_metric = st.selectbox(
        "📌 Rank by",
        options=[
            "Best Economy ↓",
            "Most Wickets ↑",
            "Dot Ball % ↑",
        ],
        index=0,
        key="combined_phase_rank"
    )

with c3:
    phase_exp_bucket = st.selectbox(
        "🌀 Matches played",
        options=[
            "All (all experience levels)",
            "1–25 (small sample)",
            "26–50 (emerging core)",
            "51–75 (proven regulars)",
            "75+ (elite longevity)",
        ],
        index=0,
        key="combined_phase_exp"
    )

bucket_map = {
    "All (all experience levels)": "All",
    "1–25 (small sample)": "1–25",
    "26–50 (emerging core)": "26–50",
    "51–75 (proven regulars)": "51–75",
    "75+ (elite longevity)": "75+",
}
bucket_clean = bucket_map[phase_exp_bucket]

# -----------------------------
# Filter dataset by phase + bucket
# -----------------------------
plot_phase = phase_gated[phase_gated["phase"] == phase_choice].copy()

if bucket_clean != "All":
    plot_phase = plot_phase[plot_phase["exp_bucket"] == bucket_clean].copy()

# -----------------------------
# Metric logic (LOCKED)
# -----------------------------
metric_map = {
    "Best Economy ↓": ("econ", True, "Economy (Lower is better)", ".2f"),
    "Most Wickets ↑": ("wkts", False, "Wickets (Higher is better)", ".0f"),
    "Dot Ball % ↑": ("dot_pct", False, "Dot Ball % (Higher is better)", ".1f"),
}

metric_col, sort_asc, x_title, label_fmt = metric_map[phase_rank_metric]

# -----------------------------
# Rank + Top N (uses main page dropdown top_n)
# IMPORTANT: enforce y-order so chart shows correctly
# -----------------------------
plot_phase = plot_phase.dropna(subset=[metric_col]).copy()
plot_phase = plot_phase.sort_values(metric_col, ascending=sort_asc).head(int(top_n)).copy()

if len(plot_phase) == 0:
    st.warning("No bowlers match this phase + experience bucket + stability gate.")
else:
    y_order = plot_phase["bowler"].tolist()
    plot_phase["rank"] = range(1, len(plot_phase) + 1)

    bars = (
        alt.Chart(plot_phase)
        .mark_bar(cornerRadiusEnd=6)
        .encode(
            y=alt.Y("bowler:N", sort=y_order, title=None, axis=alt.Axis(labelLimit=300)),
            x=alt.X(f"{metric_col}:Q", title=x_title),
            color=alt.Color("rank:O", scale=alt.Scale(range=LIGHT_RAINBOW), legend=None),
            tooltip=[
                "bowler:N",
                alt.Tooltip("phase:N", title="Phase"),
                alt.Tooltip("exp_bucket:N", title="Matches bucket"),
                alt.Tooltip("matches:Q", title="Matches"),
                alt.Tooltip("overs:Q", title="Overs", format=".1f"),
                alt.Tooltip("wkts:Q", title="Wkts"),
                alt.Tooltip("econ:Q", title="ECON", format=".2f"),
                alt.Tooltip("dot_pct:Q", title="Dot%", format=".1f"),
            ]
        )
        .properties(height=360)
    )

    labels = (
        alt.Chart(plot_phase)
        .mark_text(align="left", dx=6, fontSize=14)
        .encode(
            y=alt.Y("bowler:N", sort=y_order),
            x=alt.X(f"{metric_col}:Q"),
            text=alt.Text(f"{metric_col}:Q", format=label_fmt),
        )
    )

    chart_phase = (bars + labels)
    chart_phase = chart_phase.configure_view(strokeOpacity=0).configure_axisY(labelPadding=12)

    st.altair_chart(chart_phase, use_container_width=True)

with st.expander("🧠 How to read this section", expanded=False):
    st.markdown(
        f"""
### What this section shows
A single phase leaderboard that highlights **specialists in specific match windows**:

- **Powerplay (Overs 1–6)** → early control + breakthroughs  
- **Middle (Overs 7–15)** → containment + pressure  
- **Death (Overs 16–20)** → execution under maximum risk  

### Ranking rules
✅ **Best Economy ↓** → lower ranks higher  
✅ **Most Wickets ↑** → higher ranks higher  
✅ **Dot Ball % ↑** → higher ranks higher  

### Stability gate (LOCKED)
Minimum **{MIN_PHASE_BALLS} legal balls in the selected phase**.
        """
    )

st.divider()


# ============================================================
# SECTION 5: Match-winning Spells (3W / 4W Hauls)
# ============================================================

st.markdown("## 🧨 Match-winning Spells")
st.caption("Bowlers who deliver game-changing wicket bursts (3W/4W hauls). Stability gated.")

# -----------------------------
# Controls (Rank by + Matches played)
# -----------------------------
c1, c2 = st.columns([1.6, 1.3], gap="large")

with c1:
    s5_metric = st.selectbox(
        "📌 Rank by",
        options=[
            "3W Hauls ↑",
            "4W Hauls ↑",
        ],
        index=0,
        key="s5_rank_metric"
    )

with c2:
    s5_exp_bucket = st.selectbox(
        "🌀 Matches played",
        options=[
            "All (all experience levels)",
            "1–25 (small sample)",
            "26–50 (emerging core)",
            "51–75 (proven regulars)",
            "75+ (elite longevity)",
        ],
        index=0,
        key="s5_exp_bucket"
    )

bucket_map = {
    "All (all experience levels)": "All",
    "1–25 (small sample)": "1–25",
    "26–50 (emerging core)": "26–50",
    "51–75 (proven regulars)": "51–75",
    "75+ (elite longevity)": "75+",
}
s5_bucket_clean = bucket_map[s5_exp_bucket]

# -----------------------------
# Build innings-level wicket bursts from ball-level data
# (base_f already filtered by Region + Season)
# -----------------------------
innings_wkts = (
    base_f.groupby(["match_id", "innings", "bowler"], as_index=False)
          .agg(
              wkts=("is_bowler_wicket", "sum"),
              legal_balls=("is_legal_ball", "sum"),
          )
)

# Stability: bowler must have enough total legal balls across scope
bowler_balls = (
    innings_wkts.groupby("bowler", as_index=False)
                .agg(total_legal_balls=("legal_balls", "sum"))
)

stable_bowlers = set(
    bowler_balls[bowler_balls["total_legal_balls"] >= MIN_LEGAL_BALLS]["bowler"].tolist()
)

innings_wkts = innings_wkts[innings_wkts["bowler"].isin(stable_bowlers)].copy()

# -----------------------------
# Convert to bowler-level haul counts
# -----------------------------
s5 = (
    innings_wkts.groupby("bowler", as_index=False)
                .agg(
                    inns=("match_id", "count"),
                    inns_3w=("wkts", lambda x: int((x >= 3).sum())),
                    inns_4w=("wkts", lambda x: int((x >= 4).sum())),
                )
)

# add matches + exp_bucket using your existing pack (best source)
s5 = s5.merge(pack[["bowler", "matches", "exp_bucket"]], on="bowler", how="left")

# Apply experience bucket filter
if s5_bucket_clean != "All":
    s5 = s5[s5["exp_bucket"] == s5_bucket_clean].copy()

# -----------------------------
# Metric logic (both are higher = better)
# -----------------------------
if s5_metric == "3W Hauls ↑":
    metric_col = "inns_3w"
    metric_title = "3W Hauls"
else:
    metric_col = "inns_4w"
    metric_title = "4W Hauls"

s5_sorted = (
    s5.sort_values([metric_col, "inns"], ascending=[False, False])
      .head(int(top_n))
      .copy()
)

# Force y-order to match sorted df
y_order = s5_sorted["bowler"].tolist()
s5_sorted["rank"] = range(1, len(s5_sorted) + 1)

# -----------------------------
# Chart
# -----------------------------
bars = (
    alt.Chart(s5_sorted)
    .mark_bar(cornerRadiusEnd=6)
    .encode(
        y=alt.Y("bowler:N", sort=y_order, title=None, axis=alt.Axis(labelLimit=240)),
        x=alt.X(f"{metric_col}:Q", title=f"{metric_title} (Higher is better)"),
        color=alt.Color("rank:O", scale=alt.Scale(range=LIGHT_RAINBOW), legend=None),
        tooltip=[
            alt.Tooltip("bowler:N", title="Bowler"),
            alt.Tooltip("matches:Q", title="Matches"),
            alt.Tooltip("exp_bucket:N", title="Matches bucket"),
            alt.Tooltip("inns:Q", title="Innings bowled"),
            alt.Tooltip("inns_3w:Q", title="3W inns"),
            alt.Tooltip("inns_4w:Q", title="4W inns"),
        ]
    )
    .properties(height=360)
)

labels = (
    alt.Chart(s5_sorted)
    .mark_text(align="left", dx=6, fontSize=14, fontWeight=700, color="#111827")
    .encode(
        y=alt.Y("bowler:N", sort=y_order),
        x=alt.X(f"{metric_col}:Q"),
        text=alt.Text(f"{metric_col}:Q", format=".0f"),
    )
)

chart_s5 = (bars + labels)
chart_s5 = chart_s5.configure_view(strokeOpacity=0).configure_axisY(labelPadding=12)

st.altair_chart(chart_s5, use_container_width=True)

with st.expander("🧠 How to read this section", expanded=False):
    st.markdown(
        f"""
### What this section shows
This leaderboard surfaces bowlers who produce **big wicket bursts** in a single innings.

✅ **3W Haul** = 3+ wickets in an innings  
✅ **4W Haul** = 4+ wickets in an innings  

### Stability gate (LOCKED)
A bowler must have at least **{MIN_LEGAL_BALLS} legal balls** in the selected scope.
        """
    )

st.divider()

# ============================================================
# SECTION 11: Pace vs Spin Specialists
# ============================================================

st.markdown("## 🧭 Pace vs Spin Specialists")
st.caption("Compare bowling styles using the same KPI-first leaderboard logic (stability gated).")

# -----------------------------
# Style mapping (MANUAL)
# Expand later if needed
# -----------------------------
BOWLER_STYLE_MAP = {
    # --- Pace examples ---
    "JJ Bumrah": "Pace",
    "SL Malinga": "Pace",
    "B Kumar": "Pace",
    "DW Steyn": "Pace",
    "DJ Bravo": "Pace",
    "GD McGrath": "Pace",
    "Sohail Tanvir": "Pace",
    "SM Pollock": "Pace",
    "DE Bollinger": "Pace",

    # --- Spin examples ---
    "Rashid Khan": "Spin",
    "Harbhajan Singh": "Spin",
    "SP Narine": "Spin",
    "R Ashwin": "Spin",
    "PP Chawla": "Spin",
    "YS Chahal": "Spin",
    "RA Jadeja": "Spin",
    "M Muralitharan": "Spin",
    "A Kumble": "Spin",
    "DL Vettori": "Spin",
}

# -----------------------------
# Build style dataframe
# -----------------------------
style_df = base_f.copy()
style_df = style_df[style_df["is_legal_ball"] == 1].copy()

style_df["bowling_style"] = style_df["bowler"].map(BOWLER_STYLE_MAP).fillna("Unknown")

# -----------------------------
# Build style pack (bowler-level)
# -----------------------------
style_pack = (
    style_df.groupby(["bowling_style", "bowler"], as_index=False)
    .agg(
        matches=("match_id", "nunique"),
        legal_balls=("is_legal_ball", "sum"),
        runs=("bowler_runs_conceded", "sum"),
        wkts=("is_bowler_wicket", "sum"),
        dots=("is_dot_ball", "sum"),
    )
)

style_pack["overs"] = style_pack["legal_balls"] / 6
style_pack["econ"] = np.where(style_pack["overs"] > 0, style_pack["runs"] / style_pack["overs"], np.nan)
style_pack["dot_pct"] = np.where(style_pack["legal_balls"] > 0, (style_pack["dots"] / style_pack["legal_balls"]) * 100, np.nan)
style_pack["sr"] = np.where(style_pack["wkts"] > 0, style_pack["legal_balls"] / style_pack["wkts"], np.nan)
style_pack["avg"] = np.where(style_pack["wkts"] > 0, style_pack["runs"] / style_pack["wkts"], np.nan)

# Experience bucket (same as Section 1)
style_pack["exp_bucket"] = style_pack["matches"].apply(add_exp_bucket)

# -----------------------------
# Stability gates (LOCKED)
# -----------------------------
MIN_STYLE_BALLS = 300
MIN_STYLE_WKTS = 15

style_gated_econ_dot = style_pack[style_pack["legal_balls"] >= MIN_STYLE_BALLS].copy()
style_gated_avg_sr = style_pack[
    (style_pack["legal_balls"] >= MIN_STYLE_BALLS) & (style_pack["wkts"] >= MIN_STYLE_WKTS)
].copy()

# -----------------------------
# Controls
# -----------------------------
h1, h2, h3 = st.columns([2.0, 1.0, 1.2], vertical_alignment="center")

with h1:
    style_rank_metric = st.selectbox(
        "📌 Rank by",
        options=[
            "Best Economy ↓",
            "Best Strike Rate ↓",
            "Best Average ↓",
            "Dot Ball % ↑",
            "Most Wickets ↑",
        ],
        index=0,
        key="s11_rank_by"
    )

with h2:
    style_choice = st.selectbox(
        "🌀 Bowling style",
        options=["All styles", "Pace", "Spin", "Unknown"],
        index=0,
        key="s11_style"
    )

with h3:
    style_exp_bucket = st.selectbox(
        "🎯 Matches played",
        options=[
            "All (all experience levels)",
            "1–25 (small sample)",
            "26–50 (emerging core)",
            "51–75 (proven regulars)",
            "75+ (elite longevity)",
        ],
        index=0,
        key="s11_exp_bucket"
    )

bucket_map = {
    "All (all experience levels)": "All",
    "1–25 (small sample)": "1–25",
    "26–50 (emerging core)": "26–50",
    "51–75 (proven regulars)": "51–75",
    "75+ (elite longevity)": "75+",
}
bucket_clean = bucket_map[style_exp_bucket]

# -----------------------------
# Choose dataset based on KPI
# -----------------------------
if style_rank_metric in ["Best Strike Rate ↓", "Best Average ↓"]:
    df_s11 = style_gated_avg_sr.copy()
else:
    df_s11 = style_gated_econ_dot.copy()

# apply style filter
if style_choice != "All styles":
    df_s11 = df_s11[df_s11["bowling_style"] == style_choice].copy()

# apply experience filter
if bucket_clean != "All":
    df_s11 = df_s11[df_s11["exp_bucket"] == bucket_clean].copy()

# -----------------------------
# Metric mapping
# -----------------------------
metric_map = {
    "Best Economy ↓": ("econ", True, "Economy (Lower is better)", ".2f"),
    "Best Strike Rate ↓": ("sr", True, "Strike Rate (Balls per wicket — Lower is better)", ".1f"),
    "Best Average ↓": ("avg", True, "Average (Runs per wicket — Lower is better)", ".1f"),
    "Dot Ball % ↑": ("dot_pct", False, "Dot Ball % (Higher is better)", ".1f"),
    "Most Wickets ↑": ("wkts", False, "Wickets (Higher is better)", ".0f"),
}

metric_col, sort_asc, x_title, label_fmt = metric_map[style_rank_metric]

df_s11 = df_s11.dropna(subset=[metric_col]).copy()
df_s11 = df_s11.sort_values(metric_col, ascending=sort_asc).head(int(top_n)).copy()

if len(df_s11) == 0:
    st.warning("No bowlers match this filter + stability gate. Try All styles or All matches.")
else:
    # Force y-order = sorted order
    y_order = df_s11["bowler"].tolist()
    df_s11["rank"] = range(1, len(df_s11) + 1)

    bars = (
        alt.Chart(df_s11)
        .mark_bar(cornerRadiusEnd=6)
        .encode(
            y=alt.Y("bowler:N", sort=y_order, title=None, axis=alt.Axis(labelLimit=300)),
            x=alt.X(f"{metric_col}:Q", title=x_title),
            color=alt.Color("rank:O", scale=alt.Scale(range=LIGHT_RAINBOW), legend=None),
            tooltip=[
                "bowler:N",
                alt.Tooltip("bowling_style:N", title="Style"),
                alt.Tooltip("exp_bucket:N", title="Matches bucket"),
                alt.Tooltip("matches:Q", title="Matches"),
                alt.Tooltip("overs:Q", title="Overs", format=".1f"),
                alt.Tooltip("wkts:Q", title="Wkts"),
                alt.Tooltip("econ:Q", title="ECON", format=".2f"),
                alt.Tooltip("dot_pct:Q", title="Dot%", format=".1f"),
                alt.Tooltip("avg:Q", title="Avg", format=".1f"),
                alt.Tooltip("sr:Q", title="SR", format=".1f"),
            ]
        )
        .properties(height=360)
    )

    labels = (
        alt.Chart(df_s11)
        .mark_text(align="left", dx=6, fontSize=14)
        .encode(
            y=alt.Y("bowler:N", sort=y_order),
            x=alt.X(f"{metric_col}:Q"),
            text=alt.Text(f"{metric_col}:Q", format=label_fmt),
        )
    )

    chart_s11 = (bars + labels)
    chart_s11 = chart_s11.configure_view(strokeOpacity=0).configure_axisY(labelPadding=12)

    st.altair_chart(chart_s11, use_container_width=True)

with st.expander("🧠 How to read this section", expanded=False):
    st.markdown(
        f"""
### What this section shows
A style-based leaderboard for **Pace vs Spin**, using the same stability rules.

### Important note
Your dataset doesn’t contain a reliable bowling-style column, so we classify using a **manual lookup**.
Unmapped bowlers appear as **Unknown**.

### Stability gates (LOCKED)
- Minimum **{MIN_STYLE_BALLS} legal balls**
- For **Average / Strike Rate**, also minimum **{MIN_STYLE_WKTS} wickets**
        """
    )

st.divider()

# ============================================================
# FINAL SECTION A: Bowler Trend — Performance Over Seasons
# ============================================================

st.markdown("## 📈 Wickets Trend — Bowler Performance Over Seasons")
st.caption("Track how a bowler’s wicket output + economy changes across IPL seasons (scope-aware).")

# ✅ Build season-level base from current filtered deliveries
trend_base = base_f[base_f["is_legal_ball"] == 1].copy()

# --- Season summary per bowler ---
bowler_season = (
    trend_base.groupby(["season_id", "bowler"], as_index=False)
    .agg(
        matches=("match_id", "nunique"),
        legal_balls=("is_legal_ball", "sum"),
        overs=("is_legal_ball", lambda x: x.sum() / 6),
        runs=("bowler_runs_conceded", "sum"),
        wkts=("is_bowler_wicket", "sum"),
        dots=("is_dot_ball", "sum"),
    )
)

bowler_season["econ"] = np.where(bowler_season["overs"] > 0, bowler_season["runs"] / bowler_season["overs"], np.nan)
bowler_season["dot_pct"] = np.where(
    bowler_season["legal_balls"] > 0,
    (bowler_season["dots"] / bowler_season["legal_balls"]) * 100,
    np.nan
)

# --- Top 50 bowlers dropdown (based on wickets in current scope) ---
top50_bowlers = (
    bowler_season.groupby("bowler", as_index=False)
    .agg(total_wkts=("wkts", "sum"), total_balls=("legal_balls", "sum"))
)

# Stability gate for selection list (same logic style)
top50_bowlers = top50_bowlers[top50_bowlers["total_balls"] >= 300].copy()

top50_bowlers = (
    top50_bowlers.sort_values(["total_wkts", "total_balls"], ascending=[False, False])
    .head(50)
)

bowler_list = top50_bowlers["bowler"].tolist()

if len(bowler_list) == 0:
    st.warning("⚠️ No bowlers qualify for the trend view in this scope (min 300 legal balls).")
else:
    pick_bowler = st.selectbox(
        "🎳 Select bowler (Top 50 by wickets in current scope)",
        options=bowler_list,
        index=0,
        key="bowler_trend_select"
    )

    bowler_trend = bowler_season[bowler_season["bowler"] == pick_bowler].copy()
    bowler_trend = bowler_trend.sort_values("season_id")

    # --- Chart: Wickets by Season (line) ---
    line = (
        alt.Chart(bowler_trend)
        .mark_line(point=True)
        .encode(
            x=alt.X("season_id:O", title="Season"),
            y=alt.Y("wkts:Q", title="Wickets"),
            tooltip=[
                alt.Tooltip("season_id:O", title="Season"),
                alt.Tooltip("matches:Q", title="Matches"),
                alt.Tooltip("wkts:Q", title="Wkts"),
                alt.Tooltip("econ:Q", title="ECON", format=".2f"),
                alt.Tooltip("dot_pct:Q", title="Dot%", format=".1f"),
                alt.Tooltip("overs:Q", title="Overs", format=".1f"),
            ]
        )
        .properties(height=360)
    )

    line = line.configure_axis(labelFontSize=12, titleFontSize=12).configure_title(fontSize=18)

    st.altair_chart(line, use_container_width=True)

    with st.expander("🧠 How to read this trend", expanded=False):
        st.markdown(
            """
### What this chart shows
This is a **season-by-season wickets trend** for the selected bowler in your current filters.

- **Wickets** = direct impact output
- Tooltip adds context:
  - **ECON** tells you if the wickets came with control or leakage
  - **Dot %** indicates pressure-building ability
  - **Overs** confirms workload / role stability

✅ Tip: Look for bowlers with **consistent wickets** AND **stable economy** across seasons.
            """
        )

st.divider()

# ============================================================
# FINAL SECTION B: Bowler KPI Profile (Top 50 bowlers)
# ============================================================

st.markdown("## 📌 Bowler KPI Profile")
st.caption("Career summary + phase-wise control profile for the selected bowler (scope-aware + stability gated).")

# --- Dropdown uses same Top 50 list from trend section ---
if len(bowler_list) == 0:
    st.warning("⚠️ No bowlers qualify for KPI profile in this scope (min 300 legal balls).")
else:
    prof_bowler = st.selectbox(
        "🎯 Select bowler (Top 50 by wickets in current scope)",
        options=bowler_list,
        index=0,
        key="bowler_profile_select"
    )

    # --- Career pack for chosen bowler ---
    prof_df = base_f[base_f["bowler"] == prof_bowler].copy()
    prof_legal = prof_df[prof_df["is_legal_ball"] == 1].copy()

    matches_played = prof_legal["match_id"].nunique()
    legal_balls = prof_legal["is_legal_ball"].sum()
    overs = legal_balls / 6
    runs = prof_legal["bowler_runs_conceded"].sum()
    wkts = prof_legal["is_bowler_wicket"].sum()
    dots = prof_legal["is_dot_ball"].sum()
    fours = prof_legal["is_four"].sum()
    sixes = prof_legal["is_six"].sum()

    econ = (runs / overs) if overs > 0 else 0
    avg = (runs / wkts) if wkts > 0 else 0
    sr = (legal_balls / wkts) if wkts > 0 else 0
    dot_pct = (dots / legal_balls) * 100 if legal_balls > 0 else 0

    boundary_balls = fours + sixes
    boundary_pct = (boundary_balls / legal_balls) * 100 if legal_balls > 0 else 0

    # --- KPI CARDS: 8 like batting ---
    st.markdown("### 🧾 Career Summary (in current scope)")

    r1, r2, r3, r4 = st.columns(4, gap="large")
    with r1:
        kpi_card("Matches", f"{matches_played:,}", "📅", KPI_BLUE, desc="Career matches in this scope")
    with r2:
        kpi_card("Wickets", f"{int(wkts):,}", "🎯", KPI_GREEN, desc="Total bowler wickets")
    with r3:
        kpi_card("Economy (ECON)", f"{econ:.2f}", "💸", KPI_ORANGE, desc="Runs conceded per over")
    with r4:
        kpi_card("Strike Rate (SR)", f"{sr:.1f}", "⚡", KPI_PURPLE, desc="Balls per wicket")

    r5, r6, r7, r8 = st.columns(4, gap="large")
    with r5:
        kpi_card("Average (AVG)", f"{avg:.2f}", "🏹", KPI_GREEN, desc="Runs conceded per wicket")
    with r6:
        kpi_card("Dot Ball %", f"{dot_pct:.1f}%", "🧱", KPI_RED, desc="Pressure indicator (higher better)")
    with r7:
        kpi_card("Boundary % Conceded", f"{boundary_pct:.1f}%", "💥", KPI_ORANGE, desc="Boundaries per 100 legal balls")
    with r8:
        kpi_card("Legal Balls", f"{int(legal_balls):,}", "🟡", KPI_DARK, desc="Workload size (stability)")

    st.divider()

    # -----------------------------
    # Phase Impact (ECON + Dot%)
    # -----------------------------
    st.markdown("### ⏱️ Phase Control Profile")
    st.caption("Economy + Dot% across phases (Powerplay / Middle / Death).")

    phase_legal = prof_legal.copy()

    phase_legal["phase"] = np.select(
        [
            phase_legal["over_number"].between(0, 5),
            phase_legal["over_number"].between(6, 14),
            phase_legal["over_number"].between(15, 19),
        ],
        ["Powerplay", "Middle", "Death"],
        default="Other"
    )
    phase_legal = phase_legal[phase_legal["phase"] != "Other"].copy()

    phase_pack = (
        phase_legal.groupby("phase", as_index=False)
        .agg(
            legal_balls=("is_legal_ball", "sum"),
            overs=("is_legal_ball", lambda x: x.sum() / 6),
            runs=("bowler_runs_conceded", "sum"),
            wkts=("is_bowler_wicket", "sum"),
            dots=("is_dot_ball", "sum"),
        )
    )

    phase_pack["econ"] = np.where(phase_pack["overs"] > 0, phase_pack["runs"] / phase_pack["overs"], np.nan)
    phase_pack["dot_pct"] = np.where(
        phase_pack["legal_balls"] > 0,
        (phase_pack["dots"] / phase_pack["legal_balls"]) * 100,
        np.nan
    )

    # Cards: 3 columns (Powerplay, Middle, Death)
    # If some phase missing (rare), fill safely
    phase_pack = phase_pack.set_index("phase")
    def safe_get(p, col, default=0):
        return float(phase_pack.loc[p, col]) if p in phase_pack.index and pd.notna(phase_pack.loc[p, col]) else default

    p1, p2, p3 = st.columns(3, gap="large")

    with p1:
        kpi_card(
            "Powerplay ECON",
            f"{safe_get('Powerplay','econ'):.2f}",
            "🌅",
            KPI_ORANGE,
            desc=f"Dot%: {safe_get('Powerplay','dot_pct'):.1f}%"
        )

    with p2:
        kpi_card(
            "Middle ECON",
            f"{safe_get('Middle','econ'):.2f}",
            "🌀",
            KPI_BLUE,
            desc=f"Dot%: {safe_get('Middle','dot_pct'):.1f}%"
        )

    with p3:
        kpi_card(
            "Death ECON",
            f"{safe_get('Death','econ'):.2f}",
            "🔥",
            KPI_RED,
            desc=f"Dot%: {safe_get('Death','dot_pct'):.1f}%"
        )

    with st.expander("🧠 How to read this profile", expanded=False):
        st.markdown(
            """
### What this profile card tells you
This section is a **single bowler scouting view**.

**Core KPIs**
- **ECON**: control (lower is better)
- **SR**: wicket frequency (lower is better)
- **AVG**: wicket quality (lower is better)
- **Dot %**: pressure (higher is better)

**Phase Control**
- **Powerplay**: early control + new ball impact
- **Middle**: containment + wicket pressure
- **Death**: execution under risk

✅ Best bowlers usually show:
- Strong **Death ECON**
- High **Dot % in Middle**
- Low **Powerplay ECON** with wickets
            """
        )

st.divider()

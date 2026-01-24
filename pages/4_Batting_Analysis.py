import streamlit as st
import altair as alt
import pandas as pd

import src.data_loader as dl


# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="Batting Analysis", page_icon="🏏", layout="wide")


# -----------------------------
# COLORS (same as Tab 3)
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
        <div style="font-size: 2.1rem; font-weight: 800;">🏏 Batting Analysis</div>
        <div style="font-size: 1.05rem; opacity: 0.85;">
            Top batters, scoring efficiency & phase-wise dominance — KPI-first, decision-ready.
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
# KPI GUIDE (placed above filters - better UX)
# -----------------------------
with st.expander("📘 KPI Guide (how to read these metrics)", expanded=False):
    st.markdown(
        """
**Runs**: Total batter runs scored.  
Example: 42 off 30 balls → Runs = 42

**Balls Faced (legal balls)**: Excludes wides (wides don’t count as a ball faced).  
Example: 1 wide + 1 dot → Balls Faced = 1

**Strike Rate (SR)**: How fast a batter scores.  
Formula: (Runs / Balls) × 100  
Example: 42 off 30 → SR = 140.0

**Batting Average (Avg)**: Consistency per dismissal.  
Formula: Runs / Outs  
Example: 500 runs, 10 outs → Avg = 50.0

**Dot Ball %**: Pressure indicator (more dots = more pressure).  
Formula: (Dot Balls / Balls) × 100  
Example: 12 dots in 30 balls → 40%

**4s / 6s**: Boundary volume (style indicator).  
Example: 5 fours + 2 sixes → 4s=5, 6s=2

**Boundary %**: How dependent a batter is on boundaries.  
Formula: (Boundary Runs / Total Runs) × 100  
Example: (5×4 + 2×6)=32 boundary runs out of 42 → 76.2%

**Non-boundary SR**: Strike rotation ability without boundaries.  
Formula: (Non-boundary Runs / Non-boundary Balls) × 100  
Example: (42−32)=10 runs off (30−7)=23 balls → 43.5

**Phases (T20)**:  
Powerplay = overs 1–6, Middle = 7–15, Death = 16–20  
(We map using 0-based over_number in data.)
        """
    )

# -----------------------------
# FILTERS (same UI density)
# -----------------------------
c1, c2, c3 = st.columns([1.3, 1.1, 1.1], gap="large")

with c1:
    region = st.selectbox(
        "🌍 Venue Region",
        options=["All"] + sorted(matches["venue_region"].dropna().unique().tolist()),
        index=0
    )

with c2:
    season_id = st.selectbox(
        "📅 Season",
        options=["All"] + sorted(matches["season_id"].dropna().unique().tolist()),
        index=0
    )

with c3:
    top_choice = st.selectbox("🎯 Show Top", [5, 10], index=1)

# -----------------------------
# APPLY FILTERS (match-scoped)
# -----------------------------
matches_f = matches.copy()

if region != "All":
    matches_f = matches_f[matches_f["venue_region"] == region]

if season_id != "All":
    matches_f = matches_f[matches_f["season_id"] == season_id]

match_ids = set(matches_f["match_id"].unique().tolist())

balls_f = balls[balls["match_id"].isin(match_ids)].copy()


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
            📌 Showing: <b>{region}</b> · <b>{season_id}</b>
        </span>
    </div>
    """,
    unsafe_allow_html=True
)

st.divider()

import numpy as np

import numpy as np

# -----------------------------
# SECTION 1: BATTING SUMMARY KPIs
# -----------------------------
st.markdown("## 📌 Batting Summary KPIs")
st.caption("Quick snapshot of scoring volume, efficiency and pressure in the selected scope.")

# --- Locked rules ---
balls_f["is_legal_ball_faced"] = (~balls_f["is_wide_ball"]).astype(int)
balls_f["is_batter_out"] = ((balls_f["is_wicket"] == True) & (balls_f["player_out"] == balls_f["batter"])).astype(int)
balls_f["is_dot_ball"] = ((balls_f["batter_runs"] == 0) & (balls_f["is_legal_ball_faced"] == 1)).astype(int)

# --- Base totals ---
total_runs = int(balls_f["batter_runs"].sum())
total_balls = int(balls_f["is_legal_ball_faced"].sum())
total_outs = int(balls_f["is_batter_out"].sum())
unique_batters = int(balls_f["batter"].nunique())

overall_sr = (total_runs / total_balls) * 100 if total_balls > 0 else 0
overall_dot_pct = (balls_f["is_dot_ball"].sum() / total_balls) * 100 if total_balls > 0 else 0
overall_avg = (total_runs / total_outs) if total_outs > 0 else 0

# --- KPI cards (4) ---
k1, k2, k3, k4 = st.columns(4, gap="large")

with k1:
    kpi_card(
        "Total runs scored",
        f"{total_runs:,}",
        "🏏",
        KPI_BLUE,
        desc="Overall scoring volume in this scope"
    )

with k2:
    kpi_card(
        "Overall strike rate",
        f"{overall_sr:,.1f}",
        "⚡",
        KPI_ORANGE,
        desc="Runs per 100 balls (scoring speed)"
    )

with k3:
    kpi_card(
        "Overall batting average",
        f"{overall_avg:,.1f}",
        "🎯",
        KPI_GREEN,
        desc="Runs per dismissal (consistency)"
    )

with k4:
    kpi_card(
        "Dot ball % (pressure)",
        f"{overall_dot_pct:,.1f}%",
        "🧱",
        KPI_RED,
        desc="Share of balls with 0 runs"
    )

st.divider()


# -----------------------------
# SECTION 1A: TOP BATTERS (LEADERBOARD)
# -----------------------------
h1, h2, h3 = st.columns([3, 1, 1.4], vertical_alignment="center")

with h1:
    st.markdown("## 🥇 Top Batters — Leaderboard")
    st.caption("Ranks batters by key KPIs using stability gates and experience buckets.")

with h2:
    leaderboard_metric = st.selectbox(
        "📌 Rank by",
        options=["Runs", "SR", "Avg", "Matches"],
        index=0,
        key="sec1_leader_metric"
    )

with h3:
    match_bucket_s1 = st.selectbox(
        "🎯 Matches played",
        options=[
            "All (all experience levels)",
            "1–25 (small sample)",
            "26–50 (emerging core)",
            "51–75 (proven regulars)",
            "75+ (elite longevity)",
        ],
        index=0,
        key="sec1_match_bucket"
    )

# label -> clean bucket mapping (same style as Sections 2–3)
bucket_map = {
    "All (all experience levels)": "All",
    "1–25 (small sample)": "1–25",
    "26–50 (emerging core)": "26–50",
    "51–75 (proven regulars)": "51–75",
    "75+ (elite longevity)": "75+",
}
match_bucket_s1_clean = bucket_map[match_bucket_s1]

player_alltime = (
    balls_f.groupby("batter", as_index=False)
    .agg(
        runs=("batter_runs", "sum"),
        balls=("is_legal_ball_faced", "sum"),
        outs=("is_batter_out", "sum"),
        matches=("match_id", "nunique")
    )
)

player_alltime["strike_rate"] = np.where(
    player_alltime["balls"] > 0,
    (player_alltime["runs"] / player_alltime["balls"]) * 100,
    np.nan
)

player_alltime["average"] = np.where(
    player_alltime["outs"] > 0,
    (player_alltime["runs"] / player_alltime["outs"]),
    np.nan
)

# Experience bucket (by matches)
player_alltime["match_bucket"] = pd.cut(
    player_alltime["matches"],
    bins=[0, 25, 50, 75, 10_000],
    labels=["1–25", "26–50", "51–75", "75+"],
    include_lowest=True
)

# Apply user bucket filter
qual_df = player_alltime.copy()
if match_bucket_s1_clean != "All":
    qual_df = qual_df[qual_df["match_bucket"] == match_bucket_s1_clean].copy()

# -----------------------------
# METRIC-SPECIFIC STABILITY GATES (LOCKED)
# -----------------------------
metric_map = {
    "Runs": ("runs", "Runs", ".0f"),
    "SR": ("strike_rate", "Strike Rate", ".1f"),
    "Avg": ("average", "Average", ".1f"),
    "Matches": ("matches", "Matches", ".0f"),
}

metric_col, metric_label, metric_fmt = metric_map[leaderboard_metric]

# metric-specific gates (LOCKED)
if leaderboard_metric in ["Runs", "Matches"]:
    qual_df = qual_df[qual_df["balls"] >= 200].copy()

elif leaderboard_metric == "SR":
    qual_df = qual_df[qual_df["balls"] >= 400].copy()

elif leaderboard_metric == "Avg":
    qual_df = qual_df[(qual_df["balls"] >= 300) & (qual_df["outs"] >= 15)].copy()

# leaderboard top-N
top_df = (
    qual_df.sort_values(metric_col, ascending=False)
    .head(top_choice)
    .copy()
)

top_df["rank"] = range(1, len(top_df) + 1)

# --- enforce y-order to match sorting ---
y_order = top_df["batter"].tolist()

# -----------------------------
# CHART (same Tab 3 style)
# -----------------------------
bars = (
    alt.Chart(top_df)
    .mark_bar(cornerRadiusEnd=6)
    .encode(
        y=alt.Y("batter:N", sort=y_order, title=None, axis=alt.Axis(labelLimit=300)),
        x=alt.X(f"{metric_col}:Q", title=metric_label),
        color=alt.Color("rank:O", scale=alt.Scale(range=LIGHT_RAINBOW), legend=None),
        tooltip=[
            "batter:N",
            alt.Tooltip("matches:Q", title="Matches"),
            alt.Tooltip("runs:Q", title="Runs"),
            alt.Tooltip("balls:Q", title="Balls faced"),
            alt.Tooltip("outs:Q", title="Outs"),
            alt.Tooltip("strike_rate:Q", title="SR", format=".1f"),
            alt.Tooltip("average:Q", title="Avg", format=".1f"),
        ]
    )
    .properties(height=340)
)

labels = (
    alt.Chart(top_df)
    .mark_text(align="left", dx=6, fontSize=14)
    .encode(
        y=alt.Y("batter:N", sort=y_order),
        x=alt.X(f"{metric_col}:Q"),
        text=alt.Text(f"{metric_col}:Q", format=metric_fmt),
    )
)

chart_leaderboard = (bars + labels)
chart_leaderboard = chart_leaderboard.configure_view(strokeOpacity=0).configure_axisY(labelPadding=12)

st.altair_chart(chart_leaderboard, use_container_width=True)

# -----------------------------
# EXPLANATION (dropdown)
# -----------------------------
with st.expander("🧠 How to read this leaderboard (experience + stability logic)", expanded=False):

    st.markdown(
        f"""
### What this shows
Top **{top_choice}** batters ranked by **{leaderboard_metric}** in the selected scope.

### Why “Matches played” filter exists (All vs 75+)
- **All (all experience levels)** includes everyone in the dataset (subject to metric gates below).
- **75+ (elite longevity)** shows only long-career batters → most stable and repeatable comparisons.

✅ Use **All** to explore emerging impact players.  
✅ Use **75+** to compare proven long-term greats.

---

## ✅ Stability gates (LOCKED)

### Runs / Matches
- Minimum **200 balls**
Reason: avoids ranking players with very low ball volume.

### Strike Rate (SR)
- Minimum **400 balls**
Reason: SR can spike with small samples.

### Average (Avg)
- Minimum **300 balls** AND **15 outs**
Reason: average becomes misleading if dismissals are too few.

### Example (why this matters)
A batter can show **SR 180** over 200 balls (short burst),
but sustaining a top SR over 800+ balls is far more meaningful.
        """
    )


# -----------------------------
# SECTION 2: PRESSURE & BOUNDARIES
# -----------------------------
st.divider()

h1, h2, h3 = st.columns([3, 1, 1.4], vertical_alignment="center")

with h1:
    st.markdown("## 🧱 Pressure & Boundaries")
    st.caption("Dot balls show pressure. Boundaries show dominance. This section highlights both.")

with h2:
    pb_metric = st.selectbox(
        "📌 Rank by",
        options=["Dot Ball % ↓", "4s", "6s", "Boundary %"],
        index=0,
        key="pb_metric_select"
    )

with h3:
    match_bucket_pb = st.selectbox(
        "🎯 Matches played",
        options=[
            "All (all experience levels)",
            "1–25 (small sample)",
            "26–50 (emerging core)",
            "51–75 (proven regulars)",
            "75+ (elite longevity)",
        ],
        index=0,
        key="pb_match_bucket"
    )

# label -> clean bucket mapping (same style as Section 3)
bucket_map = {
    "All (all experience levels)": "All",
    "1–25 (small sample)": "1–25",
    "26–50 (emerging core)": "26–50",
    "51–75 (proven regulars)": "51–75",
    "75+ (elite longevity)": "75+",
}
match_bucket_pb_clean = bucket_map[match_bucket_pb]

# --- Derived flags (locked rules) ---
balls_f["is_dot_ball"] = ((balls_f["batter_runs"] == 0) & (balls_f["is_legal_ball_faced"] == 1)).astype(int)
balls_f["is_four"] = ((balls_f["batter_runs"] == 4) & (balls_f["is_legal_ball_faced"] == 1)).astype(int)
balls_f["is_six"] = ((balls_f["batter_runs"] == 6) & (balls_f["is_legal_ball_faced"] == 1)).astype(int)
balls_f["boundary_runs"] = (balls_f["is_four"] * 4 + balls_f["is_six"] * 6).astype(int)

pb = (
    balls_f.groupby("batter", as_index=False)
    .agg(
        runs=("batter_runs", "sum"),
        balls=("is_legal_ball_faced", "sum"),
        dot_balls=("is_dot_ball", "sum"),
        fours=("is_four", "sum"),
        sixes=("is_six", "sum"),
        boundary_runs=("boundary_runs", "sum"),
        matches=("match_id", "nunique"),
    )
)

pb["dot_ball_pct"] = np.where(pb["balls"] > 0, (pb["dot_balls"] / pb["balls"]) * 100, np.nan)
pb["boundary_pct"] = np.where(pb["runs"] > 0, (pb["boundary_runs"] / pb["runs"]) * 100, np.nan)

# ✅ Base stability gate (LOCKED)
pb = pb[pb["balls"] >= 200].copy()

# Experience bucket (by matches)
pb["match_bucket"] = pd.cut(
    pb["matches"],
    bins=[0, 25, 50, 75, 10_000],
    labels=["1–25", "26–50", "51–75", "75+"],
    include_lowest=True
)

# Apply user bucket filter
if match_bucket_pb_clean != "All":
    pb = pb[pb["match_bucket"] == match_bucket_pb_clean].copy()

# metric logic
pb_map = {
    "Dot Ball % ↓": ("dot_ball_pct", "Dot Ball % (Lower is better)", ".1f", True),
    "4s": ("fours", "4s", ".0f", False),
    "6s": ("sixes", "6s", ".0f", False),
    "Boundary %": ("boundary_pct", "Boundary %", ".1f", False),
}

metric_col, metric_label, metric_fmt, invert = pb_map[pb_metric]

# sorting direction (invert=True => ascending for Dot%)
pb_sorted = pb.sort_values(metric_col, ascending=invert).head(top_choice).copy()
pb_sorted["rank"] = range(1, len(pb_sorted) + 1)

# ✅ important: force y-order to match the sorted dataframe
y_order = pb_sorted["batter"].tolist()

bars = (
    alt.Chart(pb_sorted)
    .mark_bar(cornerRadiusEnd=6)
    .encode(
        y=alt.Y("batter:N", sort=y_order, title=None, axis=alt.Axis(labelLimit=300)),
        x=alt.X(f"{metric_col}:Q", title=metric_label),
        color=alt.Color("rank:O", scale=alt.Scale(range=LIGHT_RAINBOW), legend=None),
        tooltip=[
            "batter:N",
            alt.Tooltip("matches:Q", title="Matches"),
            alt.Tooltip("balls:Q", title="Balls"),
            alt.Tooltip("dot_ball_pct:Q", title="Dot%", format=".1f"),
            alt.Tooltip("fours:Q", title="4s"),
            alt.Tooltip("sixes:Q", title="6s"),
            alt.Tooltip("boundary_pct:Q", title="Boundary%", format=".1f"),
        ]
    )
    .properties(height=340)
)

labels = (
    alt.Chart(pb_sorted)
    .mark_text(align="left", dx=6, fontSize=14)
    .encode(
        y=alt.Y("batter:N", sort=y_order),
        x=alt.X(f"{metric_col}:Q"),
        text=alt.Text(f"{metric_col}:Q", format=metric_fmt),
    )
)

chart_pb = (bars + labels)
chart_pb = chart_pb.configure_view(strokeOpacity=0).configure_axisY(labelPadding=12)

st.altair_chart(chart_pb, use_container_width=True)

with st.expander("🧠 How to read this section", expanded=False):
    st.markdown(
        """
### What this section measures
**Dot Ball % (lower is better):** how often a batter gets stuck (0 runs on a legal ball).  
Example: 12 dot balls in 30 balls → **40%** dot balls.

**Boundary %:** how dependent the batter is on boundaries for scoring.  
Example: 32 boundary runs out of 42 total runs → **76.2%** boundary dependency.

### Why “Matches played” filter exists (All vs 75+)
- **All (all experience levels)** includes everyone who passes the base ball filter.
- **75+ (elite longevity)** shows only long-career batters → most stable comparisons.

✅ Use **All** to discover short-career impact batters.  
✅ Use **75+** to compare proven long-term performers.

### Qualification rule (base stability)
Minimum **200 balls faced** in the selected scope
        """
    )



# -----------------------------
# SECTION 3: PHASE PERFORMANCE
# -----------------------------
st.divider()

st.markdown("## ⏱️ Phase Performance")
st.caption("Compare batter impact across phases using Strike Rate, Runs and Boundary%. (Experience bucketed)")

# ✅ Filters in ONE LINE (Phase | Rank by | Matches played)
f1, f2, f3 = st.columns([1.2, 1.2, 1.4], vertical_alignment="center")

with f1:
    phase_choice = st.selectbox(
        "🧩 Phase",
        options=["Powerplay", "Middle", "Death"],
        index=0,
        key="phase_choice"
    )

with f2:
    phase_metric = st.selectbox(
        "📌 Rank by",
        options=["SR", "Runs", "Boundary %"],
        index=0,
        key="phase_metric"
    )

with f3:
    match_bucket_phase = st.selectbox(
        "🎯 Matches played",
        options=[
            "All (all experience levels)",
            "1–25 (small sample)",
            "26–50 (emerging core)",
            "51–75 (proven regulars)",
            "75+ (elite longevity)"
        ],
        index=0,
        key="phase_match_bucket"
    )

# map label -> bucket code
bucket_map = {
    "All (all experience levels)": "All",
    "1–25 (small sample)": "1–25",
    "26–50 (emerging core)": "26–50",
    "51–75 (proven regulars)": "51–75",
    "75+ (elite longevity)": "75+",
}
match_bucket_phase_clean = bucket_map[match_bucket_phase]

# --- Phase tagging (over_number is 0-based) ---
balls_f["phase"] = pd.Series(pd.NA, index=balls_f.index)
balls_f.loc[balls_f["over_number"].between(0, 5), "phase"] = "Powerplay"
balls_f.loc[balls_f["over_number"].between(6, 14), "phase"] = "Middle"
balls_f.loc[balls_f["over_number"].between(15, 19), "phase"] = "Death"

phase_balls = balls_f[balls_f["phase"] == phase_choice].copy()

# boundary flags in-phase
phase_balls["is_four"] = ((phase_balls["batter_runs"] == 4) & (phase_balls["is_legal_ball_faced"] == 1)).astype(int)
phase_balls["is_six"] = ((phase_balls["batter_runs"] == 6) & (phase_balls["is_legal_ball_faced"] == 1)).astype(int)
phase_balls["boundary_runs"] = (phase_balls["is_four"] * 4 + phase_balls["is_six"] * 6).astype(int)

ph = (
    phase_balls.groupby("batter", as_index=False)
    .agg(
        runs=("batter_runs", "sum"),
        balls=("is_legal_ball_faced", "sum"),
        fours=("is_four", "sum"),
        sixes=("is_six", "sum"),
        boundary_runs=("boundary_runs", "sum"),
        matches=("match_id", "nunique"),
    )
)

ph["strike_rate"] = np.where(ph["balls"] > 0, (ph["runs"] / ph["balls"]) * 100, np.nan)
ph["boundary_pct"] = np.where(ph["runs"] > 0, (ph["boundary_runs"] / ph["runs"]) * 100, np.nan)

# ✅ base phase stability gate (LOCKED)
ph = ph[ph["balls"] >= 120].copy()

# Experience bucket (by matches)
ph["match_bucket"] = pd.cut(
    ph["matches"],
    bins=[0, 25, 50, 75, 10_000],
    labels=["1–25", "26–50", "51–75", "75+"],
    include_lowest=True
)

# Apply user bucket filter
if match_bucket_phase_clean != "All":
    ph = ph[ph["match_bucket"] == match_bucket_phase_clean].copy()

# metric map (short labels)
phase_map = {
    "SR": ("strike_rate", "Strike Rate", ".1f"),
    "Runs": ("runs", "Runs", ".0f"),
    "Boundary %": ("boundary_pct", "Boundary %", ".1f"),
}

metric_col, metric_label, metric_fmt = phase_map[phase_metric]

ph_sorted = ph.sort_values(metric_col, ascending=False).head(top_choice).copy()
ph_sorted["rank"] = range(1, len(ph_sorted) + 1)

y_order = ph_sorted["batter"].tolist()

bars = (
    alt.Chart(ph_sorted)
    .mark_bar(cornerRadiusEnd=6)
    .encode(
        y=alt.Y("batter:N", sort=y_order, title=None, axis=alt.Axis(labelLimit=300)),
        x=alt.X(f"{metric_col}:Q", title=f"{phase_choice} — {metric_label}"),
        color=alt.Color("rank:O", scale=alt.Scale(range=LIGHT_RAINBOW), legend=None),
        tooltip=[
            "batter:N",
            alt.Tooltip("matches:Q", title="Matches"),
            alt.Tooltip("runs:Q", title="Runs"),
            alt.Tooltip("balls:Q", title="Balls"),
            alt.Tooltip("strike_rate:Q", title="SR", format=".1f"),
            alt.Tooltip("boundary_pct:Q", title="Boundary%", format=".1f"),
            alt.Tooltip("fours:Q", title="4s"),
            alt.Tooltip("sixes:Q", title="6s"),
        ]
    )
    .properties(height=340)
)

labels = (
    alt.Chart(ph_sorted)
    .mark_text(align="left", dx=6, fontSize=14)
    .encode(
        y=alt.Y("batter:N", sort=y_order),
        x=alt.X(f"{metric_col}:Q"),
        text=alt.Text(f"{metric_col}:Q", format=metric_fmt),
    )
)

chart_phase = (bars + labels)
chart_phase = chart_phase.configure_view(strokeOpacity=0).configure_axisY(labelPadding=12)

st.altair_chart(chart_phase, use_container_width=True)

with st.expander("🧠 How to read this section", expanded=False):
    st.markdown(
        """
### Phases (T20)
- **Powerplay (1–6):** field restrictions → easier boundary value
- **Middle (7–15):** rotation + matchup control
- **Death (16–20):** finishing power + boundary hitting

### Why “Matches played” filter exists (All vs 75+)
- **All** includes every batter who qualifies by phase balls (>=120) → includes short & long careers.
- **75+** shows only long-tenure IPL batters → most stable comparisons.

✅ Use **All** to discover new impact players.  
✅ Use **75+** to compare proven long-term performers.
        """
    )

# -----------------------------
# SECTION 4A: NON-BOUNDARY STRIKE RATE (ROTATION)
# -----------------------------
st.divider()

h1, h2 = st.columns([3, 1.4], vertical_alignment="center")

with h1:
    st.markdown("## 🔁 Rotation Engine — Non-Boundary Strike Rate")
    st.caption("Measures strike rotation: scoring speed excluding boundary runs (4s & 6s).")

with h2:
    match_bucket_nb = st.selectbox(
        "🎯 Matches played",
        options=[
            "All (all experience levels)",
            "1–25 (small sample)",
            "26–50 (emerging core)",
            "51–75 (proven regulars)",
            "75+ (elite longevity)",
        ],
        index=0,
        key="nb_match_bucket"
    )

bucket_map = {
    "All (all experience levels)": "All",
    "1–25 (small sample)": "1–25",
    "26–50 (emerging core)": "26–50",
    "51–75 (proven regulars)": "51–75",
    "75+ (elite longevity)": "75+",
}
match_bucket_nb_clean = bucket_map[match_bucket_nb]

# --- Build non-boundary components ---
balls_f["is_four"] = ((balls_f["batter_runs"] == 4) & (balls_f["is_legal_ball_faced"] == 1)).astype(int)
balls_f["is_six"] = ((balls_f["batter_runs"] == 6) & (balls_f["is_legal_ball_faced"] == 1)).astype(int)

balls_f["boundary_runs"] = (balls_f["is_four"] * 4 + balls_f["is_six"] * 6).astype(int)

# a legal ball is a "boundary ball" if it resulted in 4 or 6 off the bat
balls_f["is_boundary_ball"] = (
    ((balls_f["batter_runs"] == 4) | (balls_f["batter_runs"] == 6))
    & (balls_f["is_legal_ball_faced"] == 1)
).astype(int)

nb = (
    balls_f.groupby("batter", as_index=False)
    .agg(
        matches=("match_id", "nunique"),
        runs=("batter_runs", "sum"),
        balls=("is_legal_ball_faced", "sum"),
        boundary_runs=("boundary_runs", "sum"),
        boundary_balls=("is_boundary_ball", "sum"),
    )
)

nb["non_boundary_runs"] = nb["runs"] - nb["boundary_runs"]
nb["non_boundary_balls"] = nb["balls"] - nb["boundary_balls"]

nb["non_boundary_sr"] = np.where(
    nb["non_boundary_balls"] > 0,
    (nb["non_boundary_runs"] / nb["non_boundary_balls"]) * 100,
    np.nan
)

# ✅ base stability gate (LOCKED)
nb = nb[nb["balls"] >= 200].copy()

# experience bucket
nb["match_bucket"] = pd.cut(
    nb["matches"],
    bins=[0, 25, 50, 75, 10_000],
    labels=["1–25", "26–50", "51–75", "75+"],
    include_lowest=True
)

if match_bucket_nb_clean != "All":
    nb = nb[nb["match_bucket"] == match_bucket_nb_clean].copy()

nb_sorted = nb.sort_values("non_boundary_sr", ascending=False).head(top_choice).copy()
nb_sorted["rank"] = range(1, len(nb_sorted) + 1)

y_order = nb_sorted["batter"].tolist()

bars = (
    alt.Chart(nb_sorted)
    .mark_bar(cornerRadiusEnd=6)
    .encode(
        y=alt.Y("batter:N", sort=y_order, title=None, axis=alt.Axis(labelLimit=300)),
        x=alt.X("non_boundary_sr:Q", title="Non-Boundary Strike Rate"),
        color=alt.Color("rank:O", scale=alt.Scale(range=LIGHT_RAINBOW), legend=None),
        tooltip=[
            "batter:N",
            alt.Tooltip("matches:Q", title="Matches"),
            alt.Tooltip("balls:Q", title="Balls"),
            alt.Tooltip("runs:Q", title="Runs"),
            alt.Tooltip("boundary_runs:Q", title="Boundary runs"),
            alt.Tooltip("non_boundary_runs:Q", title="Non-boundary runs"),
            alt.Tooltip("non_boundary_balls:Q", title="Non-boundary balls"),
            alt.Tooltip("non_boundary_sr:Q", title="Non-Boundary SR", format=".1f"),
        ]
    )
    .properties(height=340)
)

labels = (
    alt.Chart(nb_sorted)
    .mark_text(align="left", dx=6, fontSize=14)
    .encode(
        y=alt.Y("batter:N", sort=y_order),
        x=alt.X("non_boundary_sr:Q"),
        text=alt.Text("non_boundary_sr:Q", format=".1f"),
    )
)

chart_nb = (bars + labels)
chart_nb = chart_nb.configure_view(strokeOpacity=0).configure_axisY(labelPadding=12)

st.altair_chart(chart_nb, use_container_width=True)

with st.expander("🧠 How to read this section", expanded=False):
    st.markdown(
        """
### What this metric tracks
**Non-Boundary Strike Rate** = scoring speed excluding boundary runs.

It focuses on:
✅ strike rotation  
✅ singles + doubles  
✅ ability to keep scoreboard moving without relying only on 4s/6s

### Why “Matches played” filter exists (All vs 75+)
- **All (all experience levels)** includes everyone who qualifies by volume.
- **75+ (elite longevity)** shows proven long-career batters → most stable rotation profiles.

### Qualification rule (base stability)
Minimum **200 balls faced** in the selected scope
        """
    )
# -----------------------------
# SECTION 4B: AVERAGE BALLS FACED PER INNINGS (BAT TIME)
# -----------------------------
st.divider()

h1, h2 = st.columns([3, 1.4], vertical_alignment="center")

with h1:
    st.markdown("## 🕒 Bat Time — Average Balls Faced per Innings")
    st.caption("Shows who bats deep vs who plays shorter cameos (stability gated + experience bucketed).")

with h2:
    match_bucket_bpi = st.selectbox(
        "🎯 Matches played",
        options=[
            "All (all experience levels)",
            "1–25 (small sample)",
            "26–50 (emerging core)",
            "51–75 (proven regulars)",
            "75+ (elite longevity)",
        ],
        index=0,
        key="bpi_match_bucket"
    )

bucket_map = {
    "All (all experience levels)": "All",
    "1–25 (small sample)": "1–25",
    "26–50 (emerging core)": "26–50",
    "51–75 (proven regulars)": "51–75",
    "75+ (elite longevity)": "75+",
}
match_bucket_bpi_clean = bucket_map[match_bucket_bpi]

# --- Batter-innings grain (match_id + innings + batter) ---
# we count only legal balls faced as "balls faced"
bi = (
    balls_f.groupby(["match_id", "innings", "batter"], as_index=False)
    .agg(
        balls_faced=("is_legal_ball_faced", "sum"),
        runs=("batter_runs", "sum"),
    )
)

# remove empty rows (shouldn't happen, but safe)
bi = bi[bi["balls_faced"] > 0].copy()

bpi = (
    bi.groupby("batter", as_index=False)
    .agg(
        innings=("match_id", "count"),  # number of batter-innings appearances
        total_balls=("balls_faced", "sum"),
        total_runs=("runs", "sum"),
        matches=("match_id", "nunique"),
    )
)

bpi["avg_balls_per_innings"] = np.where(
    bpi["innings"] > 0,
    bpi["total_balls"] / bpi["innings"],
    np.nan
)

# ✅ base stability gate (LOCKED)
bpi = bpi[bpi["total_balls"] >= 200].copy()

# experience bucket
bpi["match_bucket"] = pd.cut(
    bpi["matches"],
    bins=[0, 25, 50, 75, 10_000],
    labels=["1–25", "26–50", "51–75", "75+"],
    include_lowest=True
)

if match_bucket_bpi_clean != "All":
    bpi = bpi[bpi["match_bucket"] == match_bucket_bpi_clean].copy()

bpi_sorted = bpi.sort_values("avg_balls_per_innings", ascending=False).head(top_choice).copy()
bpi_sorted["rank"] = range(1, len(bpi_sorted) + 1)

y_order = bpi_sorted["batter"].tolist()

bars = (
    alt.Chart(bpi_sorted)
    .mark_bar(cornerRadiusEnd=6)
    .encode(
        y=alt.Y("batter:N", sort=y_order, title=None, axis=alt.Axis(labelLimit=300)),
        x=alt.X("avg_balls_per_innings:Q", title="Average balls faced per innings"),
        color=alt.Color("rank:O", scale=alt.Scale(range=LIGHT_RAINBOW), legend=None),
        tooltip=[
            "batter:N",
            alt.Tooltip("matches:Q", title="Matches"),
            alt.Tooltip("innings:Q", title="Innings"),
            alt.Tooltip("total_balls:Q", title="Total balls"),
            alt.Tooltip("total_runs:Q", title="Total runs"),
            alt.Tooltip("avg_balls_per_innings:Q", title="Avg balls/innings", format=".1f"),
        ]
    )
    .properties(height=340)
)

labels = (
    alt.Chart(bpi_sorted)
    .mark_text(align="left", dx=6, fontSize=14)
    .encode(
        y=alt.Y("batter:N", sort=y_order),
        x=alt.X("avg_balls_per_innings:Q"),
        text=alt.Text("avg_balls_per_innings:Q", format=".1f"),
    )
)

chart_bpi = (bars + labels)
chart_bpi = chart_bpi.configure_view(strokeOpacity=0).configure_axisY(labelPadding=12)

st.altair_chart(chart_bpi, use_container_width=True)

with st.expander("🧠 How to read this section", expanded=False):
    st.markdown(
        """
### What this metric tracks
**Average Balls Faced per Innings** = how long a batter typically stays at the crease.

- Higher value → bats deep, anchors or long innings
- Lower value → cameo hitter / finisher role (short bursts)

### Example
If a batter plays 5 innings and faces:
20, 35, 10, 28, 27 balls  
Average balls/innings = (20+35+10+28+27) / 5 = **24.0**

### Why “Matches played” filter exists (All vs 75+)
- **All (all experience levels)** includes short and long careers.
- **75+ (elite longevity)** highlights proven long-term batting profiles.

### Qualification rule (base stability)
Minimum **200 balls faced** in the selected scope
        """
    )
# -----------------------------
# SECTION 4C: BOUNDARY % BY PHASE (DOMINANCE)
# -----------------------------
st.divider()

h1, h2, h3 = st.columns([3, 1.2, 1.4], vertical_alignment="center")

with h1:
    st.markdown("## 🎯 Boundary Dominance — Boundary % by Phase")
    st.caption("Shows how boundary-dependent a batter is in each phase (Powerplay / Middle / Death).")

with h2:
    phase_choice_bp = st.selectbox(
        "🧩 Phase",
        options=["Powerplay", "Middle", "Death"],
        index=0,
        key="bp_phase_choice"
    )

with h3:
    match_bucket_bp = st.selectbox(
        "🎯 Matches played",
        options=[
            "All (all experience levels)",
            "1–25 (small sample)",
            "26–50 (emerging core)",
            "51–75 (proven regulars)",
            "75+ (elite longevity)",
        ],
        index=0,
        key="bp_match_bucket"
    )

bucket_map = {
    "All (all experience levels)": "All",
    "1–25 (small sample)": "1–25",
    "26–50 (emerging core)": "26–50",
    "51–75 (proven regulars)": "51–75",
    "75+ (elite longevity)": "75+",
}
match_bucket_bp_clean = bucket_map[match_bucket_bp]

# --- Phase tagging (over_number is 0-based) ---
balls_f["phase"] = pd.Series(pd.NA, index=balls_f.index)
balls_f.loc[balls_f["over_number"].between(0, 5), "phase"] = "Powerplay"
balls_f.loc[balls_f["over_number"].between(6, 14), "phase"] = "Middle"
balls_f.loc[balls_f["over_number"].between(15, 19), "phase"] = "Death"

phase_balls = balls_f[balls_f["phase"] == phase_choice_bp].copy()

# boundary flags in-phase
phase_balls["is_four"] = ((phase_balls["batter_runs"] == 4) & (phase_balls["is_legal_ball_faced"] == 1)).astype(int)
phase_balls["is_six"] = ((phase_balls["batter_runs"] == 6) & (phase_balls["is_legal_ball_faced"] == 1)).astype(int)
phase_balls["boundary_runs"] = (phase_balls["is_four"] * 4 + phase_balls["is_six"] * 6).astype(int)

bp = (
    phase_balls.groupby("batter", as_index=False)
    .agg(
        matches=("match_id", "nunique"),
        runs=("batter_runs", "sum"),
        balls=("is_legal_ball_faced", "sum"),
        fours=("is_four", "sum"),
        sixes=("is_six", "sum"),
        boundary_runs=("boundary_runs", "sum"),
    )
)

bp["boundary_pct"] = np.where(bp["runs"] > 0, (bp["boundary_runs"] / bp["runs"]) * 100, np.nan)

# ✅ Phase stability gate (LOCKED baseline)
bp = bp[bp["balls"] >= 120].copy()

# experience bucket
bp["match_bucket"] = pd.cut(
    bp["matches"],
    bins=[0, 25, 50, 75, 10_000],
    labels=["1–25", "26–50", "51–75", "75+"],
    include_lowest=True
)

if match_bucket_bp_clean != "All":
    bp = bp[bp["match_bucket"] == match_bucket_bp_clean].copy()

bp_sorted = bp.sort_values("boundary_pct", ascending=False).head(top_choice).copy()
bp_sorted["rank"] = range(1, len(bp_sorted) + 1)

y_order = bp_sorted["batter"].tolist()

bars = (
    alt.Chart(bp_sorted)
    .mark_bar(cornerRadiusEnd=6)
    .encode(
        y=alt.Y("batter:N", sort=y_order, title=None, axis=alt.Axis(labelLimit=300)),
        x=alt.X("boundary_pct:Q", title=f"{phase_choice_bp} — Boundary %"),
        color=alt.Color("rank:O", scale=alt.Scale(range=LIGHT_RAINBOW), legend=None),
        tooltip=[
            "batter:N",
            alt.Tooltip("matches:Q", title="Matches"),
            alt.Tooltip("balls:Q", title="Balls"),
            alt.Tooltip("runs:Q", title="Runs"),
            alt.Tooltip("fours:Q", title="4s"),
            alt.Tooltip("sixes:Q", title="6s"),
            alt.Tooltip("boundary_pct:Q", title="Boundary %", format=".1f"),
        ]
    )
    .properties(height=340)
)

labels = (
    alt.Chart(bp_sorted)
    .mark_text(align="left", dx=6, fontSize=14)
    .encode(
        y=alt.Y("batter:N", sort=y_order),
        x=alt.X("boundary_pct:Q"),
        text=alt.Text("boundary_pct:Q", format=".1f"),
    )
)

chart_bp = (bars + labels)
chart_bp = chart_bp.configure_view(strokeOpacity=0).configure_axisY(labelPadding=12)

st.altair_chart(chart_bp, use_container_width=True)

with st.expander("🧠 How to read this section", expanded=False):
    st.markdown(
        """
### What this metric tracks
**Boundary %** = share of total runs coming from **4s + 6s**.

- High Boundary % → power / dominance
- Lower Boundary % → more singles + rotation

### Example
If a batter scores **50 runs**, and **32 runs** come from boundaries:  
Boundary % = (32 / 50) × 100 = **64%**

### Why Phase matters
Boundary dependence changes by phase:
- Powerplay: field restrictions → easier boundaries
- Middle: rotation + matchups → fewer boundaries needed
- Death: finishing → boundary-heavy scoring

### Why “Matches played” filter exists (All vs 75+)
- **All (all experience levels)** includes short and long careers.
- **75+ (elite longevity)** highlights proven long-term phase profiles.

### Qualification rule (phase stability)
Minimum **120 balls faced in the selected phase**
        """
    )

# -----------------------------
# SECTION 4D: DISMISSAL PATTERNS (HOW BATTERS GET OUT)
# -----------------------------
st.divider()

h1, h2, h3 = st.columns([3, 1.2, 1.4], vertical_alignment="center")

with h1:
    st.markdown("## 🎯 Dismissal Patterns — How Batters Get Out")
    st.caption("Identify dismissal tendencies: caught-heavy, bowled-heavy, LBW risk, etc.")

with h2:
    dismissal_choice = st.selectbox(
        "🧤 Dismissal type",
        options=["Caught", "Bowled", "LBW", "Run Out", "Stumped"],
        index=0,
        key="dismissal_type_choice"
    )

with h3:
    match_bucket_dis = st.selectbox(
        "🎯 Matches played",
        options=[
            "All (all experience levels)",
            "1–25 (small sample)",
            "26–50 (emerging core)",
            "51–75 (proven regulars)",
            "75+ (elite longevity)",
        ],
        index=0,
        key="dismissal_match_bucket"
    )

bucket_map = {
    "All (all experience levels)": "All",
    "1–25 (small sample)": "1–25",
    "26–50 (emerging core)": "26–50",
    "51–75 (proven regulars)": "51–75",
    "75+ (elite longevity)": "75+",
}
match_bucket_dis_clean = bucket_map[match_bucket_dis]

# --- Batter outs table ---
outs = balls_f[(balls_f["is_batter_out"] == 1)].copy()

# normalize wicket kind (defensive)
outs["wicket_kind"] = outs["wicket_kind"].astype(str).str.strip()

# map user choice -> wicket_kind values
dismissal_map = {
    "Caught": ["caught"],
    "Bowled": ["bowled"],
    "LBW": ["lbw"],
    "Run Out": ["run out"],
    "Stumped": ["stumped"],
}

# create a normalized version for matching
outs["wicket_kind_norm"] = outs["wicket_kind"].str.lower()

target_kinds = dismissal_map[dismissal_choice]

# count outs per batter (total + chosen type)
dis = (
    outs.groupby("batter", as_index=False)
    .agg(
        total_outs=("batter", "size"),
        matches=("match_id", "nunique"),
    )
)

dis_target = (
    outs[outs["wicket_kind_norm"].isin(target_kinds)]
    .groupby("batter", as_index=False)
    .agg(target_outs=("batter", "size"))
)

dis = dis.merge(dis_target, on="batter", how="left")
dis["target_outs"] = dis["target_outs"].fillna(0).astype(int)

# dismissal share (% of a batter's dismissals)
dis["dismissal_share_pct"] = np.where(
    dis["total_outs"] > 0,
    (dis["target_outs"] / dis["total_outs"]) * 100,
    np.nan
)

# stability gate (LOCKED baseline for dismissal patterns)
dis = dis[dis["total_outs"] >= 15].copy()

# experience bucket (by matches)
dis["match_bucket"] = pd.cut(
    dis["matches"],
    bins=[0, 25, 50, 75, 10_000],
    labels=["1–25", "26–50", "51–75", "75+"],
    include_lowest=True
)

if match_bucket_dis_clean != "All":
    dis = dis[dis["match_bucket"] == match_bucket_dis_clean].copy()

dis_sorted = dis.sort_values("dismissal_share_pct", ascending=False).head(top_choice).copy()
dis_sorted["rank"] = range(1, len(dis_sorted) + 1)

y_order = dis_sorted["batter"].tolist()

bars = (
    alt.Chart(dis_sorted)
    .mark_bar(cornerRadiusEnd=6)
    .encode(
        y=alt.Y("batter:N", sort=y_order, title=None, axis=alt.Axis(labelLimit=300)),
        x=alt.X("dismissal_share_pct:Q", title=f"{dismissal_choice} share of dismissals (%)"),
        color=alt.Color("rank:O", scale=alt.Scale(range=LIGHT_RAINBOW), legend=None),
        tooltip=[
            "batter:N",
            alt.Tooltip("matches:Q", title="Matches"),
            alt.Tooltip("total_outs:Q", title="Total outs"),
            alt.Tooltip("target_outs:Q", title=f"{dismissal_choice} outs"),
            alt.Tooltip("dismissal_share_pct:Q", title="Share %", format=".1f"),
        ]
    )
    .properties(height=340)
)

labels = (
    alt.Chart(dis_sorted)
    .mark_text(align="left", dx=6, fontSize=14)
    .encode(
        y=alt.Y("batter:N", sort=y_order),
        x=alt.X("dismissal_share_pct:Q"),
        text=alt.Text("dismissal_share_pct:Q", format=".1f"),
    )
)

chart_dis = (bars + labels)
chart_dis = chart_dis.configure_view(strokeOpacity=0).configure_axisY(labelPadding=12)

st.altair_chart(chart_dis, use_container_width=True)

with st.expander("🧠 How to read this section", expanded=False):
    st.markdown(
        """
### What this metric tracks
This chart shows what **percentage of a batter’s dismissals** come from a chosen wicket type.

Example:
If a batter got out **40 times**, and **22 were caught** → Caught share = (22 / 40) × 100 = **55%**

### How to use it
- High **Caught share** → hitting into the field / aerial risk
- High **Bowled/LBW share** → susceptible to straight balls / movement
- High **Stumped share** → vulnerable vs spin / using feet
- High **Run Out share** → risky singles or poor running

### Qualification rule (stability)
Minimum **15 total outs** (to avoid small-sample distortion)
        """
    )

# -----------------------------
# SECTION 4E: BATTING MATCHUPS — VS SPIN / VS PACE
# -----------------------------
st.divider()

h1, h2, h3, h4 = st.columns([3, 1.15, 1.15, 1.4], vertical_alignment="center")

with h1:
    st.markdown("## 🧩 Batting Matchups — vs Spin / Pace")
    st.caption("Shows which batters perform best depending on the bowler type faced.")

with h2:
    bowler_type_choice = st.selectbox(
        "🎯 Bowler type",
        options=["Spin", "Pace"],
        index=0,
        key="matchup_bowler_type"
    )

with h3:
    matchup_metric = st.selectbox(
        "📌 Rank by",
        options=["SR", "Runs", "Dot Ball % ↓"],
        index=0,
        key="matchup_metric"
    )

with h4:
    match_bucket_matchup = st.selectbox(
        "🎯 Matches played",
        options=[
            "All (all experience levels)",
            "1–25 (small sample)",
            "26–50 (emerging core)",
            "51–75 (proven regulars)",
            "75+ (elite longevity)",
        ],
        index=0,
        key="matchup_match_bucket"
    )

bucket_map = {
    "All (all experience levels)": "All",
    "1–25 (small sample)": "1–25",
    "26–50 (emerging core)": "26–50",
    "51–75 (proven regulars)": "51–75",
    "75+ (elite longevity)": "75+",
}
match_bucket_matchup_clean = bucket_map[match_bucket_matchup]

# --- filter balls by bowler type faced ---
matchup_balls = balls_f.copy()

# normalize bowler_type labels (defensive)
# normalize bowler_type labels (defensive)
matchup_balls["bowler_type_norm"] = matchup_balls["bowler_type"].astype(str).str.lower().str.strip()

# classify spin using bowling style keywords
spin_keywords = [
    "spin", "legbreak", "offbreak", "orthodox", "chinaman", "googly"
]

is_spin = matchup_balls["bowler_type_norm"].str.contains("|".join(spin_keywords), regex=True, na=False)

if bowler_type_choice == "Spin":
    matchup_balls = matchup_balls[is_spin].copy()
else:
    matchup_balls = matchup_balls[~is_spin].copy()


# dot balls
matchup_balls["is_dot_ball"] = (
    (matchup_balls["batter_runs"] == 0) & (matchup_balls["is_legal_ball_faced"] == 1)
).astype(int)

mu = (
    matchup_balls.groupby("batter", as_index=False)
    .agg(
        matches=("match_id", "nunique"),
        runs=("batter_runs", "sum"),
        balls=("is_legal_ball_faced", "sum"),
        dot_balls=("is_dot_ball", "sum"),
    )
)

mu["strike_rate"] = np.where(mu["balls"] > 0, (mu["runs"] / mu["balls"]) * 100, np.nan)
mu["dot_ball_pct"] = np.where(mu["balls"] > 0, (mu["dot_balls"] / mu["balls"]) * 100, np.nan)

# ✅ base stability gate (LOCKED)
mu = mu[mu["balls"] >= 200].copy()

# experience bucket (by matches)
mu["match_bucket"] = pd.cut(
    mu["matches"],
    bins=[0, 25, 50, 75, 10_000],
    labels=["1–25", "26–50", "51–75", "75+"],
    include_lowest=True
)

if match_bucket_matchup_clean != "All":
    mu = mu[mu["match_bucket"] == match_bucket_matchup_clean].copy()

# metric map
mu_map = {
    "SR": ("strike_rate", "Strike Rate", ".1f", False),
    "Runs": ("runs", "Runs", ".0f", False),
    "Dot Ball % ↓": ("dot_ball_pct", "Dot Ball % (Lower is better)", ".1f", True),
}

metric_col, metric_label, metric_fmt, invert = mu_map[matchup_metric]

mu_sorted = mu.sort_values(metric_col, ascending=invert).head(top_choice).copy()
mu_sorted["rank"] = range(1, len(mu_sorted) + 1)

y_order = mu_sorted["batter"].tolist()

bars = (
    alt.Chart(mu_sorted)
    .mark_bar(cornerRadiusEnd=6)
    .encode(
        y=alt.Y("batter:N", sort=y_order, title=None, axis=alt.Axis(labelLimit=300)),
        x=alt.X(f"{metric_col}:Q", title=f"vs {bowler_type_choice} — {metric_label}"),
        color=alt.Color("rank:O", scale=alt.Scale(range=LIGHT_RAINBOW), legend=None),
        tooltip=[
            "batter:N",
            alt.Tooltip("matches:Q", title="Matches"),
            alt.Tooltip("runs:Q", title="Runs"),
            alt.Tooltip("balls:Q", title="Balls"),
            alt.Tooltip("strike_rate:Q", title="SR", format=".1f"),
            alt.Tooltip("dot_ball_pct:Q", title="Dot%", format=".1f"),
        ]
    )
    .properties(height=340)
)

labels = (
    alt.Chart(mu_sorted)
    .mark_text(align="left", dx=6, fontSize=14)
    .encode(
        y=alt.Y("batter:N", sort=y_order),
        x=alt.X(f"{metric_col}:Q"),
        text=alt.Text(f"{metric_col}:Q", format=metric_fmt),
    )
)

chart_mu = (bars + labels)
chart_mu = chart_mu.configure_view(strokeOpacity=0).configure_axisY(labelPadding=12)

st.altair_chart(chart_mu, use_container_width=True)

with st.expander("🧠 How to read this section", expanded=False):
    st.markdown(
        """
### What this section tracks
This leaderboard ranks batters based on performance **vs a selected bowler type**:
- **Spin** (slow bowlers)
- **Pace** (fast/medium bowlers)

### Why this matters
Many batters have clear matchup patterns:
- Some dominate spin in the middle overs
- Some are elite pace hitters at the death
- Some struggle when the bowler type changes

### Qualification rule (base stability)
Minimum **200 balls faced** vs the selected bowler type
        """
    )

# -----------------------------
# SECTION 5: RUNS TREND (PER SEASON)
# -----------------------------
st.divider()

st.markdown("## 📈 Runs Trend — Batter Performance Over Seasons")
st.caption("Track how a batter’s output changes across IPL seasons (runs + efficiency context).")

# --- build season-level batting table (all-time, from selected scope) ---
season_bat = (
    balls_f.groupby(["season_id", "batter"], as_index=False)
    .agg(
        matches=("match_id", "nunique"),
        runs=("batter_runs", "sum"),
        balls=("is_legal_ball_faced", "sum"),
        outs=("is_batter_out", "sum"),
    )
)

season_bat["strike_rate"] = np.where(season_bat["balls"] > 0, (season_bat["runs"] / season_bat["balls"]) * 100, np.nan)
season_bat["average"] = np.where(season_bat["outs"] > 0, (season_bat["runs"] / season_bat["outs"]), np.nan)

# --- choose batter list: restrict to meaningful batters (avoid clutter) ---
batter_pool = (
    season_bat.groupby("batter", as_index=False)
    .agg(total_runs=("runs", "sum"), total_balls=("balls", "sum"), total_matches=("matches", "sum"))
)

batter_pool = batter_pool[batter_pool["total_balls"] >= 200].copy()
batter_pool = batter_pool.sort_values("total_runs", ascending=False)

top_batters = batter_pool["batter"].head(50).tolist()

c1, c2 = st.columns([1.8, 1.2], vertical_alignment="center")

with c1:
    selected_batter = st.selectbox(
        "🏏 Select batter (Top 50 by runs in current scope)",
        options=top_batters,
        index=0,
        key="runs_trend_batter"
    )

with c2:
    st.caption("✅ Tip: This list changes based on your Region / Season filters.")

trend_df = season_bat[season_bat["batter"] == selected_batter].copy()
trend_df = trend_df.sort_values("season_id")

# --- chart: runs trend line ---
line = (
    alt.Chart(trend_df)
    .mark_line(point=True)
    .encode(
        x=alt.X("season_id:O", title="Season"),
        y=alt.Y("runs:Q", title="Runs"),
        tooltip=[
            alt.Tooltip("season_id:O", title="Season"),
            alt.Tooltip("matches:Q", title="Matches"),
            alt.Tooltip("runs:Q", title="Runs"),
            alt.Tooltip("balls:Q", title="Balls"),
            alt.Tooltip("strike_rate:Q", title="SR", format=".1f"),
            alt.Tooltip("average:Q", title="Avg", format=".1f"),
            alt.Tooltip("outs:Q", title="Outs"),
        ]
    )
    .properties(height=320)
)

chart_trend = line.configure_view(strokeOpacity=0).configure_axis(labelFontSize=12, titleFontSize=13)

st.altair_chart(chart_trend, use_container_width=True)

with st.expander("🧠 How to read this section", expanded=False):
    st.markdown(
        """
### What this section shows
Runs scored by the selected batter **season by season**.

### How to use it
- Rising trend → improving impact / growing role
- Drop in runs → lower form, fewer matches, or role change

### Read with context
A season with fewer runs can still be good if:
- matches played were fewer
- strike rate stayed high
- average remained stable
        """
    )

# -----------------------------
# SECTION 6: PLAYER DEEP DIVE SUMMARY
# -----------------------------
st.divider()

st.markdown("## 🧠 Player Deep Dive — Summary Card")
st.caption("One batter, full profile: volume + efficiency + pressure + phase impact (stability gated).")

# --- Build batter pool for selection (top 75 by runs in current scope, balls>=200) ---
batter_pool = (
    balls_f.groupby("batter", as_index=False)
    .agg(
        matches=("match_id", "nunique"),
        runs=("batter_runs", "sum"),
        balls=("is_legal_ball_faced", "sum"),
        outs=("is_batter_out", "sum"),
    )
)

batter_pool["strike_rate"] = np.where(batter_pool["balls"] > 0, (batter_pool["runs"] / batter_pool["balls"]) * 100, np.nan)
batter_pool["average"] = np.where(batter_pool["outs"] > 0, (batter_pool["runs"] / batter_pool["outs"]), np.nan)

batter_pool = batter_pool[batter_pool["balls"] >= 200].copy()
batter_pool = batter_pool.sort_values("runs", ascending=False)

top_batters = batter_pool["batter"].head(75).tolist()

selected_batter_deep = st.selectbox(
    "🏏 Select batter (Top 75 by runs in current scope)",
    options=top_batters,
    index=0,
    key="deep_dive_batter"
)

# --- Base profile row (all overs) ---
p = batter_pool[batter_pool["batter"] == selected_batter_deep].copy()
if p.empty:
    st.warning("No batter data found for this selection.")
    st.stop()

p = p.iloc[0].to_dict()

# --- Pressure & boundary features ---
tmp = balls_f[balls_f["batter"] == selected_batter_deep].copy()

tmp["is_dot_ball"] = ((tmp["batter_runs"] == 0) & (tmp["is_legal_ball_faced"] == 1)).astype(int)
tmp["is_four"] = ((tmp["batter_runs"] == 4) & (tmp["is_legal_ball_faced"] == 1)).astype(int)
tmp["is_six"] = ((tmp["batter_runs"] == 6) & (tmp["is_legal_ball_faced"] == 1)).astype(int)

tmp["boundary_runs"] = (tmp["is_four"] * 4 + tmp["is_six"] * 6).astype(int)
tmp["is_boundary_ball"] = (((tmp["batter_runs"] == 4) | (tmp["batter_runs"] == 6)) & (tmp["is_legal_ball_faced"] == 1)).astype(int)

dot_pct = (tmp["is_dot_ball"].sum() / max(1, tmp["is_legal_ball_faced"].sum())) * 100
boundary_pct = (tmp["boundary_runs"].sum() / max(1, tmp["batter_runs"].sum())) * 100

non_boundary_runs = tmp["batter_runs"].sum() - tmp["boundary_runs"].sum()
non_boundary_balls = tmp["is_legal_ball_faced"].sum() - tmp["is_boundary_ball"].sum()
non_boundary_sr = (non_boundary_runs / max(1, non_boundary_balls)) * 100

# --- Phase SRs ---
tmp["phase"] = pd.Series(pd.NA, index=tmp.index)
tmp.loc[tmp["over_number"].between(0, 5), "phase"] = "Powerplay"
tmp.loc[tmp["over_number"].between(6, 14), "phase"] = "Middle"
tmp.loc[tmp["over_number"].between(15, 19), "phase"] = "Death"

phase_kpi = (
    tmp.groupby("phase", as_index=False)
    .agg(
        runs=("batter_runs", "sum"),
        balls=("is_legal_ball_faced", "sum")
    )
)

phase_kpi["sr"] = np.where(phase_kpi["balls"] > 0, (phase_kpi["runs"] / phase_kpi["balls"]) * 100, np.nan)

def get_phase_sr(df, phase_name):
    row = df[df["phase"] == phase_name]
    if row.empty:
        return np.nan
    return float(row["sr"].iloc[0])

pp_sr = get_phase_sr(phase_kpi, "Powerplay")
mid_sr = get_phase_sr(phase_kpi, "Middle")
death_sr = get_phase_sr(phase_kpi, "Death")

# -----------------------------
# KPI STRIP (8 cards)
# -----------------------------
st.markdown("### 📌 Batter KPI Profile")

c1, c2, c3, c4 = st.columns(4, gap="large")
with c1:
    kpi_card("Matches", f"{int(p['matches']):,}", "🧾", KPI_BLUE, desc="Career games in this scope")
with c2:
    kpi_card("Runs", f"{int(p['runs']):,}", "🏏", KPI_PURPLE, desc="Total batting runs")
with c3:
    kpi_card("Strike Rate", f"{p['strike_rate']:.1f}", "⚡", KPI_ORANGE, desc="Runs per 100 balls")
with c4:
    kpi_card("Average", f"{p['average']:.1f}", "🎯", KPI_GREEN, desc="Runs per dismissal")

c5, c6, c7, c8 = st.columns(4, gap="large")
with c5:
    kpi_card("Dot Ball %", f"{dot_pct:.1f}%", "🧱", KPI_RED, desc="Pressure / stagnation")
with c6:
    kpi_card("Boundary %", f"{boundary_pct:.1f}%", "🎯", KPI_ORANGE, desc="Boundary dependency")
with c7:
    kpi_card("Non-Boundary SR", f"{non_boundary_sr:.1f}", "🔁", KPI_BLUE, desc="Rotation speed")
with c8:
    kpi_card("Balls Faced", f"{int(p['balls']):,}", "🟡", KPI_DARK, desc="Total legal balls faced")

st.divider()

# -----------------------------
# PHASE KPI MINI-CARDS
# -----------------------------
st.markdown("### ⏱️ Phase Impact (Strike Rate)")

p1, p2, p3 = st.columns(3, gap="large")

with p1:
    kpi_card("Powerplay SR", f"{pp_sr:.1f}" if not np.isnan(pp_sr) else "—", "🌟", KPI_GREEN, desc="Overs 1–6")
with p2:
    kpi_card("Middle Overs SR", f"{mid_sr:.1f}" if not np.isnan(mid_sr) else "—", "🧠", KPI_BLUE, desc="Overs 7–15")
with p3:
    kpi_card("Death Overs SR", f"{death_sr:.1f}" if not np.isnan(death_sr) else "—", "🔥", KPI_ORANGE, desc="Overs 16–20")

with st.expander("🧠 How to read this profile card", expanded=False):
    st.markdown(
        """
### What this section gives you
A full batter snapshot in one place:
- **Volume:** matches, runs, balls
- **Efficiency:** strike rate, average
- **Pressure:** dot ball %
- **Style:** boundary %, non-boundary SR
- **Situation:** phase SRs (Powerplay / Middle / Death)

### How to use it
✅ Use this as a quick player profile for auctions, matchups and role clarity.  
Example: a batter with high **Death SR** + high **Boundary %** is a strong finisher profile.
        """
    )

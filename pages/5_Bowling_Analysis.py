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
from src.data_loader import load_processed_csv


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


def chart_style_for_topn(n: int) -> dict:
    """
    Horizontal label/number sizing helper.
    Keeps label readability consistent across Top 5 vs Top 10 charts.
    """
    if n <= 5:
        return {"label_size": 12, "text_size": 18}
    return {"label_size": 11, "text_size": 16}


def compute_rank_score(df: pd.DataFrame, metric_col: str, rank_method: str) -> pd.DataFrame:
    """
    Adds a rank_score column depending on ranking method.

    Pure KPI -> rank_score = metric
    Volume-adjusted -> rank_score = metric × √balls

    Note:
    - For bowling metrics where LOWER is better (e.g., economy, strike_rate, runs_per_wicket),
      pass metric_col as a "rank_proxy" where higher = better (e.g., -economy).
    """
    df = df.copy()

    if rank_method.startswith("Pure KPI"):
        df["rank_score"] = df[metric_col]
        return df

    # Volume-adjusted (sample fairness)
    df["vol_weight"] = df["balls"] ** 0.5
    df["rank_score"] = df[metric_col] * df["vol_weight"]
    return df


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
KPI_FILE = "kpi_player_bowling_alltime.csv"

try:
    bowl = load_processed_csv(KPI_FILE)
except FileNotFoundError:
    html_section("Bowling KPI File Not Found")
    html_explain("This tab depends on a precomputed KPI CSV in data/processed_new.")

    st.error(f"Missing file: data/processed_new/{KPI_FILE}")
    st.stop()



# -----------------------------
# Basic cleanup
# -----------------------------
bowl["venue_region"] = bowl["venue_region"].astype(str).str.strip()
bowl["season"] = bowl["season"].astype(str).str.strip()
bowl["bowler"] = bowl["bowler"].astype(str).str.strip()


# ============================================================
# FILTERS (Top section = ONLY Region + Season)
# ============================================================

html_section("Filters")
html_explain(
    "Select the venue region and season scope. Stability filtering is handled automatically to keep comparisons fair."
)

c1, c2 = st.columns([1.2, 1.2])

with c1:
    region_choice = st.selectbox(
        "Venue Region",
        ["All Venues", "India", "Overseas"],
        index=0,
        key="tab5_region",
    )

with c2:
    if region_choice == "All Venues":
        season_list = sorted(
            bowl["season"].unique().tolist(), key=lambda x: (x != "All Time", x)
        )
    else:
        season_list = sorted(
            bowl[bowl["venue_region"] == region_choice]["season"].unique().tolist(),
            key=lambda x: (x != "All Time", x),
        )

    # If "All Time" doesn't exist for some reason, we still keep the list safe.
    season_choice = st.selectbox(
        "Season",
        season_list,
        index=0,
        key="tab5_season",
    )


# -----------------------------
# Apply scope filters (Region + Season)
# -----------------------------
bowl_scope = bowl.copy()

if region_choice != "All Venues":
    bowl_scope = bowl_scope[bowl_scope["venue_region"] == region_choice].copy()

bowl_scope = bowl_scope[bowl_scope["season"] == season_choice].copy()

# ============================================================
# STABILITY CONTROL (Blended Rule: Median balls + innings floor)
# ============================================================

html_section("Stability Control (Fair Rankings)")
html_explain(
    "Bowling KPIs can swing heavily in small samples. We apply a stability filter so leaderboards reflect repeatable performance."
)

# -----------------------------
# Data-driven threshold: median balls in current scope
# -----------------------------
median_balls_threshold = int(round(float(bowl_scope["balls"].median())))

# -----------------------------
# Blended innings rule
# All Time -> strict floor (credibility)
# Single season -> flexible floor (coverage)
# -----------------------------
if str(season_choice).strip() == "All Time":
    innings_floor = 20
else:
    innings_floor = 6

# Apply stability filters
stable_scope = bowl_scope.copy()
stable_scope = stable_scope[stable_scope["balls"] >= median_balls_threshold].copy()
stable_scope = stable_scope[stable_scope["innings_bowled"] >= int(innings_floor)].copy()

# Badge for transparency
html_badge(
    f"Stability filter applied: balls ≥ <b>{median_balls_threshold}</b> "
    f"and innings_bowled ≥ <b>{innings_floor}</b>"
)

# -----------------------------
# Detailed explanation + examples
# -----------------------------
with st.expander("ℹ️ Why stability filtering matters (with examples)", expanded=False):
    st.markdown(
        f"""
### Why we apply stability filters
Bowling metrics like **economy**, **strike rate**, and **3+ wicket frequency** are naturally volatile.

A bowler can look *elite* in a short burst of matches, but that doesn’t always represent a repeatable skill level.
To keep leaderboards credible, we filter out small samples.

---

## The stability rules used in Tab 5

### ✅ Rule 1: Median balls threshold (data-driven)
We require:

**balls ≥ median(balls) within the selected scope**

This means a bowler must have bowled at least the **typical workload** for that scope.

**Example**  
If you select:
- Venue Region = **{region_choice}**
- Season = **{season_choice}**

…and the median balls bowled across bowlers in that scope is:

**median balls = {median_balls_threshold}**

Then anyone with fewer than {median_balls_threshold} balls is excluded.

This prevents cases where someone ranks highly after bowling only a handful of overs.

---

### ✅ Rule 2: Innings floor (repeatability)
In addition to balls, we require an innings minimum:

**innings_bowled ≥ {innings_floor}**

Why innings matters:
- **balls** measures total volume  
- **innings** measures repeatability across multiple spells/matches  

A bowler with high impact across many innings is far more reliable than one who appears strong in just a few matches.

---

## Why “All Time” is stricter than single season

### ✅ All Time scope (strict)
When you select **All Time**, we set:

**innings_bowled ≥ 20**

Because All Time leaderboards are expected to reflect **long-term performance**.
A bowler with 8–12 innings might still look extreme due to variance.

**Worked example**  
Bowler A:
- balls = 250  
- innings = 11  
- wickets = 16  
- strike rate looks amazing  

But 11 innings is still a small career window, so we don’t rank it as “All Time elite”.

---

### ✅ Single season scope (flexible)
When you select a specific season, we set:

**innings_bowled ≥ 6**

Because a season is short. If we demand 20 innings in a single season,
most seasons would have too few bowlers left and charts would break.

---

## Bottom line
This blended approach keeps the dashboard balanced:

✅ **Credible All Time rankings**  
✅ **Usable season-level rankings**  
✅ **No misleading small-sample leaderboards**
        """
    )

# -----------------------------
# Stop if stability removes everything
# -----------------------------
if len(stable_scope) == 0:
    st.warning(
        "No bowlers meet the stability thresholds in this scope. "
        "Try switching venue region or season."
    )
    st.stop()

st.divider()


# ============================================================
# SUMMARY TILES (sanity check)
# ============================================================

html_section("Bowling Summary")
html_explain("A quick scope overview after applying stability filtering.")

total_bowlers = int(stable_scope["bowler"].nunique())
total_balls = int(stable_scope["balls"].sum())
total_wkts = int(stable_scope["wickets"].sum())
avg_econ = float(stable_scope["economy"].mean())

a, b, c, d = st.columns(4)

with a:
    metric_tile(f"{total_bowlers:,}", "Bowlers in scope after stability filter.")

with b:
    metric_tile(f"{total_balls:,}", "Total balls in scope (stable sample).")

with c:
    metric_tile(f"{total_wkts:,}", "Total wickets taken (bowler-attributed).")

with d:
    metric_tile(f"{avg_econ:.2f}", "Average economy across stable bowlers.")

st.divider()


# ============================================================
# SECTION 1: Impact Leaders (Wickets)
# ============================================================

html_section("Impact Leaders (Wickets)")
html_explain(
    "Who are the highest wicket-taking bowlers in the selected scope (after stability filtering)?"
)

top_n_wkts = st.selectbox(
    "Top Bowlers",
    [5, 10],
    index=0,
    key="tab5_topn_wickets",
)

style_w = chart_style_for_topn(int(top_n_wkts))

impact_w = (
    stable_scope.sort_values("wickets", ascending=False)
    .head(int(top_n_wkts))
    .copy()
)

order_w = impact_w["bowler"].tolist()

BASE_H = 180
ROW_H = 36
chart_h_w = int(BASE_H + (ROW_H * int(top_n_wkts)))

base_w = (
    alt.Chart(impact_w)
    .mark_bar()
    .encode(
        y=alt.Y(
            "bowler:N",
            sort=order_w,
            title="",
            axis=alt.Axis(labelFontSize=style_w["label_size"]),
        ),
        x=alt.X("wickets:Q", title="Wickets"),
        color=alt.value("#ad8ad0"),  # purple (Tab 4 Light theme)
        tooltip=[
            alt.Tooltip("bowler:N", title="Bowler"),
            alt.Tooltip("wickets:Q", title="Wickets", format=",.0f"),
            alt.Tooltip("balls:Q", title="Balls", format=",.0f"),
            alt.Tooltip("innings_bowled:Q", title="Innings", format=",.0f"),
            alt.Tooltip("economy:Q", title="Economy", format=".2f"),
            alt.Tooltip("bowling_strike_rate:Q", title="Strike Rate", format=".2f"),
            alt.Tooltip("runs_per_wicket:Q", title="Runs/Wicket", format=".2f"),
        ],
    )
    .properties(height=chart_h_w)
)

labels_w = (
    alt.Chart(impact_w)
    .transform_calculate(x_pos="datum.wickets * 0.80")
    .mark_text(color="#1b1b1b", fontSize=style_w["text_size"])
    .encode(
        y=alt.Y("bowler:N", sort=order_w, title=""),
        x=alt.X("x_pos:Q"),
        text=alt.Text("wickets:Q", format=",.0f"),
    )
)

st.altair_chart(apply_altair_theme(base_w + labels_w), use_container_width=True)

st.caption(
    "Wickets shown here are bowler-attributed wickets from the dataset. "
    "Totals may differ slightly from official records depending on dataset coverage and attribution rules."
)

st.divider()


# ============================================================
# SECTION 2: Control & Efficiency (Economy + Strike Rate)
# ============================================================

html_section("Control & Efficiency (Economy + Strike Rate)")
html_explain(
    "This section highlights bowlers who combine control (economy) with wicket-taking speed (strike rate). "
    "Lower values are better for both, so we provide ranking methods to keep comparisons stable."
)

rank_method_ctrl = st.radio(
    "Ranking Method (applies to both charts)",
    ["Pure KPI (Metric only)", "Volume-adjusted (Metric × √balls)"],
    index=1,
    horizontal=True,
    key="tab5_sec2_rank_method",
)

left, gap, right = st.columns([1, 0.12, 1])
with gap:
    st.markdown("")

FIXED_H = 340

# -----------------------------
# Chart A: Economy (lower better)
# -----------------------------
with left:
    st.markdown("### Economy (Runs per Over)")

    top_n_econ = st.selectbox(
        "Top Bowlers",
        [5, 10],
        index=0,
        key="tab5_topn_econ",
    )

    econ_df = stable_scope[
        ["bowler", "economy", "balls", "innings_bowled", "wickets", "runs_conceded"]
    ].copy()

    econ_df = econ_df.dropna(subset=["economy"]).copy()

    # lower economy is better -> use negative proxy for ranking
    econ_df["rank_proxy"] = -econ_df["economy"]
    econ_df = compute_rank_score(econ_df, "rank_proxy", rank_method_ctrl)

    econ_df = (
        econ_df.sort_values("rank_score", ascending=False)
        .head(int(top_n_econ))
        .copy()
    )

    # Visual order by economy (lowest first)
    econ_df = econ_df.sort_values("economy", ascending=True).reset_index(drop=True)
    order_econ = econ_df["bowler"].tolist()

    style_e = chart_style_for_topn(int(top_n_econ))

    econ_base = (
        alt.Chart(econ_df)
        .mark_bar()
        .encode(
            x=alt.X(
                "bowler:N",
                sort=order_econ,
                title="",
                axis=alt.Axis(labelAngle=-45, labelFontSize=style_e["label_size"]),
            ),
            y=alt.Y("economy:Q", title="Economy"),
            color=alt.value("#4f93c7"),  # blue
            tooltip=[
                alt.Tooltip("bowler:N", title="Bowler"),
                alt.Tooltip("economy:Q", title="Economy", format=".2f"),
                alt.Tooltip("balls:Q", title="Balls", format=",.0f"),
                alt.Tooltip("innings_bowled:Q", title="Innings", format=",.0f"),
                alt.Tooltip("wickets:Q", title="Wickets", format=",.0f"),
                alt.Tooltip("rank_score:Q", title="Ranking Score", format=",.0f"),
            ],
        )
        .properties(height=FIXED_H)
    )

    econ_labels = (
        alt.Chart(econ_df)
        .transform_calculate(y_pos="datum.economy * 0.65")
        .mark_text(color="#1b1b1b", fontSize=style_e["text_size"])
        .encode(
            x=alt.X("bowler:N", sort=order_econ, axis=alt.Axis(labelAngle=-45)),
            y=alt.Y("y_pos:Q"),
            text=alt.Text("economy:Q", format=".2f"),
        )
    )

    st.altair_chart(apply_altair_theme(econ_base + econ_labels), use_container_width=True)
    st.caption("Lower economy = better run control per over.")


# -----------------------------
# Chart B: Strike Rate (lower better)
# -----------------------------
with right:
    st.markdown("### Bowling Strike Rate (Balls per Wicket)")

    top_n_sr = st.selectbox(
        "Top Bowlers",
        [5, 10],
        index=0,
        key="tab5_topn_sr",
    )

    sr_df = stable_scope[
        ["bowler", "bowling_strike_rate", "balls", "innings_bowled", "wickets", "runs_conceded"]
    ].copy()

    sr_df = sr_df.dropna(subset=["bowling_strike_rate"]).copy()

    # lower strike rate is better -> use negative proxy for ranking
    sr_df["rank_proxy"] = -sr_df["bowling_strike_rate"]
    sr_df = compute_rank_score(sr_df, "rank_proxy", rank_method_ctrl)

    sr_df = (
        sr_df.sort_values("rank_score", ascending=False)
        .head(int(top_n_sr))
        .copy()
    )

    # Visual order by strike rate (lowest first)
    sr_df = sr_df.sort_values("bowling_strike_rate", ascending=True).reset_index(drop=True)
    order_sr = sr_df["bowler"].tolist()

    style_s = chart_style_for_topn(int(top_n_sr))

    sr_base = (
        alt.Chart(sr_df)
        .mark_bar()
        .encode(
            x=alt.X(
                "bowler:N",
                sort=order_sr,
                title="",
                axis=alt.Axis(labelAngle=-45, labelFontSize=style_s["label_size"]),
            ),
            y=alt.Y("bowling_strike_rate:Q", title="Strike Rate (balls/wicket)"),
            color=alt.value("#ff9a45"),  # orange
            tooltip=[
                alt.Tooltip("bowler:N", title="Bowler"),
                alt.Tooltip("bowling_strike_rate:Q", title="Strike Rate", format=".2f"),
                alt.Tooltip("balls:Q", title="Balls", format=",.0f"),
                alt.Tooltip("innings_bowled:Q", title="Innings", format=",.0f"),
                alt.Tooltip("wickets:Q", title="Wickets", format=",.0f"),
                alt.Tooltip("rank_score:Q", title="Ranking Score", format=",.0f"),
            ],
        )
        .properties(height=FIXED_H)
    )

    sr_labels = (
        alt.Chart(sr_df)
        .transform_calculate(y_pos="datum.bowling_strike_rate * 0.65")
        .mark_text(color="#1b1b1b", fontSize=style_s["text_size"])
        .encode(
            x=alt.X("bowler:N", sort=order_sr, axis=alt.Axis(labelAngle=-45)),
            y=alt.Y("y_pos:Q"),
            text=alt.Text("bowling_strike_rate:Q", format=".1f"),
        )
    )

    st.altair_chart(apply_altair_theme(sr_base + sr_labels), use_container_width=True)
    st.caption("Lower strike rate = faster wicket-taking frequency.")

st.divider()


# ============================================================
# SECTION 3: Pressure Building (Dot Ball %)
# ============================================================

html_section("Pressure Building (Dot Ball %)")
html_explain(
    "Dot balls are the clearest signal of pressure. This section highlights bowlers who consistently win deliveries."
)

top_n_dot = st.selectbox(
    "Top Bowlers",
    [5, 10],
    index=0,
    key="tab5_topn_dot",
)

dot_df = stable_scope[
    ["bowler", "dot_ball_pct", "dot_balls", "balls", "innings_bowled", "wickets", "economy"]
].copy()

dot_df = dot_df.dropna(subset=["dot_ball_pct"]).copy()

dot_df = dot_df.sort_values("dot_ball_pct", ascending=False).head(int(top_n_dot)).copy()
order_dot = dot_df["bowler"].tolist()

style_d = chart_style_for_topn(int(top_n_dot))
chart_h_dot = int(BASE_H + (ROW_H * int(top_n_dot)))

dot_base = (
    alt.Chart(dot_df)
    .mark_bar()
    .encode(
        y=alt.Y(
            "bowler:N",
            sort=order_dot,
            title="",
            axis=alt.Axis(labelFontSize=style_d["label_size"]),
        ),
        x=alt.X("dot_ball_pct:Q", title="Dot Ball %"),
        color=alt.value("#55b3a8"),  # teal
        tooltip=[
            alt.Tooltip("bowler:N", title="Bowler"),
            alt.Tooltip("dot_ball_pct:Q", title="Dot Ball %", format=".1f"),
            alt.Tooltip("dot_balls:Q", title="Dot Balls", format=",.0f"),
            alt.Tooltip("balls:Q", title="Balls", format=",.0f"),
            alt.Tooltip("innings_bowled:Q", title="Innings", format=",.0f"),
            alt.Tooltip("economy:Q", title="Economy", format=".2f"),
            alt.Tooltip("wickets:Q", title="Wickets", format=",.0f"),
        ],
    )
    .properties(height=chart_h_dot)
)

dot_labels = (
    alt.Chart(dot_df)
    .transform_calculate(x_pos="datum.dot_ball_pct * 0.80")
    .mark_text(color="#1b1b1b", fontSize=style_d["text_size"])
    .encode(
        y=alt.Y("bowler:N", sort=order_dot, title=""),
        x=alt.X("x_pos:Q"),
    )
    .transform_calculate(label="round(datum.dot_ball_pct) + '%'")
    .encode(text="label:N")
)

st.altair_chart(apply_altair_theme(dot_base + dot_labels), use_container_width=True)
st.caption("Higher dot ball % = greater ability to build sustained pressure.")

st.divider()

# ============================================================
# SECTION 4: Match-Winner Signal (3+ Wickets Frequency)
# ============================================================

html_section("Match-Winner Signal (3+ Wickets Frequency)")
html_explain(
    "This section highlights bowlers who frequently deliver big-impact spells (3+ wickets in an innings). "
    "These are match-turning performances rather than steady accumulation."
)

required_cols_3p = ["innings_3plus_wkts", "pct_innings_3plus"]
missing_cols_3p = [c for c in required_cols_3p if c not in stable_scope.columns]

if missing_cols_3p:
    st.info(
        "3+ wickets KPI columns not found in this KPI file. "
        f"Missing columns: {missing_cols_3p}"
    )
else:
    top_n_3p = st.selectbox(
        "Top Bowlers",
        [5, 10],
        index=0,
        key="tab5_topn_3plus",
    )

    three_df = stable_scope[
        [
            "bowler",
            "pct_innings_3plus",
            "innings_3plus_wkts",
            "innings_bowled",
            "balls",
            "wickets",
        ]
    ].copy()

    # Safety cleanup
    three_df["innings_bowled"] = pd.to_numeric(three_df["innings_bowled"], errors="coerce").fillna(0)
    three_df["innings_3plus_wkts"] = pd.to_numeric(three_df["innings_3plus_wkts"], errors="coerce").fillna(0)
    three_df["pct_innings_3plus"] = pd.to_numeric(three_df["pct_innings_3plus"], errors="coerce").fillna(0)

    # Remove empty sample bowlers (extra safety)
    three_df = three_df[three_df["innings_bowled"] > 0].copy()

    # Top N by % frequency
    three_df = (
        three_df.sort_values("pct_innings_3plus", ascending=False)
        .head(int(top_n_3p))
        .copy()
    )

    order_3p = three_df["bowler"].tolist()

    style_3 = chart_style_for_topn(int(top_n_3p))
    chart_h_3p = int(BASE_H + (ROW_H * int(top_n_3p)))

    base_3p = (
        alt.Chart(three_df)
        .mark_bar()
        .encode(
            y=alt.Y(
                "bowler:N",
                sort=order_3p,
                title="",
                axis=alt.Axis(labelFontSize=style_3["label_size"]),
            ),
            x=alt.X("pct_innings_3plus:Q", title="3+ Wicket Innings Frequency (%)"),
            color=alt.value("#e05a5b"),  # ✅ fixed: no TAB5_COLORS dependency
            tooltip=[
                alt.Tooltip("bowler:N", title="Bowler"),
                alt.Tooltip("pct_innings_3plus:Q", title="3+ Innings %", format=".1f"),
                alt.Tooltip("innings_3plus_wkts:Q", title="3+ Wkt Innings", format=",.0f"),
                alt.Tooltip("innings_bowled:Q", title="Innings Bowled", format=",.0f"),
                alt.Tooltip("balls:Q", title="Balls", format=",.0f"),
                alt.Tooltip("wickets:Q", title="Wickets", format=",.0f"),
            ],
        )
        .properties(height=chart_h_3p)
    )

    labels_3p = (
        alt.Chart(three_df)
        .transform_calculate(x_pos="datum.pct_innings_3plus * 0.75")
        .mark_text(color="#1b1b1b", fontSize=style_3["text_size"])
        .encode(
            y=alt.Y("bowler:N", sort=order_3p, title=""),
            x=alt.X("x_pos:Q"),
        )
        .transform_calculate(label="round(datum.pct_innings_3plus) + '%'")
        .encode(text="label:N")
    )

    st.altair_chart(apply_altair_theme(base_3p + labels_3p), use_container_width=True)
    st.caption("Higher = more frequent big-impact 3+ wicket spells per innings.")

st.divider()


# ============================================================
# SECTION 5: Phase Specialists (Powerplay vs Death Wickets)
# ============================================================

html_section("Phase Specialists (Powerplay vs Death Impact)")
html_explain(
    "Some bowlers deliver value in the Powerplay, while others dominate at the Death. "
    "This section compares wickets and strike rate across phases."
)

required_phase_cols = [
    "wickets_powerplay",
    "wickets_death",
    "sr_powerplay",
    "sr_death",
    "balls_powerplay",
    "balls_death",
]

missing_phase_cols = [c for c in required_phase_cols if c not in stable_scope.columns]

if len(missing_phase_cols) > 0:
    st.info(
        f"Phase KPI columns not found: {missing_phase_cols}. "
        "Make sure the master KPI includes phase metrics before enabling this section."
    )
else:
    top_n_phase = st.selectbox(
        "Top Bowlers",
        [5, 10],
        index=0,
        key="tab5_topn_phase",
    )

    phase_df = stable_scope[
        [
            "bowler",
            "innings_bowled",
            "balls",
            "wickets",
            "wickets_powerplay",
            "wickets_death",
            "sr_powerplay",
            "sr_death",
            "balls_powerplay",
            "balls_death",
        ]
    ].copy()

    # Small additional stability for phase charts:
    # avoid bowlers with almost no phase volume
    # (keeps the visuals believable)
    phase_df = phase_df[(phase_df["balls_powerplay"] >= 12) | (phase_df["balls_death"] >= 12)].copy()

    if len(phase_df) == 0:
        st.warning("No bowlers have enough phase volume for Powerplay/Death comparisons in this scope.")
        st.stop()

    # "Impact proxy": total wickets in PP + Death
    phase_df["phase_wkts_total"] = phase_df["wickets_powerplay"] + phase_df["wickets_death"]

    phase_df = (
        phase_df.sort_values("phase_wkts_total", ascending=False)
        .head(int(top_n_phase))
        .copy()
    )

    # Reshape for grouped bars (wickets)
    wkts_long = pd.DataFrame(
        {
            "bowler": list(phase_df["bowler"]) * 2,
            "phase": (["Powerplay"] * len(phase_df)) + (["Death"] * len(phase_df)),
            "wickets": list(phase_df["wickets_powerplay"]) + list(phase_df["wickets_death"]),
        }
    )

    order_phase = phase_df["bowler"].tolist()

    phase_w_chart = (
        alt.Chart(wkts_long)
        .mark_bar()
        .encode(
            y=alt.Y("bowler:N", sort=order_phase, title=""),
            x=alt.X("wickets:Q", title="Wickets (Phase)"),
            color=alt.Color(
                "phase:N",
                title="",
                scale=alt.Scale(domain=["Powerplay", "Death"], range=["#4f93c7", "#ff9a45"]),
            ),
            tooltip=[
                alt.Tooltip("bowler:N", title="Bowler"),
                alt.Tooltip("phase:N", title="Phase"),
                alt.Tooltip("wickets:Q", title="Wickets", format=",.0f"),
            ],
        )
        .properties(height=int(BASE_H + ROW_H * int(top_n_phase)))
    )

    st.altair_chart(apply_altair_theme(phase_w_chart), use_container_width=True)

    st.caption(
        "Powerplay wickets reflect early breakthroughs. Death wickets reflect end-overs finishing impact. "
        "Phase strike rates are computed from phase balls ÷ phase wickets."
    )

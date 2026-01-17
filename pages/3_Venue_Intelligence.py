import os
import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Venue Intelligence | IPL Strategy Dashboard", layout="wide")

# ✅ KPI Root
PROJECT_ROOT = r"E:\Google Drive\Portfolio Projects\IPL_Strategy_Dashboard"
KPI_ROOT = os.path.join(PROJECT_ROOT, "data", "KPIs")


# ============================================================
# TAB 3: Venue Intelligence (LOCKED + EXPLAINABLE + COLORS)
# ============================================================

# -----------------------------
# HTML DESIGN SYSTEM (Tab 3)
# -----------------------------
def html_title(text):
    st.markdown(
        f"<div style='font-size: 2.0rem; font-weight: 800; color:#111; margin-bottom: 2px;'>{text}</div>",
        unsafe_allow_html=True
    )

def html_subtitle(text):
    st.markdown(
        f"<div style='font-size: 1.15rem; color:#555; margin-top: -2px; margin-bottom: 14px;'>{text}</div>",
        unsafe_allow_html=True
    )

def html_section(text):
    st.markdown(
        f"<div style='font-size: 1.45rem; font-weight: 750; color:#111; margin-top: 6px;'>{text}</div>",
        unsafe_allow_html=True
    )

def html_explain(text):
    st.markdown(
        f"<div style='font-size: 1.1rem; color:#555; margin-top: 4px; margin-bottom: 10px; line-height:1.45;'>{text}</div>",
        unsafe_allow_html=True
    )

def html_note(text, color="#555"):
    st.markdown(
        f"<div style='font-size: 1.1rem; color:{color}; margin-top: 6px; margin-bottom: 8px; line-height:1.45;'>{text}</div>",
        unsafe_allow_html=True
    )

def html_badge(text, bg="#EEF2FF", border="#D9E2FF", color="#2B3A67"):
    st.markdown(
        f"""
        <div style="
            display:inline-block;
            padding: 6px 12px;
            border-radius: 999px;
            background: {bg};
            border: 1px solid {border};
            color: {color};
            font-size: 1.02rem;
            margin: 6px 0px 10px 0px;
        ">
            {text}
        </div>
        """,
        unsafe_allow_html=True
    )

def format_indian_number(n):
    try:
        n = float(n)
    except:
        return str(n)

    if abs(n) < 1000:
        return f"{n:,.0f}"

    x = int(round(n))
    s = str(x)
    last3 = s[-3:]
    rest = s[:-3]
    if rest == "":
        return last3

    parts = []
    while len(rest) > 2:
        parts.append(rest[-2:])
        rest = rest[:-2]
    if rest:
        parts.append(rest)

    return ",".join(parts[::-1]) + "," + last3

# ✅ Metric tile (no top title)
def metric_tile(value, explanation, value_color="#111"):
    st.markdown(
        f"""
        <div style="
            border: 1px solid #EEE;
            border-radius: 14px;
            padding: 16px 16px;
            background: #FFF;
        ">
            <div style="font-size: 2.25rem; font-weight: 800; color: {value_color};">
                {value}
            </div>
            <div style="font-size: 1.1rem; color: #555; margin-top: 10px; line-height: 1.35;">
                {explanation}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# -----------------------------
# Primary spectrum palette
# -----------------------------
PRIMARY_PALETTE = ["#1F77B4", "#2CA02C", "#FF7F0E", "#9467BD", "#D62728", "#17BECF"]

# Meaningful colors for decisions
COLOR_CHASE = "#2CA02C"     # green
COLOR_DEFEND = "#D62728"    # red
COLOR_NEUTRAL = "#FF7F0E"   # orange/amber
COLOR_INFO = "#1F77B4"      # blue


# -----------------------------
# Load KPI files
# -----------------------------
@st.cache_data(show_spinner=False)
def load_tab3_files(region_choice: str):
    region_key_map = {
        "All Venues": "all",
        "India": "india",
        "Overseas": "overseas"
    }
    key = region_key_map.get(region_choice, "all")

    base_path = r"E:\Google Drive\Portfolio Projects\IPL_Strategy_Dashboard\data\KPIs\master_kpis\venue"

    df_summary = pd.read_csv(fr"{base_path}\tab3_venue_summary_{key}.csv")
    df_cd = pd.read_csv(fr"{base_path}\tab3_venue_chase_defend_{key}.csv")
    df_toss = pd.read_csv(fr"{base_path}\tab3_venue_toss_advantage_{key}.csv")

    for d in [df_summary, df_cd, df_toss]:
        d["season"] = d["season"].astype(str)

    return df_summary, df_cd, df_toss

def season_sort_key(x):
    if str(x).lower() == "all time":
        return -1
    try:
        return int(x)
    except:
        return 999999


# -----------------------------
# Ball-by-ball minimal load (for innings highs/lows)
# -----------------------------
@st.cache_data(show_spinner=False)
def load_ball_master_for_innings():
    path = r"E:\Google Drive\Portfolio Projects\IPL_Strategy_Dashboard\data\processed\phase1_master_clean_validated_all_venues_v3.csv"
    df = pd.read_csv(
        path,
        usecols=["match_id", "innings", "venue_region", "season_id_x", "total_runs"]
    )

    df["venue_region"] = df["venue_region"].astype(str).str.strip()
    df["season_id_x"] = df["season_id_x"].astype(str)
    df["innings"] = pd.to_numeric(df["innings"], errors="coerce").fillna(0).astype(int)
    df["total_runs"] = pd.to_numeric(df["total_runs"], errors="coerce").fillna(0)

    return df


# -----------------------------
# Header
# -----------------------------
html_title("Venue Intelligence")
html_subtitle("Every chart answers one practical question: what decision should a team make at this venue?")
st.markdown("")


# -----------------------------
# Filters
# -----------------------------
c1, c2, c3 = st.columns([1.2, 1.0, 1.0])

with c1:
    region_choice = st.selectbox(
        "Venue Region",
        ["All Venues", "India", "Overseas"],
        index=0,
        key="tab3_region"
    )

df_summary, df_cd, df_toss = load_tab3_files(region_choice)

available_seasons = sorted(df_summary["season"].unique().tolist(), key=season_sort_key)
if "All Time" not in available_seasons:
    available_seasons = ["All Time"] + available_seasons

with c2:
    season_choice = st.selectbox(
        "Season",
        available_seasons,
        index=0,
        key="tab3_season"
    )

with c3:
    top_n = st.selectbox(
        "Top Venues",
        [10, 15, 20],
        index=0,
        key="tab3_topn"
    )

summary_f = df_summary[df_summary["season"] == season_choice].copy()
cd_f = df_cd[df_cd["season"] == season_choice].copy()
toss_f = df_toss[df_toss["season"] == season_choice].copy()


# -----------------------------
# Stability thresholds (LOCKED)
# -----------------------------
if season_choice == "All Time":
    min_matches_chase_bias = 20
    min_matches_toss = 25
else:
    min_matches_chase_bias = 5
    min_matches_toss = 5

html_badge(f"Showing: <b>{region_choice}</b> • <b>{season_choice}</b>")


# -----------------------------
# High/Low single innings totals (completed innings only)
# -----------------------------
ball_min = load_ball_master_for_innings()
ball_scope = ball_min.copy()

if region_choice != "All Venues":
    ball_scope = ball_scope[ball_scope["venue_region"] == region_choice].copy()

if season_choice != "All Time":
    ball_scope = ball_scope[ball_scope["season_id_x"] == str(season_choice)].copy()

innings_totals = (
    ball_scope.groupby(["match_id", "innings"], as_index=False)
    .agg(
        innings_total_runs=("total_runs", "sum"),
        balls=("total_runs", "count")
    )
)

innings_totals = innings_totals[innings_totals["innings"].isin([1, 2])].copy()
innings_totals_completed = innings_totals[innings_totals["balls"] >= 60].copy()

if len(innings_totals_completed) > 0:
    highest_innings_total = int(innings_totals_completed["innings_total_runs"].max())
    lowest_innings_total = int(innings_totals_completed["innings_total_runs"].min())
else:
    highest_innings_total = 0
    lowest_innings_total = 0


# -----------------------------
# Key Stats Tiles
# -----------------------------
total_matches = int(summary_f["matches"].sum()) if len(summary_f) else 0
unique_venues = int(summary_f["venue"].nunique()) if len(summary_f) else 0
avg_match_runs = float(summary_f["avg_total_runs_per_match"].mean()) if len(summary_f) else 0
avg_run_rate = float(summary_f["avg_run_rate"].mean()) if len(summary_f) else 0

r1a, r1b, r1c, r1d = st.columns(4)
with r1a:
    metric_tile(format_indian_number(total_matches), "Total matches in the selected scope.", value_color=COLOR_INFO)
with r1b:
    metric_tile(format_indian_number(unique_venues), "Unique grounds covered in this selection.", value_color=COLOR_INFO)
with r1c:
    metric_tile(f"{avg_match_runs:,.1f}", "Average match runs (both innings combined).", value_color="#111")
with r1d:
    metric_tile(f"{avg_run_rate:,.2f}", "Overall scoring speed (runs per over).", value_color="#111")

r2a, r2b, r2c, r2d = st.columns(4)
with r2a:
    metric_tile(format_indian_number(highest_innings_total), "Highest team score in a single innings.", value_color=COLOR_CHASE)
with r2b:
    metric_tile(format_indian_number(lowest_innings_total), "Lowest team score in a single innings (min 60 balls).", value_color=COLOR_DEFEND)
with r2c:
    st.empty()
with r2d:
    st.empty()

st.divider()


# ============================================================
# SECTION: Most Used Venues
# ============================================================
html_section("Most Used Venues")
html_explain("Question answered: where do teams play the most? These venues have the largest sample size.")

top_venues = summary_f.sort_values("matches", ascending=False).head(int(top_n)).copy()

if len(top_venues) > 0:
    fig_top = px.bar(
        top_venues,
        x="matches",
        y="venue",
        orientation="h",
        text="matches",
        color_discrete_sequence=[PRIMARY_PALETTE[0]],
        height=460
    )
    fig_top.update_traces(textposition="outside")
    fig_top.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        yaxis_title="",
        xaxis_title="Matches",
        yaxis=dict(categoryorder="total ascending")
    )
    st.plotly_chart(fig_top, use_container_width=True)

    html_note("So what? Venues with more matches give more reliable strategy signals.", color="#555")
else:
    st.info("No venue data available for the selected filters.")

st.markdown("")


# ============================================================
# SECTION: Chase vs Defend Bias (Meaningful + Sorted by ABS bias)
# ============================================================
html_section("Chase vs Defend Bias")
html_explain(
    f"Question answered: if you win the toss here, should you generally chase or defend? "
    f"Only venues with at least <b>{min_matches_chase_bias}</b> matches are shown."
)

cd_chart = cd_f.copy()
if len(cd_chart) > 0:
    cd_chart = cd_chart[cd_chart["matches"] >= min_matches_chase_bias].copy()

    cd_chart["recommendation"] = cd_chart["chase_defend_delta_pct"].apply(
        lambda x: "Chase" if x >= 8 else ("Defend" if x <= -8 else "Neutral")
    )

    cd_chart["signal_strength"] = cd_chart["chase_defend_delta_pct"].abs()

    cd_chart = cd_chart.sort_values("signal_strength", ascending=False).head(int(top_n)).copy()

    color_map = {"Chase": COLOR_CHASE, "Defend": COLOR_DEFEND, "Neutral": COLOR_NEUTRAL}

if len(cd_chart) > 0:
    fig_bias = px.bar(
        cd_chart,
        x="chase_defend_delta_pct",
        y="venue",
        orientation="h",
        color="recommendation",
        color_discrete_map=color_map,
        hover_data={
            "matches": True,
            "chasing_win_pct": True,
            "defending_win_pct": True,
            "other_result_pct": True,
            "recommendation": True
        },
        height=480
    )

    fig_bias.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        yaxis_title="",
        xaxis_title="Bias (%): Chasing win% − Defending win%",
        legend_title="Recommendation",
        yaxis=dict(categoryorder="total ascending")
    )

    st.plotly_chart(fig_bias, use_container_width=True)

    html_note(
        "<b>How to interpret:</b> "
        "<span style='color:#2CA02C; font-weight:700;'>Green</span> → chasing historically wins more. "
        "<span style='color:#D62728; font-weight:700;'>Red</span> → defending historically wins more. "
        "<span style='color:#FF7F0E; font-weight:700;'>Amber</span> → no strong bias.",
        color="#555"
    )

    html_note(
        "So what? This helps a captain decide the safer toss call. "
        "If bias is strong and sample size is stable, follow the recommended strategy.",
        color="#555"
    )
else:
    st.info("Not enough venues meet the stability threshold for chase vs defend. Try All Time.")

st.markdown("")


# ============================================================
# SECTION: Toss Influence (Split into Impact + Preference)
# ============================================================
html_section("Toss Influence")
html_explain(
    f"Question answered: (1) does the toss matter here? (2) what do captains prefer after winning the toss? "
    f"Only venues with at least <b>{min_matches_toss}</b> matches are shown."
)

toss_scope = toss_f.copy()
if len(toss_scope) > 0:
    toss_scope = toss_scope[toss_scope["matches"] >= min_matches_toss].copy()

unknown_avg = float(toss_f["toss_decision_unknown_pct"].mean()) if len(toss_f) else 0.0
if unknown_avg <= 2:
    dq_color = "#0F766E"
    dq_text = "Good"
elif unknown_avg <= 5:
    dq_color = "#B45309"
    dq_text = "Okay"
else:
    dq_color = "#B91C1C"
    dq_text = "Caution"

html_badge(
    f"Decision data quality: <b style='color:{dq_color}'>{dq_text}</b> • Avg unknown: <b>{unknown_avg:.1f}%</b>",
    bg="#FFF7ED", border="#FED7AA", color="#7C2D12"
)

if len(toss_scope) == 0:
    st.info("Not enough venues meet the stability threshold for toss patterns. Try All Time.")
else:
    html_section("Toss Impact (Where it matters most)")
    html_explain("Higher values mean: winning the toss increases your chance of winning the match at this venue.")

    impact_chart = toss_scope.sort_values("toss_win_match_win_pct", ascending=False).head(int(top_n)).copy()

    impact_chart["impact_band"] = impact_chart["toss_win_match_win_pct"].apply(
        lambda x: "High impact" if x >= 55 else ("Low impact" if x <= 45 else "Moderate")
    )

    impact_color_map = {
        "High impact": COLOR_CHASE,
        "Moderate": COLOR_NEUTRAL,
        "Low impact": COLOR_DEFEND
    }

    fig_impact = px.bar(
        impact_chart,
        x="toss_win_match_win_pct",
        y="venue",
        orientation="h",
        color="impact_band",
        color_discrete_map=impact_color_map,
        hover_data={"matches": True, "toss_win_match_win_pct": True},
        height=460
    )
    fig_impact.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        yaxis_title="",
        xaxis_title="Toss winner also won match (%)",
        legend_title="Impact level",
        yaxis=dict(categoryorder="total ascending")
    )
    st.plotly_chart(fig_impact, use_container_width=True)

    html_note(
        "So what? On high-impact venues, toss strategy (and playing conditions) matter more. "
        "On low-impact venues, outcomes depend more on skill and execution than the toss.",
        color="#555"
    )

    st.markdown("")

    html_section("Decision Preference (Captain behavior)")
    html_explain(
        "Preference Index = Field-first% − Bat-first%. "
        "Positive means captains prefer to chase. Negative means captains prefer to defend."
    )

    pref_chart = toss_scope.copy()
    pref_chart["field_first_index"] = pref_chart["toss_win_field_first_pct"] - pref_chart["toss_win_bat_first_pct"]
    pref_chart["preference"] = pref_chart["field_first_index"].apply(
        lambda x: "Prefer Field First" if x >= 10 else ("Prefer Bat First" if x <= -10 else "Mixed")
    )

    pref_color_map = {
        "Prefer Field First": COLOR_CHASE,
        "Prefer Bat First": COLOR_DEFEND,
        "Mixed": COLOR_NEUTRAL
    }

    pref_chart["pref_strength"] = pref_chart["field_first_index"].abs()
    pref_chart = pref_chart.sort_values("pref_strength", ascending=False).head(int(top_n)).copy()

    fig_pref = px.bar(
        pref_chart,
        x="field_first_index",
        y="venue",
        orientation="h",
        color="preference",
        color_discrete_map=pref_color_map,
        hover_data={
            "matches": True,
            "toss_win_field_first_pct": True,
            "toss_win_bat_first_pct": True
        },
        height=460
    )
    fig_pref.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        yaxis_title="",
        xaxis_title="Preference Index (Field% − Bat%)",
        legend_title="Decision pattern",
        yaxis=dict(categoryorder="total ascending")
    )
    st.plotly_chart(fig_pref, use_container_width=True)

    html_note(
        "So what? This shows how captains behave at each venue. "
        "A strong preference often reflects dew, pitch deterioration, or par-score pressure.",
        color="#555"
    )

import os
import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Match & Toss Strategy | IPL Strategy Dashboard", layout="wide")

# ✅ KPI Root
PROJECT_ROOT = r"E:\Google Drive\Portfolio Projects\IPL_Strategy_Dashboard"
KPI_ROOT = os.path.join(PROJECT_ROOT, "data", "KPIs")


# ============================================================
# TAB 2: Match & Toss Strategy (FAST - match_base, Region-aware)
# + Comparison supports All Time / India / Overseas / Seasons
# ============================================================

# -----------------------------
# HTML Design System (Tab 2)
# -----------------------------
def html_title(text):
    st.markdown(
        f"<div style='font-size: 2.0rem; font-weight: 800; color:#111; margin-bottom: 2px;'>{text}</div>",
        unsafe_allow_html=True
    )

def html_subtitle(text):
    st.markdown(
        f"<div style='font-size: 1.15rem; color:#555; margin-top: -2px; margin-bottom: 14px; line-height:1.45;'>{text}</div>",
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

def info_box(text):
    st.markdown(
        f"""
        <div style="
            padding: 14px 16px;
            border-radius: 16px;
            background: #F7F8FA;
            border: 1px solid #E6E8EC;
            font-size: 1.10rem;
            color: #333;
            line-height: 1.55;
            margin-top: 8px;
        ">
            {text}
        </div>
        """,
        unsafe_allow_html=True
    )

def metric_tile(value, explanation, value_color="#111"):
    st.markdown(
        f"""
        <div style="
            border: 1px solid #EEE;
            border-radius: 14px;
            padding: 16px 16px;
            background: #FFF;
        ">
            <div style="font-size: 2.25rem; font-weight: 800; color:{value_color};">
                {value}
            </div>
            <div style="font-size: 1.1rem; color:#555; margin-top: 10px; line-height:1.35;">
                {explanation}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

PRIMARY_PALETTE = ["#1F77B4", "#2CA02C", "#FF7F0E", "#9467BD", "#D62728", "#17BECF"]
COLOR_CHASE = "#2CA02C"
COLOR_DEFEND = "#D62728"
COLOR_NEUTRAL = "#FF7F0E"
COLOR_INFO = "#1F77B4"


# -----------------------------
# Header
# -----------------------------
html_title("Match & Toss Strategy")
html_subtitle("Filter by region + season and compare two selections side-by-side.")
st.markdown("")


# ---------------------------------
# Load match base (All Venues) - small file, fast
# ---------------------------------
match_base_path = os.path.join(KPI_ROOT, "master_kpis", "matches", "phase2_match_base_all_venues.csv")
match_base = pd.read_csv(match_base_path)

# Standardize + derived columns
match_base["season_id"] = pd.to_numeric(match_base["season_id"], errors="coerce").astype("Int64")
match_base["toss_decision"] = match_base["toss_decision"].astype(str).str.lower().str.strip()
match_base["toss_strategy"] = match_base["toss_decision"].map({"field": "Chase", "bat": "Defend"}).fillna("Unknown")
match_base["toss_winner_won_match"] = (match_base["toss_winner"] == match_base["match_winner"]).astype(int)
match_base["venue_region"] = match_base["venue_region"].astype(str).str.strip()

# Global season list (for comparison dropdown)
all_seasons = sorted([int(x) for x in match_base["season_id"].dropna().unique().tolist()])


# ---------------------------------
# Region dropdown (main scope filter)
# ---------------------------------
region_options = ["All Venues", "India", "Overseas"]

cR1, cR2 = st.columns([1.2, 3.8])
with cR1:
    selected_region = st.selectbox(
        "Venue Region",
        options=region_options,
        index=0,
        key="region_toss_kpi"
    )

with cR2:
    st.markdown(
        "<div style='font-size: 1.02rem; color:#666; padding-top: 28px; line-height:1.4;'>"
        "Use this filter to see toss behavior in India-only, Overseas-only, or all matches."
        "</div>",
        unsafe_allow_html=True
    )

# Apply main region filter
if selected_region != "All Venues":
    match_base_scope = match_base[match_base["venue_region"] == selected_region].copy()
else:
    match_base_scope = match_base.copy()

# Season dropdown relevant to selected region
scope_seasons = sorted([int(x) for x in match_base_scope["season_id"].dropna().unique().tolist()])
scope_season_options = ["All Time"] + scope_seasons


# ---------------------------------
# Season dropdown (main scope)
# ---------------------------------
cS1, cS2 = st.columns([1.2, 3.8])
with cS1:
    selected_season = st.selectbox(
        "Season",
        options=scope_season_options,
        index=0,
        key="season_toss_main_kpi"
    )

with cS2:
    st.markdown(
        "<div style='font-size: 1.02rem; color:#666; padding-top: 28px; line-height:1.4;'>"
        "This filters all metrics below. Keep <b>All Time</b> for the most stable signal."
        "</div>",
        unsafe_allow_html=True
    )

# Apply main season filter
if selected_season == "All Time":
    mb = match_base_scope.copy()
    scope_label = f"{selected_region} • All Time"
else:
    mb = match_base_scope[match_base_scope["season_id"] == int(selected_season)].copy()
    scope_label = f"{selected_region} • Season {selected_season}"


if len(mb) == 0:
    st.warning("No data available for the selected filters.")
else:
    matches_in_scope = int(mb["match_id"].nunique())

    toss_winner_win_pct = (mb["toss_winner_won_match"].mean() * 100)
    toss_loser_win_pct = 100 - toss_winner_win_pct

    cd = (
        mb[mb["toss_strategy"].isin(["Chase", "Defend"])]
        .groupby("toss_strategy", as_index=False)
        .agg(win_pct=("toss_winner_won_match", "mean"))
    )
    cd["win_pct"] = cd["win_pct"] * 100

    chase_win = float(cd.loc[cd["toss_strategy"] == "Chase", "win_pct"].values[0]) if "Chase" in cd["toss_strategy"].values else 0.0
    defend_win = float(cd.loc[cd["toss_strategy"] == "Defend", "win_pct"].values[0]) if "Defend" in cd["toss_strategy"].values else 0.0

    chase_advantage = chase_win - defend_win

    if chase_advantage >= 1:
        best_call = "Chase"
        best_color = COLOR_CHASE
    elif chase_advantage <= -1:
        best_call = "Defend"
        best_color = COLOR_DEFEND
    else:
        best_call = "Neutral"
        best_color = COLOR_NEUTRAL

    html_badge(f"Showing: <b>{scope_label}</b> • Matches: <b>{matches_in_scope}</b>")

    # Tiles row 1
    m1, m2, m3, m4 = st.columns(4)

    with m1:
        metric_tile(f"{toss_winner_win_pct:.2f}%", "If you win the toss, chance you also win the match.", value_color=COLOR_INFO)
    with m2:
        metric_tile(f"{toss_loser_win_pct:.2f}%", "If you lose the toss, chance you still win the match.", value_color=COLOR_INFO)
    with m3:
        metric_tile(f"{chase_win:.2f}%", "Toss-winner win% when choosing to chase.", value_color=COLOR_CHASE)
    with m4:
        metric_tile(f"{defend_win:.2f}%", "Toss-winner win% when choosing to defend.", value_color=COLOR_DEFEND)

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    # Tiles row 2
    m5, m6, m7, m8 = st.columns(4)

    with m5:
        adv_color = COLOR_CHASE if chase_advantage >= 0 else COLOR_DEFEND
        metric_tile(f"{chase_advantage:.2f}%", "Chase win% − Defend win% (toss winner only).", value_color=adv_color)

    with m6:
        metric_tile(best_call, "Suggested toss call based on historical outcomes.", value_color=best_color)

    with m7:
        metric_tile(f"{matches_in_scope}", "Matches used for calculations in this scope.", value_color="#111")

    with m8:
        st.empty()

    info_box(
        "<b>So what?</b> This section helps decide whether the toss matters and which toss decision tends to work better. "
        "When chase advantage is strong, choosing to field first has historically been more successful for toss winners."
    )

    st.divider()

    # ============================================================
    # Comparison section
    # ============================================================
    html_section("Compare two selections")
    html_explain("Compare region vs region, or season vs season, using the same toss metrics.")

    comparison_options = ["All Time", "India", "Overseas"] + all_seasons

    cA, cB, cC = st.columns([1.2, 1.2, 2.6])

    with cA:
        compare_a = st.selectbox(
            "Compare A",
            options=comparison_options,
            index=0,
            key="compare_a_toss_kpi"
        )

    with cB:
        compare_b = st.selectbox(
            "Compare B",
            options=comparison_options,
            index=1 if len(comparison_options) > 1 else 0,
            key="compare_b_toss_kpi"
        )

    with cC:
        st.markdown(
            "<div style='font-size: 1.02rem; color:#666; padding-top: 28px; line-height:1.4;'>"
            "Examples: India vs Overseas, All Time vs India, or 2016 vs 2020."
            "</div>",
            unsafe_allow_html=True
        )

    def compute_metrics(selection, base_df):
        temp = base_df.copy()

        if selection in ["India", "Overseas"]:
            temp = temp[temp["venue_region"] == selection].copy()
            label = f"{selection} (All Time)"
        elif selection == "All Time":
            label = "All Time"
        else:
            temp = temp[temp["season_id"] == int(selection)].copy()
            label = f"Season {selection}"

        if len(temp) == 0:
            return label, 0, 0, 0, 0, 0, 0

        matches = int(temp["match_id"].nunique())

        toss_win_pct = (temp["toss_winner_won_match"].mean() * 100)
        toss_lose_pct = 100 - toss_win_pct

        cd_temp = (
            temp[temp["toss_strategy"].isin(["Chase", "Defend"])]
            .groupby("toss_strategy", as_index=False)
            .agg(win_pct=("toss_winner_won_match", "mean"))
        )
        cd_temp["win_pct"] = cd_temp["win_pct"] * 100

        chase = float(cd_temp.loc[cd_temp["toss_strategy"] == "Chase", "win_pct"].values[0]) if "Chase" in cd_temp["toss_strategy"].values else 0.0
        defend = float(cd_temp.loc[cd_temp["toss_strategy"] == "Defend", "win_pct"].values[0]) if "Defend" in cd_temp["toss_strategy"].values else 0.0
        advantage = chase - defend

        return label, matches, toss_win_pct, toss_lose_pct, chase, defend, advantage

    label_a, matches_a, toss_win_a, toss_lose_a, chase_a, defend_a, adv_a = compute_metrics(compare_a, match_base)
    label_b, matches_b, toss_win_b, toss_lose_b, chase_b, defend_b, adv_b = compute_metrics(compare_b, match_base)

    html_section("Comparison summary")
    html_explain("This highlights the practical difference between two selections.")

    x1, x2, x3, x4 = st.columns(4)
    with x1:
        metric_tile(label_a, "Selection A", value_color=PRIMARY_PALETTE[0])
    with x2:
        metric_tile(matches_a, "Matches (A)", value_color="#111")
    with x3:
        metric_tile(f"{toss_win_a:.2f}%", "Win toss → win match (A)", value_color=COLOR_INFO)
    with x4:
        metric_tile(f"{adv_a:.2f}%", "Chase advantage (A)", value_color=COLOR_CHASE if adv_a >= 0 else COLOR_DEFEND)

    y1, y2, y3, y4 = st.columns(4)
    with y1:
        metric_tile(label_b, "Selection B", value_color=PRIMARY_PALETTE[3])
    with y2:
        metric_tile(matches_b, "Matches (B)", value_color="#111")
    with y3:
        metric_tile(f"{toss_win_b:.2f}%", "Win toss → win match (B)", value_color=COLOR_INFO)
    with y4:
        metric_tile(f"{adv_b:.2f}%", "Chase advantage (B)", value_color=COLOR_CHASE if adv_b >= 0 else COLOR_DEFEND)

    info_box(
        "<b>So what?</b> Use this to compare conditions: India vs Overseas, or different seasons. "
        "If one selection shows much higher chase advantage, choosing to field first has historically worked better there."
    )

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    show_advanced = st.toggle(
        "Show advanced visuals",
        value=False,
        key="toggle_toss_advanced_kpi"
    )

    if show_advanced:
        bar_df = pd.DataFrame([
            {"Selection": label_a, "Metric": "Win toss → win match", "Value": round(toss_win_a, 2)},
            {"Selection": label_a, "Metric": "Chase win% (toss winner)", "Value": round(chase_a, 2)},
            {"Selection": label_a, "Metric": "Defend win% (toss winner)", "Value": round(defend_a, 2)},
            {"Selection": label_a, "Metric": "Chase advantage", "Value": round(adv_a, 2)},

            {"Selection": label_b, "Metric": "Win toss → win match", "Value": round(toss_win_b, 2)},
            {"Selection": label_b, "Metric": "Chase win% (toss winner)", "Value": round(chase_b, 2)},
            {"Selection": label_b, "Metric": "Defend win% (toss winner)", "Value": round(defend_b, 2)},
            {"Selection": label_b, "Metric": "Chase advantage", "Value": round(adv_b, 2)},
        ])

        fig1 = px.bar(
            bar_df,
            x="Metric",
            y="Value",
            color="Selection",
            barmode="group",
            title="A vs B — Outcome comparison",
            text="Value",
            color_discrete_sequence=[PRIMARY_PALETTE[0], PRIMARY_PALETTE[1]]
        )

        fig1.update_traces(
            texttemplate="%{text:.2f}%",
            textposition="outside",
            cliponaxis=False
        )

        fig1.update_layout(
            height=360,
            margin=dict(l=10, r=10, t=60, b=10),
            yaxis_title="Percentage",
            xaxis_title="",
            yaxis=dict(range=[0, max(bar_df["Value"].max() + 10, 60)])
        )

        st.plotly_chart(fig1, use_container_width=True)

        info_box(
            "<b>So what?</b> The bars make it easier to visually compare the two selections without reading every number."
        )

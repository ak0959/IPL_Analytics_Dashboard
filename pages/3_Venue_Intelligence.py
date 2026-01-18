import streamlit as st
import altair as alt
import pandas as pd

import src.data_loader as dl


# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="Venue Intelligence", page_icon="🏟️", layout="wide")


# -----------------------------
# SLIGHTLY DEEPER PASTEL COLORS (Not too light)
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


# KPI number colors (logic based)
KPI_BLUE = "#2563EB"      # total/sample
KPI_PURPLE = "#7C3AED"    # unique venues
KPI_DARK = "#111827"      # neutral
KPI_ORANGE = "#F59E0B"    # pace
KPI_GREEN = "#16A34A"     # high record (good)
KPI_RED = "#DC2626"       # low record (bad)


# -----------------------------
# PAGE HEADER
# -----------------------------
st.markdown(
    """
    <div style="padding: 0.2rem 0 0.8rem 0;">
        <div style="font-size: 2.1rem; font-weight: 800;">🏟️ Venue Intelligence</div>
        <div style="font-size: 1.05rem; opacity: 0.85;">
            Scoring patterns, chase bias & toss impact by ground — KPI-first, decision-ready.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.divider()


# -----------------------------
# LOAD DATA (Tab 3 KPIs)
# -----------------------------
df_most_used = dl.load_csv("tab3_venue_kpis", "venue_most_used.csv")
df_bias = dl.load_csv("tab3_venue_kpis", "venue_chase_defend_bias.csv")
df_toss = dl.load_csv("tab3_venue_kpis", "venue_toss_influence.csv")
df_phase = dl.load_csv("tab3_venue_kpis", "venue_phase_scoring.csv")
df_avg_inns = dl.load_csv("tab3_venue_kpis", "venue_avg_innings_1v2.csv")

matches = dl.load_master_matches()

# --- Apply venue cleanup mapping (same as KPI build) ---
vmap = dl.load_csv("venue_cleanup_map.csv")  # from data/processed_new/
venue_map = dict(zip(vmap["venue_raw"], vmap["venue_clean"]))

matches["venue"] = matches["venue"].astype(str).str.strip()
matches["venue_region"] = matches["venue_region"].astype(str).str.strip()

matches["venue"] = matches["venue"].map(venue_map).fillna(matches["venue"])


# -----------------------------
# FILTERS
# -----------------------------
c1, c2, c3, c4 = st.columns([1.3, 1.1, 1.1, 1.5], gap="large")

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
    min_matches = st.slider("🧱 Min matches (for bias charts)", 10, 50, 20, 5)

with c4:
    st.caption("✅ Tab 3 is powered by precomputed venue KPI files (fast + cloud-safe).")

st.divider()


# -----------------------------
# APPLY FILTERS
# -----------------------------
matches_f = matches.copy()

if region != "All":
    matches_f = matches_f[matches_f["venue_region"] == region]

if season_id != "All":
    matches_f = matches_f[matches_f["season_id"] == season_id]

match_ids = set(matches_f["match_id"].unique().tolist())

# filter KPI tables by venue scope
bias_f = df_bias[df_bias["venue"].isin(matches_f["venue"].unique())].copy()
toss_f = df_toss[df_toss["venue"].isin(matches_f["venue"].unique())].copy()
most_used_f = df_most_used[df_most_used["venue"].isin(matches_f["venue"].unique())].copy()
avg_inns_f = df_avg_inns[df_avg_inns["venue"].isin(matches_f["venue"].unique())].copy()
phase_f = df_phase[df_phase["venue"].isin(matches_f["venue"].unique())].copy()

# For scoring KPIs, use balls master filtered by match_id
balls = dl.load_master_balls()
balls = balls[(balls["is_super_over"] == False) & (balls["match_id"].isin(match_ids))].copy()


# -----------------------------
# KPI CARD STYLING (COLOR VALUE)
# -----------------------------
def kpi_card(label, value, emoji="✅", value_color="#111"):
    st.markdown(
        f"""
        <div style="
            background: rgba(255,255,255,0.75);
            border: 1px solid rgba(0,0,0,0.06);
            border-radius: 18px;
            padding: 16px 16px 14px 16px;
            box-shadow: 0 8px 22px rgba(0,0,0,0.06);
            height: 110px;
        ">
            <div style="font-size: 1.60rem; font-weight: 850; line-height: 1; color:{value_color};">
                {value}
            </div>
            <div style="margin-top: 8px; font-size: 0.95rem; opacity: 0.78;">
                {emoji} {label}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# -----------------------------
# KPI CALCS (Screenshot KPIs)
# -----------------------------
total_matches = matches_f["match_id"].nunique()
unique_grounds = matches_f["venue"].nunique()

avg_match_runs = balls.groupby("match_id")["total_runs"].sum().mean()
overall_rpo = (balls["total_runs"].sum() / len(balls)) * 6

inn_tot = (
    balls.groupby(["match_id", "innings", "team_batting"], as_index=False)["total_runs"]
    .sum()
    .rename(columns={"total_runs": "innings_runs"})
)

highest_innings = inn_tot["innings_runs"].max()

legal = balls[(balls["is_wide_ball"] == False) & (balls["is_no_ball"] == False)].copy()
inn_legal = (
    legal.groupby(["match_id", "innings", "team_batting"], as_index=False)
    .agg(innings_runs=("total_runs", "sum"), legal_balls=("total_runs", "size"))
)
lowest_innings_60 = inn_legal.loc[inn_legal["legal_balls"] >= 60, "innings_runs"].min()


# -----------------------------
# KPI GRID (6 cards)
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

r1 = st.columns(4, gap="large")
with r1[0]:
    kpi_card("Total matches in selection", f"{total_matches:,}", "🧾", KPI_BLUE)
with r1[1]:
    kpi_card("Unique grounds covered", f"{unique_grounds:,}", "🏟️", KPI_PURPLE)
with r1[2]:
    kpi_card("Average match runs (both innings)", f"{avg_match_runs:,.1f}", "📈", KPI_DARK)
with r1[3]:
    kpi_card("Overall scoring speed (runs/over)", f"{overall_rpo:,.2f}", "⚡", KPI_ORANGE)

r2 = st.columns(4, gap="large")
with r2[0]:
    kpi_card("Highest team score in a single innings", f"{int(highest_innings):,}", "🔥", KPI_GREEN)
with r2[1]:
    kpi_card("Lowest team score (min 60 balls)", f"{int(lowest_innings_60):,}", "🧊", KPI_RED)
with r2[2]:
    st.empty()
with r2[3]:
    st.empty()

st.divider()


# -----------------------------
# SECTION: MOST USED VENUES
# -----------------------------
h1, h2 = st.columns([3, 1], vertical_alignment="center")

with h1:
    st.markdown("## 🏟️ Most Used Venues")
    st.caption("Question answered: where do teams play the most? These venues have the largest sample size.")

with h2:
    venue_scope = st.radio(
        "Venue Scope",
        options=["India 🇮🇳", "Overseas ✈️"],
        index=0,
        horizontal=True,
        label_visibility="collapsed",
    )

    top_choice = st.selectbox("🎯 Show Top", [5, 10], index=0)

def is_overseas_venue(v: str) -> bool:
    v = str(v)
    return any(tag in v for tag in [", UAE", ", SA", "Abu Dhabi", "Dubai", "Sharjah"])

most_used_scoped = most_used_f.copy()
most_used_scoped["is_overseas"] = most_used_scoped["venue"].apply(is_overseas_venue)

if venue_scope == "India 🇮🇳":
    most_used_scoped = most_used_scoped[most_used_scoped["is_overseas"] == False]
else:
    most_used_scoped = most_used_scoped[most_used_scoped["is_overseas"] == True]

most_used_plot = most_used_scoped.sort_values("matches", ascending=False).head(top_choice).copy()
most_used_plot["rank"] = range(1, len(most_used_plot) + 1)

base_bars = (
    alt.Chart(most_used_plot)
    .mark_bar(cornerRadiusEnd=6)
    .encode(
        y=alt.Y("venue:N", sort="-x", title=None, axis=alt.Axis(labelLimit=500)),
        x=alt.X("matches:Q", title="Matches"),
        color=alt.Color("rank:O", scale=alt.Scale(range=LIGHT_RAINBOW), legend=None),
        tooltip=["venue:N", "matches:Q"]
    )
)

text_labels = (
    alt.Chart(most_used_plot)
    .mark_text(align="left", dx=6, fontSize=14)
    .encode(
        y=alt.Y("venue:N", sort="-x"),
        x=alt.X("matches:Q"),
        text=alt.Text("matches:Q")
    )
)

chart_most_used = (base_bars + text_labels).properties(height=280)
chart_most_used = chart_most_used.configure_view(strokeOpacity=0).configure_axisY(labelPadding=12)

st.altair_chart(chart_most_used, use_container_width=True)
st.caption("✅ Key insight: Venues with more matches give more reliable strategy signals.")
st.divider()


# -----------------------------
# SECTION: CHASE vs DEFEND BIAS
# -----------------------------
st.markdown("## 🧭 Chase vs Defend Bias")
st.caption("Question answered: if you win the toss here, should you generally chase or defend?")

bias_plot = bias_f.copy()
bias_plot = bias_plot[bias_plot["matches"] >= min_matches].copy()

bias_plot["abs_bias"] = bias_plot["bias"].abs()
bias_plot = bias_plot.sort_values("abs_bias", ascending=False).head(10).copy()
bias_plot["recommendation"] = bias_plot["bias"].apply(lambda x: "Chase" if x >= 0 else "Defend")

bars = (
    alt.Chart(bias_plot)
    .mark_bar(cornerRadiusEnd=6)
    .encode(
        y=alt.Y("venue:N", sort=alt.SortField(field="bias", order="descending"), title=None, axis=alt.Axis(labelLimit=500)),
        x=alt.X("bias:Q", title="Bias (% points)  →  Chase (+)  |  Defend (-)"),
        color=alt.condition(
            alt.datum.bias >= 0,
            alt.value(PASTEL_GREEN),
            alt.value(PASTEL_RED)
        ),
        tooltip=[
            "venue:N",
            alt.Tooltip("matches:Q", title="Matches"),
            alt.Tooltip("bias:Q", format=".1f", title="Bias"),
            alt.Tooltip("recommendation:N", title="Recommendation"),
        ]
    )
    .properties(height=360)
)

zero_line = (
    alt.Chart(pd.DataFrame({"bias": [0]}))
    .mark_rule(strokeWidth=2, opacity=0.35)
    .encode(x="bias:Q")
)

chart_bias = (zero_line + bars)
chart_bias = chart_bias.configure_view(strokeOpacity=0).configure_axisY(labelPadding=12)

st.altair_chart(chart_bias, use_container_width=True)
st.caption("✅ How to read: Green = chase-friendly. Red = defend-friendly. Bigger bar = stronger advantage.")
st.divider()


# -----------------------------
# SECTION: TOSS INFLUENCE
# -----------------------------
st.markdown("## 🪙 Toss Influence")
st.caption("Question answered: (1) does toss matter here? (2) what do captains prefer after winning the toss?")

toss_plot = toss_f.copy()
toss_plot = toss_plot[toss_plot["matches"] >= max(10, min_matches)].copy()

toss_plot["toss_impact_pct"] = toss_plot["toss_win_match_rate"] * 100
toss_plot["impact_level"] = toss_plot["toss_impact_pct"].apply(lambda x: "High impact" if x >= 55 else "Moderate")

toss_plot = toss_plot.sort_values("toss_impact_pct", ascending=False).head(10).copy()
y_order = toss_plot["venue"].tolist()

st.markdown("### Toss Impact (Where it matters most)")
st.caption("Higher values mean: winning the toss increases your chance of winning the match at this venue.")

bars = (
    alt.Chart(toss_plot)
    .mark_bar(cornerRadiusEnd=6)
    .encode(
        y=alt.Y("venue:N", sort=y_order, title=None, axis=alt.Axis(labelLimit=500)),
        x=alt.X("toss_impact_pct:Q", title="Toss winner also won match (%)"),
        color=alt.Color(
            "impact_level:N",
            scale=alt.Scale(domain=["High impact", "Moderate"], range=[PASTEL_GREEN, PASTEL_BLUE]),
            legend=alt.Legend(title="Impact level")
        ),
        tooltip=[
            "venue:N",
            alt.Tooltip("matches:Q", title="Matches"),
            alt.Tooltip("toss_impact_pct:Q", format=".1f", title="Toss impact (%)"),
        ],
    )
    .properties(height=340)
)

labels = (
    alt.Chart(toss_plot)
    .mark_text(align="left", dx=6, fontSize=14)
    .encode(
        y=alt.Y("venue:N", sort=y_order),
        x=alt.X("toss_impact_pct:Q"),
        text=alt.Text("toss_impact_pct:Q", format=".1f"),
    )
)

chart_toss_impact = (bars + labels)
chart_toss_impact = chart_toss_impact.configure_view(strokeOpacity=0).configure_axisY(labelPadding=12)

st.altair_chart(chart_toss_impact, use_container_width=True)
st.caption("✅ Key insight: On high-impact venues, toss strategy (and conditions) matter more. On low-impact venues, execution matters more than the toss.")
st.divider()


# -----------------------------
# SECTION: DECISION PREFERENCE
# -----------------------------
st.markdown("## 🧠 Decision Preference (Captain behaviour)")
st.caption("Preference Index = Field-first% − Bat-first%. Positive = captains prefer to chase. Negative = captains prefer to defend.")

pref_all = toss_f.copy()
pref_all = pref_all[pref_all["matches"] >= max(10, min_matches)].copy()

top_pos = pref_all.sort_values("decision_preference_index", ascending=False).head(5).copy()
top_neg = pref_all.sort_values("decision_preference_index", ascending=True).head(5).copy()

pref_plot = pd.concat([top_pos, top_neg], ignore_index=True)

top_pos_order = top_pos.sort_values("decision_preference_index", ascending=False)["venue"].tolist()
top_neg_order = top_neg.sort_values("decision_preference_index", ascending=True)["venue"].tolist()
y_order = top_pos_order + top_neg_order

pref_plot["pref_label"] = pref_plot["decision_preference_index"].apply(
    lambda x: "Prefer Field First" if x >= 0 else "Prefer Bat First"
)

bars = (
    alt.Chart(pref_plot)
    .mark_bar(cornerRadiusEnd=6)
    .encode(
        y=alt.Y("venue:N", sort=y_order, title=None, axis=alt.Axis(labelLimit=500)),
        x=alt.X("decision_preference_index:Q", title="Preference Index (Field% − Bat%)"),
        color=alt.condition(
            alt.datum.decision_preference_index >= 0,
            alt.value(PASTEL_GREEN),
            alt.value(PASTEL_RED)
        ),
        tooltip=[
            "venue:N",
            alt.Tooltip("matches:Q", title="Matches"),
            alt.Tooltip("decision_preference_index:Q", format=".1f", title="Preference Index"),
            alt.Tooltip("pref_label:N", title="Decision pattern"),
        ],
    )
    .properties(height=360)
)

zero_line = (
    alt.Chart(pd.DataFrame({"x": [0]}))
    .mark_rule(strokeWidth=2, opacity=0.35)
    .encode(x="x:Q")
)

labels = (
    alt.Chart(pref_plot)
    .mark_text(align="left", dx=6, fontSize=14)
    .encode(
        y=alt.Y("venue:N", sort=y_order),
        x=alt.X("decision_preference_index:Q"),
        text=alt.Text("decision_preference_index:Q", format=".1f"),
    )
)

chart_pref = (zero_line + bars + labels)
chart_pref = chart_pref.configure_view(strokeOpacity=0).configure_axisY(labelPadding=12)

st.altair_chart(chart_pref, use_container_width=True)
st.caption("✅ Key insight: Strong field-first venues often indicate dew or better chasing conditions. Strong bat-first venues indicate scoreboard pressure or pitch deterioration.")
st.divider()

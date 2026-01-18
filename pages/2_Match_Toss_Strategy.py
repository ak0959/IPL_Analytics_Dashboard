import streamlit as st
import pandas as pd

import src.data_loader as dl


# =========================================================
# Page Config
# =========================================================
st.set_page_config(page_title="Match & Toss Strategy", page_icon="🪙", layout="wide")


# =========================================================
# Slightly deeper pastel palette (same family as Tab 3)
# =========================================================
PASTEL_GREEN = "#6EE7B7"
PASTEL_RED = "#FDA4AF"
PASTEL_BLUE = "#93C5FD"
PASTEL_ORANGE = "#FCD34D"
PASTEL_PURPLE = "#A5B4FC"
PASTEL_DARK = "#0f172a"


# =========================================================
# Page Header (modern)
# =========================================================
st.markdown(
    """
    <div style="padding: 0.2rem 0 0.8rem 0;">
        <div style="font-size: 2.1rem; font-weight: 800;">🪙 Match & Toss Strategy 🏏</div>
        <div style="font-size: 1.05rem; opacity: 0.85;">
            Toss impact, decision preference, and chase vs defend outcomes — KPI-first, decision-ready 🎯
        </div>
    </div>
    """,
    unsafe_allow_html=True
)
st.divider()


# =========================================================
# Global UI Styling (cards + colorful accents)
# =========================================================
st.markdown(
    f"""
    <style>
    .kpi-card {{
        background: rgba(255,255,255,0.75);
        border: 1px solid rgba(0,0,0,0.06);
        border-radius: 18px;
        padding: 16px 16px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        min-height: 125px;
    }}
    .kpi-title {{
        font-size: 0.92rem;
        color: #334155;
        margin-bottom: 10px;
        font-weight: 800;
    }}
    .kpi-value {{
        font-size: 2.2rem;
        font-weight: 900;
        color: {PASTEL_DARK};
        line-height: 1.05;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }}
    .kpi-value-green {{
        color: #16a34a;
    }}
    .kpi-value-red {{
        color: #dc2626;
    }}
    .kpi-value-blue {{
        color: #2563eb;
    }}
    .kpi-value-orange {{
        color: #f59e0b;
    }}
    .kpi-value-purple {{
        color: #7c3aed;
    }}

    .kpi-split {{
        font-size: 1.05rem;
        font-weight: 850;
        color: {PASTEL_DARK};
        margin-top: 2px;
        line-height: 1.2;
    }}
    .kpi-sub {{
        font-size: 0.82rem;
        color: #64748b;
        margin-top: 10px;
        line-height: 1.35;
    }}

    .chip {{
        display: inline-block;
        padding: 6px 10px;
        border-radius: 999px;
        font-size: 0.8rem;
        font-weight: 700;
        margin-right: 8px;
        margin-bottom: 8px;
        background: #f1f5f9;
        color: #0f172a;
        border: 1px solid #e2e8f0;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# Load Data
# =========================================================
df = dl.load_match_toss_base()
teams = dl.load_csv("master3_teams.csv")

team_map = dict(zip(teams["team_id"], teams["team_name"]))

# map ids -> names for readability
for col in ["team_batting", "team_bowling", "match_winner", "toss_winner"]:
    df[col] = df[col].map(team_map).fillna(df[col].astype(str))

df["toss_decision"] = df["toss_decision"].astype(str).str.lower().str.strip()
df["result"] = df["result"].astype(str).str.lower().str.strip()


# =========================================================
# Filters (consistent order: Venue Region then Season)
# =========================================================
fcol1, fcol2 = st.columns(2)

with fcol1:
    region_options = ["All Regions"] + sorted(df["venue_region"].dropna().unique().tolist())
    selected_region = st.selectbox("🌍 Venue Region", region_options, index=0)

with fcol2:
    season_options = ["All Time"] + sorted(df["season_id"].dropna().unique().tolist())
    selected_season = st.selectbox("📅 Season", season_options, index=0)

f = df.copy()
if selected_region != "All Regions":
    f = f[f["venue_region"] == selected_region]

if selected_season != "All Time":
    f = f[f["season_id"] == selected_season]


# =========================================================
# Core Toss KPIs
# =========================================================
f_valid = f.dropna(subset=["toss_winner", "match_winner"])

toss_win_rate = (f_valid["toss_winner"] == f_valid["match_winner"]).mean() if len(f_valid) else 0.0

decision_counts = f["toss_decision"].value_counts(dropna=True)
field_pct = decision_counts.get("field", 0) / decision_counts.sum() if decision_counts.sum() else 0.0
bat_pct = decision_counts.get("bat", 0) / decision_counts.sum() if decision_counts.sum() else 0.0

chase_matches = f_valid[f_valid["toss_decision"] == "field"]
defend_matches = f_valid[f_valid["toss_decision"] == "bat"]

chase_win_pct = (chase_matches["toss_winner"] == chase_matches["match_winner"]).mean() if len(chase_matches) else 0.0
defend_win_pct = (defend_matches["toss_winner"] == defend_matches["match_winner"]).mean() if len(defend_matches) else 0.0


# =========================================================
# Result quality KPIs
# =========================================================
match_count = f["match_id"].nunique()

no_result_count = (f["result"] == "no result").sum()
tie_count = (f["result"] == "tie").sum()

# Super over count: compute from master2 (match_id-level only)
balls = dl.load_master_balls()
balls_scope = balls[balls["match_id"].isin(f["match_id"].unique())]
super_over_match_ids = balls_scope.loc[balls_scope["is_super_over"] == True, "match_id"].unique()
super_over_count = len(super_over_match_ids)

avg_win_runs = f["win_by_runs"].dropna().mean() if "win_by_runs" in f else 0.0
avg_win_wkts = f["win_by_wickets"].dropna().mean() if "win_by_wickets" in f else 0.0


# =========================================================
# Strategy Insight (simple, crisp)
# =========================================================
if chase_win_pct > defend_win_pct:
    insight = "🎯 Chasing looks stronger here — toss winners should usually field first."
elif defend_win_pct > chase_win_pct:
    insight = "🧱 Defending holds up better here — batting first is not a bad call."
else:
    insight = "⚖️ Toss decision impact is balanced — focus more on venue + matchups."


# =========================================================
# Scope Chip
# =========================================================
st.markdown(
    f"""
    <div style="margin: 6px 0 16px 0;">
        <span class="chip">📌 Showing: <b>{selected_region}</b> · <b>{selected_season}</b></span>
        <span class="chip">🧾 Matches: <b>{match_count}</b></span>
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# KPI Row 1 (3 cards) — Toss Impact
# =========================================================
st.markdown("")
r1c1, r1c2, r1c3 = st.columns(3)

with r1c1:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">🪙 Toss Winner Wins</div>
            <div class="kpi-value kpi-value-blue">{toss_win_rate*100:.1f}%</div>
            <div class="kpi-sub">How often the toss winner also wins the match.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with r1c2:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">🧠 Toss Decision Preference</div>
            <div class="kpi-split">🏃 Field: <span style="color:#2563eb;font-weight:900;">{field_pct*100:.1f}%</span></div>
            <div class="kpi-split">🏏 Bat: <span style="color:#7c3aed;font-weight:900;">{bat_pct*100:.1f}%</span></div>
            <div class="kpi-sub">What captains choose after winning the toss.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with r1c3:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">🎯 Chase vs Defend (Toss Winner)</div>
            <div class="kpi-split">🏃 Chase: <span style="color:#16a34a;font-weight:900;">{chase_win_pct*100:.1f}%</span></div>
            <div class="kpi-split">🧱 Defend: <span style="color:#dc2626;font-weight:900;">{defend_win_pct*100:.1f}%</span></div>
            <div class="kpi-sub">Toss winner success when choosing field vs bat.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# KPI Row 2 (3 cards) — Result quality + Win margins
# =========================================================
st.markdown("")
r2c1, r2c2, r2c3 = st.columns(3)

with r2c1:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">🌧️ No Result (Count)</div>
            <div class="kpi-value kpi-value-orange">{no_result_count}</div>
            <div class="kpi-sub">Matches abandoned / no result in this scope.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with r2c2:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">🤝 Tie + ⚡ Super Over</div>
            <div class="kpi-split">🤝 Ties: <span style="color:#7c3aed;font-weight:900;">{tie_count}</span></div>
            <div class="kpi-split">⚡ Super Overs: <span style="color:#2563eb;font-weight:900;">{super_over_count}</span></div>
            <div class="kpi-sub">Close finishes and tiebreaker matches.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with r2c3:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">📏 Avg Win Margins</div>
            <div class="kpi-split">🧱 Runs: <span style="color:#16a34a;font-weight:900;">{avg_win_runs:.1f}</span></div>
            <div class="kpi-split">🏃 Wkts: <span style="color:#2563eb;font-weight:900;">{avg_win_wkts:.1f}</span></div>
            <div class="kpi-sub">Typical defend margin vs typical chase margin.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.markdown("")
st.info(f"🧠 Key Insight: {insight}")

st.markdown("---")
st.subheader("🆚 Compare 2 Seasons (Strategy Shift)")
st.caption("Compare how toss calls and outcomes changed between two seasons.")

# Season options (numeric only, no All Time)
season_list = sorted(df["season_id"].dropna().unique().tolist())

cA, cB = st.columns(2)
with cA:
    season_a = st.selectbox("Season A", season_list, index=0, key="season_a")
with cB:
    season_b = st.selectbox("Season B", season_list, index=min(1, len(season_list)-1), key="season_b")


def compute_season_kpis(base_df: pd.DataFrame, season_id: int) -> dict:
    s = base_df[base_df["season_id"] == season_id].copy()
    s_valid = s.dropna(subset=["toss_winner", "match_winner"])

    # Decision preference
    dec_counts = s["toss_decision"].value_counts(dropna=True)
    field_pct_s = dec_counts.get("field", 0) / dec_counts.sum() if dec_counts.sum() else 0.0
    bat_pct_s = dec_counts.get("bat", 0) / dec_counts.sum() if dec_counts.sum() else 0.0

    # Chase vs Defend success (toss winner)
    chase_s = s_valid[s_valid["toss_decision"] == "field"]
    defend_s = s_valid[s_valid["toss_decision"] == "bat"]
    chase_win_s = (chase_s["toss_winner"] == chase_s["match_winner"]).mean() if len(chase_s) else 0.0
    defend_win_s = (defend_s["toss_winner"] == defend_s["match_winner"]).mean() if len(defend_s) else 0.0

    # Margins
    avg_runs_s = s["win_by_runs"].dropna().mean()
    avg_wkts_s = s["win_by_wickets"].dropna().mean()

    return {
        "Season": season_id,
        "Field %": round(field_pct_s * 100, 1),
        "Bat %": round(bat_pct_s * 100, 1),
        "Chase Win % (Toss Winner)": round(chase_win_s * 100, 1),
        "Defend Win % (Toss Winner)": round(defend_win_s * 100, 1),
        "Avg Win Runs": round(avg_runs_s, 1) if pd.notna(avg_runs_s) else None,
        "Avg Win Wkts": round(avg_wkts_s, 1) if pd.notna(avg_wkts_s) else None,
    }


# Comparison KPIs (cards, not table)
a = compute_season_kpis(df, season_a)
b = compute_season_kpis(df, season_b)

st.markdown("")
k1, k2, k3 = st.columns(3)

with k1:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">🧠 Toss Decision Preference</div>
            <div class="kpi-split">🅰️ {a['Season']} → Field <span style="color:#2563eb;font-weight:900;">{a['Field %']:.1f}%</span> | Bat <span style="color:#7c3aed;font-weight:900;">{a['Bat %']:.1f}%</span></div>
            <div class="kpi-split">🅱️ {b['Season']} → Field <span style="color:#2563eb;font-weight:900;">{b['Field %']:.1f}%</span> | Bat <span style="color:#7c3aed;font-weight:900;">{b['Bat %']:.1f}%</span></div>
            <div class="kpi-sub">How the toss call changed across seasons.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with k2:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">🎯 Chase vs Defend (Toss Winner)</div>
            <div class="kpi-split">🅰️ {a['Season']} → Chase <span style="color:#16a34a;font-weight:900;">{a['Chase Win % (Toss Winner)']:.1f}%</span> | Defend <span style="color:#dc2626;font-weight:900;">{a['Defend Win % (Toss Winner)']:.1f}%</span></div>
            <div class="kpi-split">🅱️ {b['Season']} → Chase <span style="color:#16a34a;font-weight:900;">{b['Chase Win % (Toss Winner)']:.1f}%</span> | Defend <span style="color:#dc2626;font-weight:900;">{b['Defend Win % (Toss Winner)']:.1f}%</span></div>
            <div class="kpi-sub">Toss winner success when choosing field vs bat.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with k3:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">📏 Avg Win Margins</div>
            <div class="kpi-split">🅰️ {a['Season']} → Runs <span style="color:#16a34a;font-weight:900;">{a['Avg Win Runs']}</span> | Wkts <span style="color:#2563eb;font-weight:900;">{a['Avg Win Wkts']}</span></div>
            <div class="kpi-split">🅱️ {b['Season']} → Runs <span style="color:#16a34a;font-weight:900;">{b['Avg Win Runs']}</span> | Wkts <span style="color:#2563eb;font-weight:900;">{b['Avg Win Wkts']}</span></div>
            <div class="kpi-sub">Typical defend margin vs chase margin.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

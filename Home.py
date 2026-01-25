import streamlit as st

st.set_page_config(page_title="Home | IPL Strategy Dashboard", layout="wide")

# ------------------------------------------------------------
# Minimal CSS (clean + safe)
# ------------------------------------------------------------
st.markdown(
    """
    <style>
      .hero-wrap{
        border: 1px solid #E6E8EC;
        border-radius: 22px;
        padding: 18px 18px;
        background: linear-gradient(135deg, #ffffff 0%, #f6f7ff 35%, #f2fbff 100%);
        box-shadow: 0 8px 22px rgba(15, 23, 42, 0.06);
        margin-bottom: 14px;
      }
      .hero-title{
        font-size: 2.35rem;
        font-weight: 900;
        color: #0f172a;
        margin: 0 0 6px 0;
        line-height: 1.15;
      }
      .hero-sub{
        font-size: 1.06rem;
        color: #475569;
        margin: 0;
        line-height: 1.55;
      }
      .muted{
        font-size: 0.98rem;
        color: #64748b;
        line-height: 1.55;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------
# TITLE ONLY (LOCKED)
# ------------------------------------------------------------
st.markdown(
    """
    <div class="hero-wrap">
      <div class="hero-title">🏏 IPL Strategy Dashboard 🔥</div>
      <div class="hero-sub">📈 Analytics & Predictions (2008 – 2025) • 🎯 Strategy-first</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------
# HOME: EVERYTHING ELSE IN DROPDOWNS (clean + uncluttered)
# ------------------------------------------------------------
with st.expander("🧠 What this dashboard helps you answer", expanded=True):
    st.markdown(
        """
✅ **Before the match:** venue bias, toss impact, phase scoring patterns  
✅ **During the match:** identify conditions, pick the right phase strategy  
✅ **Team strategy:** top batters/bowlers by stability-gated KPI performance  

This app is built to be **KPI-first**, **decision-ready**, and **fast** (no heavy runtime recompute).
        """
    )

with st.expander("🧭 How to use the dashboard (recommended flow)", expanded=False):
    st.markdown(
        """
1) 🌍 **Pick Region + Season** where available  
2) 📌 Start with **Quick Insights** for the scoring environment  
3) 🏟️ Go to **Venue Intelligence** for chase/defend bias  
4) 🏏 Use **Batting Analysis** for batting dominance + profiles  
5) 🎯 Use **Bowling Analysis** for wicket threat + phase specialists  

Tip: always compare players only after the **stability gates** qualify them.
        """
    )

with st.expander("📌 Pages included (what each tab does)", expanded=False):
    st.markdown("Click a page to open it 👇")

    st.page_link("pages/1_All_Seasons_Quick_Insights.py", label="📊 All Seasons – Quick Insights", icon="➡️")
    st.caption("Run trends, phase scoring patterns, global environment overview")

    st.page_link("pages/2_Match_Toss_Strategy.py", label="🧠 Match & Toss Strategy", icon="➡️")
    st.caption("When toss matters and what choices work best by conditions")

    st.page_link("pages/3_Venue_Intelligence.py", label="🏟️ Venue Intelligence", icon="➡️")
    st.caption("Venue bias, chase/defend signals, stability-gated venue KPIs")

    st.page_link("pages/4_Batting_Analysis.py", label="🏏 Batting Analysis", icon="➡️")
    st.caption("Top batters, pressure/boundary profiles, phase dominance, deep dive")

    st.page_link("pages/5_Bowling_Analysis.py", label="🎯 Bowling Analysis", icon="➡️")
    st.caption("Wicket threat, control vs damage, phase specialists, bowler deep dive")


with st.expander("🧾 Data & Rules (stability gates + definitions)", expanded=False):
    st.markdown(
        """
### ✅ Dataset rules (locked)
- **Super overs removed** for standard T20 comparability
- **Legal balls** exclude **wides**
- **Dot balls** counted only on **legal balls**
- **Bowler runs conceded** = batter runs + wide runs + no-ball runs  
  (byes/legbyes are excluded in the baseline model)
- **Bowler wickets** exclude **run out / retired hurt / obstructing the field**

---

### 🧱 Stability gates (why they exist)
Leaderboards can get distorted by tiny samples.  
So most rankings apply **minimum volume filters** (balls / overs / wickets).

✅ Example:  
A bowler with **6 wickets in 2 games** looks elite, but isn't a stable comparison.

---

### 📘 KPI glossary (quick definitions)

**Batting**
- **Runs**: Total runs scored
- **Strike Rate (SR)**: (Runs / Balls) × 100
- **Average (Avg)**: Runs / Outs
- **Dot Ball %**: (Dot balls / Balls) × 100
- **Boundary %**: (Boundary runs / Total runs) × 100
- **Non-Boundary SR**: scoring speed excluding 4s + 6s

**Bowling**
- **Economy (ECON)**: Runs conceded per over
- **Strike Rate (SR)**: Balls per wicket
- **Average (Avg)**: Runs conceded per wicket
- **Dot Ball %**: (Dot balls / Legal balls) × 100
- **Boundary % conceded**: (4s + 6s balls) / Legal balls

---

### ⏱️ Phase mapping (locked)
We use 0-based `over_number` from the dataset:
- **Powerplay** = 0–5 (Overs 1–6)
- **Middle** = 6–14 (Overs 7–15)
- **Death** = 15–19 (Overs 16–20)
        """
    )


st.caption("✅ Home page intentionally minimal. Use sidebar tabs to explore insights.")

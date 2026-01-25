import streamlit as st

st.set_page_config(page_title="Home | IPL Strategy Dashboard", layout="wide")

# ------------------------------------------------------------
# Minimal CSS (clean + colorful, no external assets required)
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
        margin: 0 0 2px 0;
        line-height: 1.55;
      }
      .hero-note{
        font-size: 0.98rem;
        color: #64748b;
        margin-top: 10px;
        line-height: 1.55;
      }
      .pill{
        display: inline-block;
        padding: 6px 10px;
        border-radius: 999px;
        border: 1px solid #E6E8EC;
        background: rgba(255,255,255,0.75);
        font-size: 0.88rem;
        color: #0f172a;
        margin-right: 8px;
        margin-top: 8px;
      }
      .section-h{
        font-size: 1.45rem;
        font-weight: 850;
        color:#0f172a;
        margin: 6px 0 2px 0;
      }
      .section-desc{
        font-size: 1.02rem;
        color:#64748b;
        line-height: 1.65;
        margin-bottom: 10px;
      }
      .card{
        border: 1px solid #E6E8EC;
        border-radius: 18px;
        padding: 16px 16px;
        background: #FFFFFF;
        box-shadow: 0 8px 18px rgba(15, 23, 42, 0.05);
        height: 100%;
      }
      .card-title{
        font-size: 1.05rem;
        font-weight: 850;
        color:#0f172a;
        margin: 0 0 6px 0;
      }
      .card-text{
        font-size: 0.98rem;
        color:#475569;
        line-height: 1.55;
        margin: 0 0 10px 0;
      }
      .badge{
        display:inline-block;
        padding: 4px 9px;
        border-radius: 999px;
        font-size: 0.82rem;
        font-weight: 700;
        border: 1px solid #E6E8EC;
        margin-right: 8px;
      }
      .b-blue{ background: #EFF6FF; color:#1D4ED8; }
      .b-green{ background: #ECFDF5; color:#047857; }
      .b-purple{ background: #F5F3FF; color:#6D28D9; }
      .b-orange{ background: #FFF7ED; color:#C2410C; }
      .footer{
        margin-top: 14px;
        color:#94a3b8;
        font-size: 0.92rem;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------
# HERO
# ------------------------------------------------------------
st.markdown(
    """
    <div class="hero-wrap">
      <div class="hero-title">🏏 IPL Strategy Dashboard 🔥</div>
      <div class="hero-sub">📈 Analytics & Predictions (2008 – 2025) • 🎯 Strategy-first</div>
      <div class="hero-note">
        Built for fast decision-making using <b>precomputed master files</b> and <b>KPI outputs</b>.
        No heavy recomputation during app runtime.
      </div>

      <div>
        <span class="pill">⚡ Fast KPI-first pages</span>
        <span class="pill">🧭 Region-aware insights</span>
        <span class="pill">📊 Altair visuals</span>
        <span class="pill">☁️ Streamlit Cloud ready</span>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------
# QUICK EXPLAINER ROW
# ------------------------------------------------------------
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("Coverage", "2008–2025", help="IPL seasons in scope")
with c2:
    st.metric("Data Model", "Masters + KPIs", help="All pages load from processed files")
with c3:
    st.metric("Runtime", "Instant", help="No heavy groupby on the ball-by-ball master during navigation")
with c4:
    st.metric("Charts", "Altair", help="Consistent visuals across tabs")

st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)

# ------------------------------------------------------------
# SECTIONS
# ------------------------------------------------------------
st.markdown("<div class='section-h'>Dashboard sections</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='section-desc'>Pick a section below or use the sidebar. Each page answers a specific strategy question.</div>",
    unsafe_allow_html=True,
)

def nav_card(title: str, page_path: str, tags: list[str], body: str):
    tags_html = " ".join([f"<span class='badge {t}'>{txt}</span>" for txt, t in tags])
    st.markdown(
        f"""
        <div class="card">
          <div class="card-title">{title}</div>
          <div style="margin-bottom: 10px;">{tags_html}</div>
          <div class="card-text">{body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link(page_path, label=f"Open {title} →", icon="➡️")

g1, g2 = st.columns(2)

with g1:
    nav_card(
        "All Seasons – Quick Insights",
        "pages/1_All_Seasons_Quick_Insights.py",
        tags=[("Overview", "b-blue"), ("Phase runs", "b-purple")],
        body=(
            "A fast snapshot of scoring environment across seasons and regions. "
            "Understand total run trends and where runs come from across phases."
        ),
    )
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    nav_card(
        "Venue Intelligence",
        "pages/3_Venue_Intelligence.py",
        tags=[("Venue bias", "b-green"), ("Chase/Defend", "b-orange")],
        body=(
            "Venue-level strategy signals: stable venues, chase/defend bias, and "
            "toss behavior patterns that affect match-day planning."
        ),
    )

with g2:
    nav_card(
        "Match & Toss Strategy",
        "pages/2_Match_Toss_Strategy.py",
        tags=[("Toss impact", "b-orange"), ("Win probability", "b-blue")],
        body=(
            "Decision support for captains: when toss matters, and what choices "
            "tend to work better by region and season."
        ),
    )
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    nav_card(
        "Batting Analysis",
        "pages/4_Batting_Analysis.py",
        tags=[("Batting KPIs", "b-purple"), ("Player impact", "b-blue")],
        body=(
            "Batter scoring patterns and role impact signals. "
            "Designed for planning innings priorities and identifying key contributors."
        ),
    )

st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

nav_card(
    "Bowling Analysis",
    "pages/5_Bowling_Analysis.py",
    tags=[("Bowling KPIs", "b-green"), ("Pressure + wickets", "b-orange")],
    body=(
        "Wicket-taking impact, economy control, dot-ball pressure, and phase specialists "
        "using fast precomputed bowling KPIs."
    ),
)

st.markdown(
    "<div class='footer'>Tip: If a page looks empty, it usually means a KPI file name or path needs to be aligned with <b>data/processed_new</b>.</div>",
    unsafe_allow_html=True,
)

st.divider()

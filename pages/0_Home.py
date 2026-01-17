import streamlit as st

st.set_page_config(
    page_title="Home | IPL Strategy Dashboard",
    layout="wide"
)

# -----------------------------
# Home Header
# -----------------------------
st.markdown(
    "<div style='font-size: 2.35rem; font-weight: 900; color:#111; margin-bottom: 6px;'>"
    "IPL Analytics & Predictions: 2008 – 2025"
    "</div>",
    unsafe_allow_html=True
)

st.markdown(
    "<div style='font-size: 1.15rem; color:#555; margin-top: -2px; margin-bottom: 16px; line-height:1.55;'>"
    "Analyze IPL match data to derive actionable strategies for teams and players."
    "</div>",
    unsafe_allow_html=True
)

st.markdown(
    "<div style='font-size: 1.06rem; color:#666; margin-bottom: 12px; line-height:1.6;'>"
    "This dashboard uses <b>precomputed CSV outputs</b> for instant loading, stable performance, and a clean UX."
    "</div>",
    unsafe_allow_html=True
)

st.markdown(
    "<hr style='border: none; border-top: 1px solid #EEE; margin: 18px 0px 18px 0px;'>",
    unsafe_allow_html=True
)

st.markdown(
    "<div style='font-size: 1.55rem; font-weight: 850; color:#111; margin-bottom: 4px;'>"
    "Dashboard sections"
    "</div>",
    unsafe_allow_html=True
)

st.markdown(
    "<div style='font-size: 1.05rem; color:#666; margin-bottom: 16px; line-height:1.6;'>"
    "Use the sidebar to navigate. Each section below explains what the page answers and how to interpret the output."
    "</div>",
    unsafe_allow_html=True
)

# -----------------------------
# Section card helper
# -----------------------------
def section_card(title: str, page_path: str, description_html: str):
    st.markdown(
        f"""
        <div style="
            border: 1px solid #E6E8EC;
            border-radius: 16px;
            padding: 16px 18px;
            background: #FFFFFF;
            margin-bottom: 10px;
        ">
                <h4><b>{title}</b></h4>
                {description_html}
        """,
        unsafe_allow_html=True
    )

    st.page_link(page_path, label=f"Open {title} →", icon="➡️")
    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)


# -----------------------------
# Section descriptions (NO <div> tags inside)
# -----------------------------
section_card(
    title="All Seasons – Quick Insights",
    page_path="pages/1_All_Seasons_Quick_Insights.py",
    description_html="""
    This section gives a fast snapshot of IPL scoring behavior across <b>all seasons</b>.
    It answers one practical question: <b>what does the overall IPL scoring environment look like?</b>
    Use the <b>Venue Region</b> and <b>Season</b> filters to compare scoring across locations and years.
    You’ll see match volume, total runs, and phase-level scoring contribution (Powerplay, Middle Overs, Death Overs),
    so you understand <b>where runs come from</b> before moving into deeper strategy sections.
    """
)

section_card(
    title="Match & Toss Strategy",
    page_path="pages/2_Match_Toss_Strategy.py",
    description_html="""
    This page turns match outcomes into a decision framework:
    <b>does winning the toss matter, and what call tends to work better?</b>
    It summarizes toss impact and compares outcomes when the toss winner chooses to <b>chase</b> versus <b>defend</b>.
    The goal is to support a <b>match-day plan</b> that adapts by <b>region</b> and <b>season</b>.
    """
)

section_card(
    title="Venue Intelligence",
    page_path="pages/3_Venue_Intelligence.py",
    description_html="""
    This section answers venue-level strategy questions such as:
    <b>Which venues provide reliable sample sizes?</b> and <b>Should a team chase or defend?</b>
    It highlights high-usage venues, stable chase-vs-defend bias, and splits toss analysis into two clean ideas:
    <b>toss impact</b> (when it matters) and <b>captain preference</b> (what teams choose to do).
    """
)

section_card(
    title="Batting Analysis",
    page_path="pages/4_Batting_Analysis.py",
    description_html="""
    This page will focus on batter performance patterns and match-up insights.
    The aim is to explain <b>who drives scoring</b>, under what conditions, and what a team should prioritize
    when planning an innings.
    """
)

section_card(
    title="Bowling Analysis",
    page_path="pages/5_Bowling_Analysis.py",
    description_html="""
    This page will focus on bowling control signals and wicket-taking patterns.
    The aim is to explain <b>how teams restrict scoring</b>, what phases matter most, and which bowling types
    perform best in different conditions.
    """
)


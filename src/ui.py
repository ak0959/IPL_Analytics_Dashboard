import streamlit as st

PRIMARY_PALETTE = ["#1F77B4", "#2CA02C", "#FF7F0E", "#9467BD", "#D62728", "#17BECF"]

COLOR_CHASE = "#2CA02C"
COLOR_DEFEND = "#D62728"
COLOR_NEUTRAL = "#FF7F0E"
COLOR_INFO = "#1F77B4"

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

def nav_buttons(back_page=None, next_page=None):
    c1, c2, c3 = st.columns([1.2, 1.2, 1.2])

    with c1:
        if back_page:
            if st.button("⬅ Back", use_container_width=True):
                st.switch_page(back_page)

    with c2:
        if st.button("🏠 Home", use_container_width=True):
            st.switch_page("pages/0_Home.py")

    with c3:
        if next_page:
            if st.button("Next ➡", use_container_width=True):
                st.switch_page(next_page)

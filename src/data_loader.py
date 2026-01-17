import os
import pandas as pd
import streamlit as st

@st.cache_data(show_spinner=False)
def load_kpi_csv(*parts):
    """
    Loads a KPI CSV using a path that works on:
    - Local machine
    - GitHub
    - Streamlit Community Cloud

    Usage:
        load_kpi_csv("master_kpis", "overview", "kpi_overview_summary_all.csv")
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # project root
    kpi_root = os.path.join(base_dir, "data", "KPIs")
    path = os.path.join(kpi_root, *parts)

    if not os.path.exists(path):
        raise FileNotFoundError(f"KPI file not found: {path}")

    return pd.read_csv(path)

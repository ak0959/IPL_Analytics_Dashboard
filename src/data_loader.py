import os
import pandas as pd
import streamlit as st

PROJECT_ROOT = r"E:\Google Drive\Portfolio Projects\IPL_Strategy_Dashboard"
KPI_ROOT = os.path.join(PROJECT_ROOT, "data", "KPIs")

@st.cache_data(show_spinner=False)
def load_kpi_csv(*parts):
    path = os.path.join(KPI_ROOT, *parts)
    return pd.read_csv(path)

@st.cache_data(show_spinner=False)
def load_match_base():
    path = os.path.join(KPI_ROOT, "master_kpis", "matches", "phase2_match_base_all_venues.csv")
    df = pd.read_csv(path)

    df["season_id"] = pd.to_numeric(df["season_id"], errors="coerce").astype("Int64")
    df["toss_decision"] = df["toss_decision"].astype(str).str.lower().str.strip()
    df["toss_strategy"] = df["toss_decision"].map({"field": "Chase", "bat": "Defend"}).fillna("Unknown")
    df["toss_winner_won_match"] = (df["toss_winner"] == df["match_winner"]).astype(int)
    df["venue_region"] = df["venue_region"].astype(str).str.strip()

    return df

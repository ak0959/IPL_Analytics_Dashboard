# src/data_loader.py

from pathlib import Path
import pandas as pd
import streamlit as st

# Project root: .../IPL_Strategy_Dashboard
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data" / "processed_new"

@st.cache_data(show_spinner=False)
def load_csv(*parts: str) -> pd.DataFrame:
    """
    Load a CSV from data/processed_new using path parts.

    Examples:
        load_csv("kpi_player_batting_alltime.csv")
        load_csv("master2_balls_baseline.csv")
    """
    path = DATA_DIR.joinpath(*parts)
    return pd.read_csv(path)

# ---------------- Masters ----------------
def load_master_matches():
    return load_csv("master1_matches_baseline.csv")

def load_master_balls():
    return load_csv("master2_balls_baseline.csv")

def load_master_teams():
    return load_csv("master3_teams.csv")

def load_teams_ui():
    return load_csv("master_teams_ui.csv")

def load_team_aliases():
    return load_csv("master_team_aliases.csv")

def load_gates_config():
    return load_csv("gates_config.csv")

def load_optional_toggles_config():
    return load_csv("optional_toggles_config.csv")

# ---------------- Player KPIs ----------------
def load_kpi_player_batting_alltime():
    return load_csv("kpi_player_batting_alltime.csv")

def load_kpi_player_bowling_alltime():
    return load_csv("kpi_player_bowling_alltime.csv")

def load_kpi_player_batting_season():
    return load_csv("kpi_player_batting_season.csv")

def load_kpi_player_bowling_season():
    return load_csv("kpi_player_bowling_season.csv")

# ---------------- Team KPIs ----------------
def load_kpi_team_batting_alltime():
    return load_csv("kpi_team_batting_alltime.csv")

def load_kpi_team_bowling_alltime():
    return load_csv("kpi_team_bowling_alltime.csv")

def load_kpi_team_batting_season():
    return load_csv("kpi_team_batting_season.csv")

def load_kpi_team_bowling_season():
    return load_csv("kpi_team_bowling_season.csv")

import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # project root
KPI_DIR = os.path.join(BASE_DIR, "data", "KPIs")

def load_kpi_csv(*parts):
    path = os.path.join(KPI_DIR, *parts)
    return pd.read_csv(path)

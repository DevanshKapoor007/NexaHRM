"""
NexaHRM — Data Access & Aggregation Layer
Cached loaders for processed datasets + executive KPI aggregation.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys
from typing import Dict, Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from core.config import (
    DATA_PROCESSED_DIR,
    ATTRITION_DATA_PATH, PERFORMANCE_DATA_PATH, PERFORMANCE_PRO_PATH
)


def get_attrition_df() -> pd.DataFrame:
    path = DATA_PROCESSED_DIR / "processed_attrition.csv"
    if not path.exists():
        from core.data_processor import process_attrition_data
        return process_attrition_data()
    return pd.read_csv(path)


def get_performance_df() -> pd.DataFrame:
    path = DATA_PROCESSED_DIR / "processed_performance.csv"
    if not path.exists():
        from core.data_processor import process_performance_data
        return process_performance_data()
    return pd.read_csv(path)


def get_training_df() -> pd.DataFrame:
    path = DATA_PROCESSED_DIR / "processed_training_engagement.csv"
    if not path.exists():
        from core.data_processor import process_training_engagement_data
        return process_training_engagement_data()
    return pd.read_csv(path)


def get_executive_kpis() -> Dict[str, Any]:
    """Computes high-level executive KPIs across all datasets."""
    df_att   = get_attrition_df()
    df_perf  = get_performance_df()
    df_train = get_training_df()

    total_headcount      = len(df_att)
    attrition_rate       = round(df_att["Attrition_Numeric"].mean() * 100, 1)
    retention_rate       = round(100.0 - attrition_rate, 1)
    avg_salary           = int(df_att["MonthlyIncome"].mean())
    avg_tenure           = round(float(df_att["YearsAtCompany"].mean()), 1)
    promotion_rate       = round(df_perf["Promotion_Numeric"].mean() * 100, 1)
    avg_productivity     = round(float(df_perf["ProductivityIndex"].mean()), 1)
    total_training_spend = int(df_train["Training Cost"].sum())
    training_success_rate = round(df_train["TrainingSuccess"].mean() * 100, 1)

    return {
        "total_headcount":       total_headcount,
        "retention_rate":        retention_rate,
        "attrition_rate":        attrition_rate,
        "avg_salary":            avg_salary,
        "avg_tenure":            avg_tenure,
        "promotion_rate":        promotion_rate,
        "avg_productivity":      avg_productivity,
        "total_training_spend":  total_training_spend,
        "training_success_rate": training_success_rate,
    }

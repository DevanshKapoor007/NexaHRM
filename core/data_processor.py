"""
NexaHRM — Raw → Processed Data Pipeline
Cleans and engineers features from raw CSVs for ML training and dashboard rendering.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from core.config import (
    DATA_RAW_DIR, DATA_PROCESSED_DIR, DATA_EXTERNAL_DIR,
    ATTRITION_DATA_PATH, PERFORMANCE_DATA_PATH, PERFORMANCE_PRO_PATH,
    OCCUPATION_DATA_PATH, ESSENTIAL_SKILLS_PATH, SOFTWARE_SKILLS_PATH
)


def _ensure_processed_dir():
    DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def _clean_string_columns(df: pd.DataFrame) -> pd.DataFrame:
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str).str.strip()
    return df


# ══════════════════════════════════════════════════════════════════════════════
# ATTRITION DATA
# ══════════════════════════════════════════════════════════════════════════════

def process_attrition_data() -> pd.DataFrame:
    """Loads, cleans and feature-engineers the IBM HR attrition dataset."""
    _ensure_processed_dir()
    df = pd.read_csv(ATTRITION_DATA_PATH)
    df = _clean_string_columns(df)

    # Target encoding
    df["Attrition_Numeric"] = (df["Attrition"].str.lower() == "yes").astype(int)

    # Derived features
    df["TotalSatisfaction"]       = df["EnvironmentSatisfaction"] + df["JobSatisfaction"] + df["RelationshipSatisfaction"] + df["WorkLifeBalance"]
    df["IncomePerYearExperience"] = df["MonthlyIncome"] / (df["TotalWorkingYears"] + 1)
    df["PromotionWaitRatio"]      = df["YearsSinceLastPromotion"] / (df["YearsInCurrentRole"] + 1)
    df["ManagerTenureRatio"]      = df["YearsWithCurrManager"] / (df["YearsAtCompany"] + 1)
    df["TenureRatio"]             = df.apply(lambda r: r["YearsAtCompany"] / (r["Age"] - 17) if r["Age"] > 18 else 0.1, axis=1)

    out = DATA_PROCESSED_DIR / "processed_attrition.csv"
    df.to_csv(out, index=False)
    print(f"[NexaHRM] Attrition data processed: {df.shape} → {out.name}")
    return df


# ══════════════════════════════════════════════════════════════════════════════
# PERFORMANCE DATA
# ══════════════════════════════════════════════════════════════════════════════

def process_performance_data() -> pd.DataFrame:
    """Processes the employee performance & promotion dataset."""
    _ensure_processed_dir()
    df = pd.read_csv(PERFORMANCE_DATA_PATH)
    df = _clean_string_columns(df)

    # Target encoding
    promoted_col = next((c for c in df.columns if "promot" in c.lower()), None)
    if promoted_col:
        df["Promotion_Numeric"] = pd.to_numeric(df[promoted_col], errors="coerce").fillna(0).astype(int)
    else:
        df["Promotion_Numeric"] = 0

    # KPI / productivity
    kpi  = pd.to_numeric(df.get("KPI Score",           df.get("KPI_Score",            pd.Series([80.0]*len(df)))), errors="coerce").fillna(80.0)
    task = pd.to_numeric(df.get("Task Completion (%)", df.get("Task_Completion",       pd.Series([85.0]*len(df)))), errors="coerce").fillna(85.0)
    att  = pd.to_numeric(df.get("Attendance (%)",      df.get("Attendance",            pd.Series([90.0]*len(df)))), errors="coerce").fillna(90.0)
    peer = pd.to_numeric(df.get("Peer Rating",         df.get("Peer_Rating",           pd.Series([4.0]*len(df)))),  errors="coerce").fillna(4.0)
    mgr  = pd.to_numeric(df.get("Manager Feedback",    df.get("Manager_Feedback",      pd.Series([4.0]*len(df)))),  errors="coerce").fillna(4.0)

    df["KPI Score"]           = kpi
    df["Task Completion (%)"] = task
    df["Attendance (%)"]      = att
    df["Peer Rating"]         = peer
    df["Manager Feedback"]    = mgr

    df["ProductivityIndex"] = (kpi * 0.35) + (task * 0.25) + (att * 0.15) + (peer * 20 * 0.15) + (mgr * 20 * 0.10)

    # Performance tier
    df["PerformanceTier"] = pd.cut(
        df["ProductivityIndex"],
        bins=[0, 75, 88, 101],
        labels=["Developing", "Proficient", "High Performer"],
    )

    out = DATA_PROCESSED_DIR / "processed_performance.csv"
    df.to_csv(out, index=False)
    print(f"[NexaHRM] Performance data processed: {df.shape} → {out.name}")
    return df


# ══════════════════════════════════════════════════════════════════════════════
# TRAINING & ENGAGEMENT DATA
# ══════════════════════════════════════════════════════════════════════════════

def process_training_engagement_data() -> pd.DataFrame:
    """Processes the training & employee engagement dataset."""
    _ensure_processed_dir()
    df = pd.read_csv(PERFORMANCE_PRO_PATH)
    df = _clean_string_columns(df)

    cost_col = next((c for c in df.columns if "cost" in c.lower()), None)
    if cost_col and cost_col != "Training Cost":
        df["Training Cost"] = pd.to_numeric(df[cost_col], errors="coerce").fillna(500)

    dur_col = next((c for c in df.columns if "duration" in c.lower() or "days" in c.lower()), None)
    if dur_col and dur_col != "Training Duration(Days)":
        df["Training Duration(Days)"] = pd.to_numeric(df[dur_col], errors="coerce").fillna(3)

    eng_col = next((c for c in df.columns if "engagement" in c.lower()), None)
    if eng_col:
        df["Engagement Score"] = pd.to_numeric(df[eng_col], errors="coerce").fillna(4)

    dept_col = next((c for c in df.columns if "dept" in c.lower() or "department" in c.lower()), None)
    if dept_col and dept_col != "DepartmentType":
        df["DepartmentType"] = df[dept_col]

    success_col = next((c for c in df.columns if "success" in c.lower() or "complet" in c.lower()), None)
    if success_col:
        df["TrainingSuccess"] = (pd.to_numeric(df[success_col], errors="coerce").fillna(0) > 0).astype(int)
    else:
        df["TrainingSuccess"] = (np.random.rand(len(df)) > 0.35).astype(int)

    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str).str.strip()

    out = DATA_PROCESSED_DIR / "processed_training_engagement.csv"
    df.to_csv(out, index=False)
    print(f"[NexaHRM] Training data processed: {df.shape} → {out.name}")
    return df


# ══════════════════════════════════════════════════════════════════════════════
# O*NET SKILLS TAXONOMY
# ══════════════════════════════════════════════════════════════════════════════

def process_onet_skills_taxonomy() -> pd.DataFrame:
    """Merges O*NET occupation, essential skills, and software tools data."""
    _ensure_processed_dir()

    df_occ  = pd.read_csv(OCCUPATION_DATA_PATH)
    df_skills = pd.read_csv(ESSENTIAL_SKILLS_PATH)
    df_sw   = pd.read_csv(SOFTWARE_SKILLS_PATH)

    for df in [df_occ, df_skills, df_sw]:
        for col in df.select_dtypes(include="object").columns:
            df[col] = df[col].astype(str).str.strip()

    # Aggregate top skills per occupation
    skills_agg = (
        df_skills.groupby("O*NET-SOC Code")
        .apply(lambda g: g.nlargest(5, "Data Value") if "Data Value" in g.columns else g.head(5))
        .reset_index(drop=True)
    )
    skills_grouped = (
        skills_agg.groupby("O*NET-SOC Code")
        .agg(
            TopSkills=("Element Name", lambda x: "|".join(x.astype(str))),
            SkillImportance=("Data Value", lambda x: "|".join(x.astype(str))),
        )
        .reset_index()
    )

    # Aggregate software tools
    sw_grouped = (
        df_sw.groupby("O*NET-SOC Code")
        .apply(lambda g: g.head(8))
        .reset_index(drop=True)
        .groupby("O*NET-SOC Code")
        .agg(
            SoftwareTools=("Commodity Title", lambda x: "|".join(x.astype(str))),
            HotTechFlags=(
                "Hot Technology",
                lambda x: "|".join(x.astype(str)) if "Hot Technology" in df_sw.columns else "",
            ),
        )
        .reset_index()
    )

    df_merged = df_occ.merge(skills_grouped, on="O*NET-SOC Code", how="left")
    df_merged = df_merged.merge(sw_grouped,   on="O*NET-SOC Code", how="left")

    out = DATA_PROCESSED_DIR / "processed_skills_taxonomy.csv"
    df_merged.to_csv(out, index=False)
    print(f"[NexaHRM] Skills taxonomy processed: {df_merged.shape} → {out.name}")
    return df_merged


def run_all_processors():
    """Runs the full data processing pipeline."""
    process_attrition_data()
    process_performance_data()
    process_training_engagement_data()
    process_onet_skills_taxonomy()

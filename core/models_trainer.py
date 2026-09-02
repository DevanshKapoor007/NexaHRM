"""
NexaHRM — ML Model Training Pipeline
Trains and serializes Random Forest pipelines for attrition risk,
promotion readiness, and training outcome prediction.
"""

import pandas as pd
import numpy as np
import joblib
from pathlib import Path
import sys
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from core.config import (
    DATA_PROCESSED_DIR, MODELS_DIR,
    ATTRITION_MODEL_PATH, PERFORMANCE_MODEL_PATH, TRAINING_MODEL_PATH
)


def _build_pipeline(cat_cols, num_cols, clf):
    preprocessor = ColumnTransformer(transformers=[
        ("num", StandardScaler(), num_cols),
        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat_cols),
    ])
    return Pipeline([("preprocessor", preprocessor), ("classifier", clf)])


# ══════════════════════════════════════════════════════════════════════════════
# ATTRITION MODEL
# ══════════════════════════════════════════════════════════════════════════════

def train_attrition_model():
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(DATA_PROCESSED_DIR / "processed_attrition.csv")

    cat_cols = ["Department", "JobRole", "MaritalStatus", "OverTime", "BusinessTravel", "EducationField"]
    num_cols = [
        "Age", "MonthlyIncome", "TotalWorkingYears", "YearsAtCompany",
        "YearsInCurrentRole", "YearsWithCurrManager", "YearsSinceLastPromotion",
        "DistanceFromHome", "TotalSatisfaction", "IncomePerYearExperience",
        "PromotionWaitRatio", "ManagerTenureRatio", "TenureRatio",
    ]

    cat_cols = [c for c in cat_cols if c in df.columns]
    num_cols = [c for c in num_cols if c in df.columns]
    features = cat_cols + num_cols

    df_clean = df[features + ["Attrition_Numeric"]].dropna()
    X = df_clean[features]
    y = df_clean["Attrition_Numeric"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    pipeline = _build_pipeline(cat_cols, num_cols, RandomForestClassifier(n_estimators=200, random_state=42, class_weight="balanced"))
    pipeline.fit(X_train, y_train)

    artifact = {
        "pipeline": pipeline,
        "training_features": features,
        "categorical_cols": cat_cols,
        "numerical_cols": num_cols,
        "optimal_threshold": 0.40,
    }
    joblib.dump(artifact, ATTRITION_MODEL_PATH)
    print(f"[NexaHRM] Attrition model saved → {ATTRITION_MODEL_PATH.name}")
    return artifact


# ══════════════════════════════════════════════════════════════════════════════
# PERFORMANCE / PROMOTION MODEL
# ══════════════════════════════════════════════════════════════════════════════

def train_performance_model():
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(DATA_PROCESSED_DIR / "processed_performance.csv")

    cat_cols = ["Department", "Gender", "Education"] if all(c in df.columns for c in ["Department", "Gender", "Education"]) else []
    cat_cols = [c for c in cat_cols if c in df.columns]

    num_cols = [
        "KPI Score", "Task Completion (%)", "Attendance (%)",
        "Peer Rating", "Manager Feedback", "ProductivityIndex",
    ]
    num_cols = [c for c in num_cols if c in df.columns]

    if "Work Hours Logged" not in df.columns:
        df["Work Hours Logged"] = 40.0
    else:
        num_cols.append("Work Hours Logged")

    df["WorkHourEfficiency"] = df["KPI Score"] * df["Task Completion (%)"] / (df.get("Work Hours Logged", 40) + 1)
    num_cols.append("WorkHourEfficiency")

    features = cat_cols + num_cols
    df_clean = df[features + ["Promotion_Numeric"]].dropna()
    X = df_clean[features]
    y = df_clean["Promotion_Numeric"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    pipeline = _build_pipeline(cat_cols, num_cols, RandomForestClassifier(n_estimators=150, random_state=42))
    pipeline.fit(X_train, y_train)

    artifact = {
        "pipeline": pipeline,
        "training_features": features,
        "categorical_cols": cat_cols,
        "numerical_cols": num_cols,
    }
    joblib.dump(artifact, PERFORMANCE_MODEL_PATH)
    print(f"[NexaHRM] Performance model saved → {PERFORMANCE_MODEL_PATH.name}")
    return artifact


# ══════════════════════════════════════════════════════════════════════════════
# TRAINING OUTCOME MODEL
# ══════════════════════════════════════════════════════════════════════════════

def train_training_model():
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(DATA_PROCESSED_DIR / "processed_training_engagement.csv")

    cat_cols = [c for c in ["DepartmentType", "Training Type"] if c in df.columns]
    num_cols = [c for c in ["Training Cost", "Training Duration(Days)", "Engagement Score", "Satisfaction Score", "Work-Life Balance Score"] if c in df.columns]

    if "CostPerTrainingDay" not in df.columns and "Training Cost" in df.columns and "Training Duration(Days)" in df.columns:
        df["CostPerTrainingDay"] = df["Training Cost"] / (df["Training Duration(Days)"] + 0.001)
        num_cols.append("CostPerTrainingDay")

    features = cat_cols + num_cols
    df_clean = df[features + ["TrainingSuccess"]].dropna()
    X = df_clean[features]
    y = df_clean["TrainingSuccess"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    pipeline = _build_pipeline(cat_cols, num_cols, RandomForestClassifier(n_estimators=100, random_state=42))
    pipeline.fit(X_train, y_train)

    artifact = {
        "pipeline": pipeline,
        "training_features": features,
        "categorical_cols": cat_cols,
        "numerical_cols": num_cols,
    }
    joblib.dump(artifact, TRAINING_MODEL_PATH)
    print(f"[NexaHRM] Training outcome model saved → {TRAINING_MODEL_PATH.name}")
    return artifact


def run_all_trainers():
    """Runs the full ML training pipeline."""
    print("[NexaHRM] Starting model training pipeline...")
    train_attrition_model()
    train_performance_model()
    train_training_model()
    print("[NexaHRM] All models trained and serialized successfully.")

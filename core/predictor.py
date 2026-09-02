"""
NexaHRM — ML Inference & Prediction Services
Loads serialized model pipelines and provides real-time predictions with
automatic self-healing retraining fallback.
"""

import pandas as pd
import numpy as np
import joblib
from pathlib import Path
import sys
from typing import Dict, Any, List

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from core.config import ATTRITION_MODEL_PATH, PERFORMANCE_MODEL_PATH, TRAINING_MODEL_PATH


class NexaPredictor:
    """Central ML inference engine for attrition, promotion, and training outcomes."""

    def __init__(self):
        self._load_models()

    def _load_models(self):
        self.attrition_artifact  = None
        self.performance_artifact = None
        self.training_artifact   = None
        needs_retrain = False

        if not (ATTRITION_MODEL_PATH.exists() and PERFORMANCE_MODEL_PATH.exists() and TRAINING_MODEL_PATH.exists()):
            needs_retrain = True
        else:
            try:
                self.attrition_artifact  = joblib.load(ATTRITION_MODEL_PATH)
                self.performance_artifact = joblib.load(PERFORMANCE_MODEL_PATH)
                self.training_artifact   = joblib.load(TRAINING_MODEL_PATH)
            except Exception as e:
                print(f"[NexaHRM] Model load warning: {e}. Initiating retraining...")
                needs_retrain = True

        if needs_retrain:
            try:
                from core.models_trainer import run_all_trainers
                run_all_trainers()
                self.attrition_artifact  = joblib.load(ATTRITION_MODEL_PATH)
                self.performance_artifact = joblib.load(PERFORMANCE_MODEL_PATH)
                self.training_artifact   = joblib.load(TRAINING_MODEL_PATH)
                print("[NexaHRM] Auto-retraining completed.")
            except Exception as e:
                print(f"[NexaHRM] Fatal retraining error: {e}")

    # ── Attrition Prediction ───────────────────────────────────────────────────

    def predict_attrition(self, emp_data: Dict[str, Any]) -> Dict[str, Any]:
        """Returns churn probability, risk tier, and burnout driver diagnosis."""
        if not self.attrition_artifact:
            self._load_models()
        if not self.attrition_artifact:
            raise FileNotFoundError("Attrition model not available.")

        df = pd.DataFrame([emp_data])

        # Feature engineering
        env  = float(df.get("EnvironmentSatisfaction",  [3]).iloc[0])
        job  = float(df.get("JobSatisfaction",           [3]).iloc[0])
        rel  = float(df.get("RelationshipSatisfaction",  [3]).iloc[0])
        wlb  = float(df.get("WorkLifeBalance",           [3]).iloc[0])
        inc  = float(df.get("MonthlyIncome",             [5000]).iloc[0])
        wyr  = float(df.get("TotalWorkingYears",         [5]).iloc[0])
        ten  = float(df.get("YearsAtCompany",            [3]).iloc[0])
        age  = float(df.get("Age",                       [30]).iloc[0])
        ryr  = float(df.get("YearsInCurrentRole",        [2]).iloc[0])
        myr  = float(df.get("YearsWithCurrManager",      [2]).iloc[0])
        pyr  = float(df.get("YearsSinceLastPromotion",   [1]).iloc[0])

        df["TotalSatisfaction"]       = env + job + rel + wlb
        df["IncomePerYearExperience"] = inc / (wyr + 1.0)
        df["PromotionWaitRatio"]      = pyr / (ryr + 1.0)
        df["ManagerTenureRatio"]      = myr / (ten + 1.0)
        df["TenureRatio"]             = ten / (age - 17.0) if age > 18 else 0.1

        artifact = self.attrition_artifact
        cat_cols = artifact.get("categorical_cols", [])
        num_cols = artifact.get("numerical_cols", [])

        for col in cat_cols:
            df[col] = df[col].astype(str) if col in df.columns else "Unknown"
        for col in num_cols:
            df[col] = pd.to_numeric(df.get(col, pd.Series([0.0])), errors="coerce").fillna(0.0)

        features = artifact["training_features"]
        for col in features:
            if col not in df.columns:
                df[col] = "Unknown" if col in cat_cols else 0.0

        prob = float(artifact["pipeline"].predict_proba(df[features])[0, 1])

        if prob >= 0.50:
            risk_level, risk_color = "High",   "#EF4444"
        elif prob >= 0.25:
            risk_level, risk_color = "Medium", "#F59E0B"
        else:
            risk_level, risk_color = "Low",    "#10B981"

        return {
            "attrition_probability": round(prob * 100, 1),
            "risk_level":            risk_level,
            "risk_color":            risk_color,
            "risk_drivers":          self._diagnose_drivers(emp_data, prob),
            "optimal_threshold":     artifact.get("optimal_threshold", 0.5),
        }

    def _diagnose_drivers(self, emp_data: Dict, prob: float) -> List[str]:
        drivers = []
        if emp_data.get("OverTime") == "Yes":
            drivers.append("Excessive mandatory overtime burden")
        if emp_data.get("MonthlyIncome", 6000) < 4000:
            drivers.append("Below-market compensation for role level")
        if emp_data.get("YearsSinceLastPromotion", 0) >= 3:
            drivers.append("Stalled career trajectory (3+ years without promotion)")
        if emp_data.get("JobSatisfaction", 3) <= 2:
            drivers.append("Low job fulfillment & role stagnation")
        if emp_data.get("WorkLifeBalance", 3) <= 2:
            drivers.append("Poor work-life balance & after-hours fatigue")
        if emp_data.get("DistanceFromHome", 5) > 15:
            drivers.append("Long daily commute (>15 miles)")
        if emp_data.get("YearsWithCurrManager", 3) <= 1 and emp_data.get("YearsAtCompany", 3) > 3:
            drivers.append("Recent manager transition / leadership disconnect")
        return (drivers or ["Balanced organizational stability metrics."])[:3]

    # ── Promotion Prediction ───────────────────────────────────────────────────

    def predict_promotion(self, emp_data: Dict[str, Any]) -> Dict[str, Any]:
        """Returns promotion readiness probability and productivity index."""
        if not self.performance_artifact:
            self._load_models()
        if not self.performance_artifact:
            raise FileNotFoundError("Performance model not available.")

        df = pd.DataFrame([emp_data])
        kpi  = float(df.get("KPI Score",           [80]).iloc[0])
        task = float(df.get("Task Completion (%)", [85]).iloc[0])
        att  = float(df.get("Attendance (%)",      [90]).iloc[0])
        peer = float(df.get("Peer Rating",         [4]).iloc[0])
        mgr  = float(df.get("Manager Feedback",    [4]).iloc[0])
        hrs  = float(df.get("Work Hours Logged",   [40]).iloc[0])

        productivity = (kpi * 0.35) + (task * 0.25) + (att * 0.15) + (peer * 20 * 0.15) + (mgr * 20 * 0.10)
        df["ProductivityIndex"]   = productivity
        df["WorkHourEfficiency"]  = (kpi * task) / (hrs + 1.0)
        df["ManagerScoreRatio"]   = mgr / (peer + 0.1)

        artifact = self.performance_artifact
        cat_cols = artifact.get("categorical_cols", [])
        num_cols = artifact.get("numerical_cols", [])

        for col in cat_cols:
            df[col] = df[col].astype(str) if col in df.columns else "Unknown"
        for col in num_cols:
            df[col] = pd.to_numeric(df.get(col, pd.Series([0.0])), errors="coerce").fillna(0.0)

        features = artifact["training_features"]
        for col in features:
            if col not in df.columns:
                df[col] = "Unknown" if col in cat_cols else 0.0

        prob = float(artifact["pipeline"].predict_proba(df[features])[0, 1])
        tier = (
            "Ready for Immediate Promotion" if prob >= 0.50
            else ("Accelerated Development Track" if prob >= 0.35
                  else "Structured Growth Pathway")
        )

        return {
            "promotion_probability": round(prob * 100, 1),
            "promotion_ready":       prob >= 0.50,
            "promotion_tier":        tier,
            "productivity_index":    round(productivity, 1),
        }

    # ── Training Outcome Prediction ────────────────────────────────────────────

    def predict_training_outcome(self, training_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predicts training completion success probability."""
        if not self.training_artifact:
            self._load_models()
        if not self.training_artifact:
            raise FileNotFoundError("Training model not available.")

        df = pd.DataFrame([training_data])
        cost = float(df.get("Training Cost",              [500]).iloc[0])
        days = float(df.get("Training Duration(Days)",    [3]).iloc[0])

        df["CostPerTrainingDay"] = cost / (days + 0.001)

        artifact = self.training_artifact
        cat_cols = artifact.get("categorical_cols", [])
        num_cols = artifact.get("numerical_cols", [])

        for col in cat_cols:
            df[col] = df[col].astype(str) if col in df.columns else "Unknown"
        for col in num_cols:
            df[col] = pd.to_numeric(df.get(col, pd.Series([0.0])), errors="coerce").fillna(0.0)

        features = artifact["training_features"]
        for col in features:
            if col not in df.columns:
                df[col] = "Unknown" if col in cat_cols else 0.0

        prob = float(artifact["pipeline"].predict_proba(df[features])[0, 1])

        return {
            "success_probability": round(prob * 100, 1),
            "is_successful":       prob >= 0.50,
            "cost_per_day":        round(cost / max(days, 1), 2),
        }


# Singleton instance
predictor = NexaPredictor()

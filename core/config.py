"""
NexaHRM — Path & Configuration Constants
Central configuration for all data paths, model artifacts, and directory references.
"""

from pathlib import Path

# ── Base Directories ───────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).resolve().parent.parent
CORE_DIR   = BASE_DIR / "core"
DATA_DIR   = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"

# ── Data Sub-Directories ───────────────────────────────────────────────────────
DATA_RAW_DIR       = DATA_DIR / "raw"
DATA_PROCESSED_DIR = DATA_DIR / "processed"
DATA_EXTERNAL_DIR  = DATA_DIR / "external"

# ── Raw Dataset Paths ──────────────────────────────────────────────────────────
ATTRITION_DATA_PATH      = DATA_RAW_DIR / "employee_attrition.csv"
PERFORMANCE_DATA_PATH    = DATA_RAW_DIR / "Employee_Performance_Dataset.csv"
PERFORMANCE_PRO_PATH     = DATA_RAW_DIR / "employee_performance_pro.csv"
HR_ANALYSIS_DATA_PATH    = DATA_RAW_DIR / "Cleaned_HR_Data_Analysis.csv"

# ── O*NET External Taxonomy Paths ──────────────────────────────────────────────
OCCUPATION_DATA_PATH  = DATA_EXTERNAL_DIR / "occupation_data.csv"
ESSENTIAL_SKILLS_PATH = DATA_EXTERNAL_DIR / "essential_skills.csv"
SOFTWARE_SKILLS_PATH  = DATA_EXTERNAL_DIR / "software_skills.csv"

# ── Serialized Model Artifact Paths ───────────────────────────────────────────
ATTRITION_MODEL_PATH   = MODELS_DIR / "attrition_model.joblib"
PERFORMANCE_MODEL_PATH = MODELS_DIR / "performance_model.joblib"
TRAINING_MODEL_PATH    = MODELS_DIR / "training_model.joblib"

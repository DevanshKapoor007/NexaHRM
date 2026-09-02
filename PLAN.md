# NexaHRM — Comprehensive Development Plan & Architecture Blueprint

## Executive Summary
**NexaHRM** is a next-generation, enterprise-grade AI Workforce Analytics and Career Intelligence Platform. Designed with a dark-mode glassmorphism interface, NexaHRM combines predictive machine learning models with standard O*NET occupation taxonomy data to solve critical talent management challenges: employee turnover, performance progression, training ROI, and career mobility.

---

## System Architecture

```
                                  +---------------------------------------+
                                  |     NexaHRM Streamlit Frontend        |
                                  |  (Dark Glassmorphism Theme Engine)    |
                                  +-------------------+-------------------+
                                                      |
                                                      v
                                  +---------------------------------------+
                                  |    FastAPI REST API Layer (Port 8000) |
                                  +-------------------+-------------------+
                                                      |
                   +----------------------------------+----------------------------------+
                   |                                  |                                  |
                   v                                  v                                  v
    +------------------------------+   +------------------------------+   +------------------------------+
    |    Authentication Engine     |   |    Predictive ML Pipelines   |   |   O*NET Career Recommender   |
    | (Dual-Role HR/Emp + HR Code) |   | (Attrition, Promo, Training) |   |  (Skill Gap & 30-60-90 Plan) |
    +--------------+---------------+   +--------------+---------------+   +--------------+---------------+
                   |                                  |                                  |
                   +----------------------------------+----------------------------------+
                                                      |
                                                      v
                                  +---------------------------------------+
                                  |      Core Data Processing Layer       |
                                  |  (Cached Data Loader & Feature Eng)   |
                                  +-------------------+-------------------+
                                                      |
                                                      v
                                  +---------------------------------------+
                                  |  Datasets & Serialized Models (.joblib)|
                                  +---------------------------------------+
```

---

## Technical Stack & Architectural Decisions

### 1. Frontend Design System (`ui/`)
- **Framework**: Streamlit with custom CSS injection (`ui/theme.py`)
- **Theme**: Dark Glassmorphism featuring deep navy background (`#0B132B`), translucent card panels (`backdrop-filter: blur(16px)`), electric cyan (`#00D4FF`) and neon purple (`#7C3AED`) accents.
- **Visualization**: Plotly Graph Objects & Plotly Express customized with a dark theme helper (`apply_nexa_plotly_theme`).

### 2. Backend & API Layer (`core/api.py`, `run_server.py`)
- **Framework**: FastAPI + Uvicorn
- **Endpoints**: CORS-enabled JSON REST endpoints covering executive KPIs, ML inference, user auth, O*NET role comparisons, and course roadmaps.

### 3. Machine Learning Engine (`core/models_trainer.py`, `core/predictor.py`)
- **Pipelines**: `scikit-learn` Random Forest Classifiers embedded within ColumnTransformer preprocessing pipelines.
- **Models**:
  1. **Attrition Model**: Predicts 90-day resignation risk and identifies primary burnout catalysts.
  2. **Performance Model**: Evaluates promotion readiness probability and computes a 360° Productivity Index (0-100).
  3. **Training Model**: Estimates course completion probability based on engagement baselines.
- **Self-Healing Fallback**: Automatically retrains and serializes missing model files on startup without interrupting server availability.

### 4. Career Recommender & Course Matcher (`core/recommender.py`, `core/course_matcher.py`)
- **Taxonomy**: Standard O*NET 27.0 Database covering 1,016 occupations, 17,500+ essential skills, and software tools.
- **Skill Gap Overlap**: Computes mathematical Jaccard similarity and weighted competency overlap between current and target roles.
- **Roadmap Generator**: Automatically creates 30-60-90 day milestone plans mapping missing skills to courses from Coursera, edX, Udemy, AWS, Google, and Wharton.

---

## Detailed Milestone Roadmap

### Phase 1: Project Scaffolding & Configuration
- Establish clear directory structure separating backend (`core/`), frontend (`ui/`), data (`data/`), and models (`models/`).
- Define centralized path resolution in `core/config.py`.
- Configure `requirements.txt` and `.gitignore`.

### Phase 2: Data Pipeline & Cleaning
- Clean and normalize raw HR datasets (`employee_attrition.csv`, `Employee_Performance_Dataset.csv`, `Cleaned_HR_Data_Analysis.csv`).
- Implement cached data access utilities in `core/data_loader.py`.
- Calculate executive KPIs (headcount, retention rate, average monthly salary, promotion rate, training spend).

### Phase 3: ML Model Training & Self-Healing Engine
- Construct scikit-learn preprocessing pipelines using OneHotEncoder and StandardScaler.
- Train Random Forest Classifiers for Attrition, Promotion Readiness, and Training Outcome prediction.
- Implement automated fallback logic in `core/predictor.py` to retrain models if `.joblib` files are missing.

### Phase 4: Dual-Role Authentication & Security
- Implement dual-role authentication (HR Manager vs. Employee).
- Build unique company HR invite code generator (e.g. `HR-9100-NEXA`).
- Add OTP generation and email verification workflow.

### Phase 5: O*NET Skill Gap Recommender & Course Matcher
- Implement fuzzy search across 1,016 O*NET SOC occupation codes.
- Compute missing core skills and software tools required for promotion.
- Build provider-filtered course discovery catalog (Coursera, edX, Udemy, AWS, Google, Wharton).
- Generate downloadable 30-60-90 Day Milestone Roadmaps in Markdown.

### Phase 6: Dark Glassmorphism Frontend (6 Dashboard Pages)
- Develop `ui/theme.py` CSS system for dark glassmorphic UI.
- Build main landing page and dual-role command portal in `ui/app.py`.
- Build **Page 1 (Executive Dashboard)**: Resignation rates, overtime impact, salary distributions, and training spend.
- Build **Page 2 (Attrition Risk Engine)**: Real-time churn calculator and interactive retention raise simulator.
- Build **Page 3 (Talent Matrix)**: Performance tiers, promotion readiness scorer, and 360° capability radar chart.
- Build **Page 4 (Learning ROI)**: Training program efficacy and cost-per-day analysis.
- Build **Page 5 (Career Pathways)**: O*NET skill gap overlay and roadmap generator.
- Build **Page 6 (AI Insights)**: Aggregated AI risk briefing dashboard highlighting flight risk warnings, promotion opportunities, and upskilling efficiency.

### Phase 7: REST API & Docker Containerization
- Build FastAPI REST API in `core/api.py` with OpenAPI docs at `/docs`.
- Create `Dockerfile` and `docker-compose.yml` for multi-container deployment.
- Implement comprehensive test harness (`run_tests.py`) covering all 10 module test suites.

---

## Verification & Validation Strategy

1. **Automated Testing**: Execute `python run_tests.py` to run unit tests covering configuration, data loading, authentication, ML inference, O*NET recommendations, and FastAPI endpoints.
2. **UI Verification**: Run `python run_app.py` and inspect pages on `http://localhost:8502`.
3. **API Verification**: Run `python run_server.py` and verify OpenAPI docs at `http://localhost:8000/docs`.

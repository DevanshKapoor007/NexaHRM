# NexaHRM — AI Workforce Analytics & Career Intelligence Platform

[![Python](https://img.shields.io/badge/Python-3.11+-00D4FF?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.3+-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)

NexaHRM is an enterprise-grade workforce analytics and career intelligence platform designed to replace legacy HR tools with predictive machine learning models, O*NET taxonomy role matching, and a dark-mode glassmorphism interface.

---

## 🌟 Key Features

### 👔 HR Executive Command Center
- **Workforce Retention Analytics**: Monitor employee headcount, turnover rates, overtime impact, and salary distributions across departments.
- **90-Day Attrition Risk Predictor**: Calculates resignation probabilities using Random Forest models and identifies primary burnout catalysts.
- **Retention Counter-Offer Simulator**: Test salary adjustments in real-time to observe predicted reductions in resignation probability.
- **Talent Matrix & Promotion Scorer**: Evaluates performance tiers and generates 360° capability radar charts.
- **Company HR Onboarding Codes**: Issue unique HR codes (e.g. `HR-9100-NEXA`) to seamlessly link employees to your organization.

### 👤 Employee Career Growth Portal
- **O*NET Occupation Matching**: Compare current vs. target promotion roles across 1,016 standard O*NET occupations.
- **Skill Gap & Software Tool Analysis**: Pinpoint missing core competencies and required software tools.
- **30-60-90 Day Milestone Roadmaps**: Auto-generate step-by-step career development plans with clear milestone deliverables.
- **Provider-Filtered Course Discovery**: Search verified courses from Coursera, edX, Udemy, AWS, Google, and Wharton.

---

## 📐 System Architecture

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

## 📂 Repository Structure

```
NexaHRM/
├── 📄 PLAN.md                            # Comprehensive development plan & architecture blueprint
├── 📄 README.md                          # Project documentation
├── 📄 Dockerfile                         # Production Docker container image
├── 📄 docker-compose.yml                  # Multi-service container orchestration (UI + API)
├── 📄 requirements.txt                    # Python dependencies
├── 📄 run_app.py                          # Streamlit application entry point (Port 8502)
├── 📄 run_server.py                       # FastAPI REST API server entry point (Port 8000)
├── 📄 run_tests.py                        # Automated test harness (10 unit tests)
│
├── 📂 core/                               # Backend Business Logic & ML Engines
│   ├── 📄 api.py                          # FastAPI REST API endpoints
│   ├── 📄 auth.py                         # Dual-role authentication & HR invite code store
│   ├── 📄 config.py                       # Centralized paths and configuration settings
│   ├── 📄 course_matcher.py               # 30-60-90 roadmap generator & course matching
│   ├── 📄 data_loader.py                  # Data loading & executive KPI aggregation
│   ├── 📄 data_processor.py               # Data pipeline & feature engineering
│   ├── 📄 models_trainer.py               # Scikit-learn Random Forest model pipelines
│   ├── 📄 predictor.py                    # Real-time ML inference & self-healing fallbacks
│   └── 📄 recommender.py                  # O*NET skill gap analysis engine
│
├── 📂 ui/                                 # Streamlit Frontend (Dark Glassmorphism Theme)
│   ├── 📄 app.py                          # Main landing page & dual-role portal
│   ├── 📄 theme.py                        # Dark glassmorphism CSS & Plotly theme styling
│   └── 📂 pages/
│       ├── 📄 1_Dashboard.py              # Executive Workforce Overview
│       ├── 📄 2_Attrition_Engine.py       # Attrition Risk Predictor & Raise Simulator
│       ├── 📄 3_Talent_Matrix.py          # Talent Matrix & Promotion Scorer
│       ├── 📄 4_Learning_ROI.py           # Learning ROI & L&D Tracker
│       ├── 📄 5_Career_Pathways.py        # O*NET Skill Gap & Pathways Hub
│       └── 📄 6_AI_Insights.py            # Aggregated AI Workforce Insights & Briefing
│
├── 📂 data/                               # Data Directory
│   ├── 📂 raw/                            # Cleaned employee datasets
│   └── 📂 external/                       # O*NET 27.0 taxonomy files
│
├── 📂 models/                             # Pre-trained ML Model Artifacts (.joblib)
│   ├── 📄 attrition_model.joblib
│   ├── 📄 performance_model.joblib
│   └── 📄 training_model.joblib
│
└── 📂 notebooks/                          # Jupyter Notebooks for Exploratory Data Analysis
    ├── 📄 01_eda_attrition.ipynb
    ├── 📄 02_eda_performance_and_training.ipynb
    └── 📄 03_eda_skills_matching.ipynb
```

---

## ⚡ Quickstart Guide

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/DevanshKapoor007/NexaHRM.git
cd NexaHRM

# Create and activate virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Running the Streamlit Web Application

```bash
python run_app.py
```
*Access the application at [http://localhost:8502](http://localhost:8502)*

### 3. Running the FastAPI REST API Server

```bash
python run_server.py
```
*Access REST endpoints at [http://localhost:8000](http://localhost:8000) and Swagger docs at [http://localhost:8000/docs](http://localhost:8000/docs)*

---

## 🐳 Running with Docker

```bash
# Start both Streamlit UI (Port 8502) and FastAPI REST API (Port 8000)
docker-compose up --build
```

---

## 🧪 Running Automated Unit Tests

```bash
python run_tests.py
```

The test harness executes 10 unit tests verifying path configuration, data loading, KPI calculation, authentication, ML inference engines, O*NET role recommendations, course matching, and FastAPI endpoints.

---

## 📡 REST API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | API status and root details |
| `GET` | `/api/kpis` | Executive KPI metrics |
| `POST` | `/api/auth/register-hr` | Register HR user & generate company code |
| `POST` | `/api/auth/register-employee` | Register employee with HR code |
| `POST` | `/api/auth/login` | Authenticate user credentials |
| `POST` | `/api/predict/attrition` | Predict 90-day resignation probability |
| `POST` | `/api/predict/promotion` | Evaluate promotion readiness score |
| `POST` | `/api/predict/training` | Estimate training program completion outcome |
| `GET` | `/api/roles/search` | Search O*NET occupation taxonomy |
| `POST` | `/api/roles/compare` | Compare current vs target role skill gaps |
| `POST` | `/api/courses/roadmap` | Generate 30-60-90 day upskilling roadmap |

---

## 📄 License & Academic Note

This project is developed as an independent HR analytics and career intelligence platform portfolio. All core logic, machine learning pipelines, dark glassmorphism user interface components, and API servers are custom authored.

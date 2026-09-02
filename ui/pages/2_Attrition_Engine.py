"""
NexaHRM — ML Attrition Risk Predictor & Burnout Diagnostic Engine
Real-time individual employee churn scoring, risk factor diagnosis,
and interactive retention raise simulator.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from ui.theme import NEXA_CSS, apply_nexa_plotly_theme
from core.predictor import predictor

st.set_page_config(page_title="Attrition Risk AI // NexaHRM", layout="wide")
st.markdown(NEXA_CSS, unsafe_allow_html=True)

# Page Header
st.markdown("""
<div class="nexa-badge"><span class="nexa-dot"></span> ML RISK DIAGNOSTICS</div>
<div class="nexa-hero-title">Individual Attrition <span>Predictor</span></div>
<div class="nexa-hero-subtitle">Input employee operational attributes to compute real-time resignation probability, identify burnout catalysts, and test retention salary adjustments.</div>
""", unsafe_allow_html=True)

st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

form_c1, form_c2, form_c3 = st.columns(3)

with form_c1:
    st.markdown("#### 1. Demographic & Compensation")
    age = st.slider("Employee Age", 18, 65, 32)
    dept = st.selectbox("Department", ["Sales", "Research & Development", "Human Resources"])
    role = st.selectbox("Job Role", [
        "Sales Executive", "Research Scientist", "Laboratory Technician",
        "Manufacturing Director", "Healthcare Representative", "Manager",
        "Sales Representative", "Research Director", "Human Resources"
    ])
    monthly_inc = st.number_input("Monthly Income ($)", min_value=1000, max_value=30000, value=5200, step=250)
    overtime = st.radio("Mandatory Overtime?", ["No", "Yes"], horizontal=True)

with form_c2:
    st.markdown("#### 2. Experience & Tenure")
    total_exp = st.slider("Total Working Experience (Years)", 0, 40, 7)
    tenure_co = st.slider("Tenure at Company (Years)", 0, 30, 3)
    role_years = st.slider("Years in Current Role", 0, 20, 2)
    promo_years = st.slider("Years Since Last Promotion", 0, 15, 1)
    mgr_years = st.slider("Years with Current Manager", 0, 20, 2)

with form_c3:
    st.markdown("#### 3. Satisfaction & Work-Life")
    env_sat = st.select_slider("Environment Satisfaction", options=[1, 2, 3, 4], value=3)
    job_sat = st.select_slider("Job Satisfaction", options=[1, 2, 3, 4], value=2)
    rel_sat = st.select_slider("Relationship Satisfaction", options=[1, 2, 3, 4], value=3)
    wlb_sat = st.select_slider("Work-Life Balance Rating", options=[1, 2, 3, 4], value=2)
    distance = st.slider("Commute Distance (Miles)", 1, 50, 12)
    marital = st.selectbox("Marital Status", ["Single", "Married", "Divorced"])
    travel = st.selectbox("Business Travel", ["Travel_Rarely", "Travel_Frequently", "Non-Travel"])

st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

emp_payload = {
    "Age": age, "Department": dept, "JobRole": role, "MonthlyIncome": monthly_inc,
    "OverTime": overtime, "TotalWorkingYears": total_exp, "YearsAtCompany": tenure_co,
    "YearsInCurrentRole": role_years, "YearsSinceLastPromotion": promo_years,
    "YearsWithCurrManager": mgr_years, "EnvironmentSatisfaction": env_sat,
    "JobSatisfaction": job_sat, "RelationshipSatisfaction": rel_sat,
    "WorkLifeBalance": wlb_sat, "DistanceFromHome": distance,
    "MaritalStatus": marital, "BusinessTravel": travel
}

res = predictor.predict_attrition(emp_payload)

# Results Display
res_c1, res_c2 = st.columns([1.2, 1.8])

with res_c1:
    st.markdown(f"""
    <div class="nexa-card" style="text-align:center;">
        <span class="pill" style="background:{res['risk_color']}20; color:{res['risk_color']}; border:1px solid {res['risk_color']}50;">
            RISK LEVEL: {res['risk_level'].upper()}
        </span>
        <div class="nexa-metric-val" style="font-size:3.5rem; color:{res['risk_color']}; margin:15px 0 5px 0;">
            {res['attrition_probability']}%
        </div>
        <div class="nexa-metric-label">Predicted Resignation Probability</div>
    </div>
    """, unsafe_allow_html=True)

with res_c2:
    st.markdown("""
    <div class="nexa-card">
        <h4 style="margin-bottom:12px;">Primary Risk Catalysts</h4>
    """, unsafe_allow_html=True)
    for driver in res["risk_drivers"]:
        st.markdown(f"- ⚠️ **{driver}**")
    st.markdown("</div>", unsafe_allow_html=True)

# Retention Salary Simulator
st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
st.markdown("### 💡 Retention Counter-Offer Simulator")

sim_c1, sim_c2 = st.columns([1.5, 2.5])
with sim_c1:
    raise_pct = st.slider("Simulate Monthly Salary Increase (%)", 0, 50, 15, step=5)
    new_inc = monthly_inc * (1 + raise_pct / 100.0)

    sim_payload = emp_payload.copy()
    sim_payload["MonthlyIncome"] = new_inc
    sim_res = predictor.predict_attrition(sim_payload)

with sim_c2:
    st.markdown(f"""
    <div class="nexa-card">
        <h4>Retention Adjustment Outcome</h4>
        <div style="display:flex; gap:30px; margin-top:12px;">
            <div>
                <div style="color:#94A3B8; font-size:0.8rem;">ORIGINAL PROBABILITY</div>
                <div style="font-size:1.8rem; font-weight:700; color:{res['risk_color']};">{res['attrition_probability']}%</div>
            </div>
            <div style="font-size:2rem; color:#00D4FF;">➔</div>
            <div>
                <div style="color:#94A3B8; font-size:0.8rem;">POST-RAISE PROBABILITY (${int(new_inc):,})</div>
                <div style="font-size:1.8rem; font-weight:700; color:{sim_res['risk_color']};">{sim_res['attrition_probability']}%</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

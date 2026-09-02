"""
NexaHRM — Executive Dashboard & Workforce Intelligence
Dark Glassmorphism UI presenting turnover rates, overtime impact, salary distributions,
performance tiers, and training allocations.
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
from core.data_loader import get_attrition_df, get_performance_df, get_training_df

st.set_page_config(page_title="Executive Analytics // NexaHRM", layout="wide")
st.markdown(NEXA_CSS, unsafe_allow_html=True)

# Page Header
st.markdown("""
<div class="nexa-badge"><span class="nexa-dot"></span> EXECUTIVE INTELLIGENCE</div>
<div class="nexa-hero-title">Workforce Dynamics & <span>Talent Distribution</span></div>
<div class="nexa-hero-subtitle">Comprehensive analytical view of retention metrics, compensation variance, organizational performance tiers, and corporate training allocations.</div>
""", unsafe_allow_html=True)

df_att = get_attrition_df()
df_perf = get_performance_df()
df_train = get_training_df()

# Filters
st.sidebar.markdown("### Segment Filter")
dept_options = sorted(df_att["Department"].unique())
selected_dept = st.sidebar.multiselect("Select Departments", options=dept_options, default=dept_options)

filtered_att = df_att[df_att["Department"].isin(selected_dept)]

st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

# Section 1: Turnover & Overtime Impact
st.markdown("### 1. Turnover Metrics & Overtime Impact")

r1_c1, r1_c2 = st.columns(2)

with r1_c1:
    role_att = (
        filtered_att.groupby("JobRole")["Attrition_Numeric"]
        .mean()
        .reset_index()
        .sort_values(by="Attrition_Numeric", ascending=True)
    )
    role_att["Attrition Rate (%)"] = (role_att["Attrition_Numeric"] * 100).round(1)

    fig_role = px.bar(
        role_att,
        x="Attrition Rate (%)",
        y="JobRole",
        orientation="h",
        color="Attrition Rate (%)",
        color_continuous_scale=[[0, "#1C2541"], [0.5, "#7C3AED"], [1, "#00D4FF"]],
        text="Attrition Rate (%)"
    )
    apply_nexa_plotly_theme(fig_role, height=380, title="Turnover Rate by Job Role (%)")
    st.plotly_chart(fig_role, use_container_width=True)

with r1_c2:
    ot_summary = (
        filtered_att.groupby(["OverTime", "Attrition"])
        .size()
        .reset_index(name="Count")
    )
    fig_ot = px.bar(
        ot_summary,
        x="OverTime",
        y="Count",
        color="Attrition",
        barmode="group",
        color_discrete_map={"No": "#10B981", "Yes": "#EF4444"}
    )
    apply_nexa_plotly_theme(fig_ot, height=380, title="Resignation Volume by Overtime Requirement")
    st.plotly_chart(fig_ot, use_container_width=True)

st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

# Section 2: Compensation Variance & Career Progression
st.markdown("### 2. Compensation Structure & Career Experience")

r2_c1, r2_c2 = st.columns(2)

with r2_c1:
    fig_sal = px.box(
        filtered_att,
        x="Department",
        y="MonthlyIncome",
        color="Attrition",
        color_discrete_map={"No": "#00D4FF", "Yes": "#EF4444"}
    )
    apply_nexa_plotly_theme(fig_sal, height=380, title="Monthly Salary Distribution by Department ($)")
    st.plotly_chart(fig_sal, use_container_width=True)

with r2_c2:
    fig_exp = px.scatter(
        filtered_att,
        x="TotalWorkingYears",
        y="MonthlyIncome",
        color="Attrition",
        size="YearsAtCompany",
        hover_data=["JobRole", "Age"],
        color_discrete_map={"No": "#10B981", "Yes": "#EF4444"}
    )
    apply_nexa_plotly_theme(fig_exp, height=380, title="Experience vs. Income Correlation (Bubble = Tenure)")
    st.plotly_chart(fig_exp, use_container_width=True)

st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

# Section 3: Performance Breakdown & Training Spend
st.markdown("### 3. Performance Breakdown & Department Training Spend")

r3_c1, r3_c2 = st.columns(2)

with r3_c1:
    tier_counts = df_perf["PerformanceTier"].value_counts().reset_index()
    tier_counts.columns = ["Tier", "Count"]
    fig_tier = px.pie(
        tier_counts,
        names="Tier",
        values="Count",
        color_discrete_sequence=["#10B981", "#00D4FF", "#7C3AED"],
        hole=0.5
    )
    apply_nexa_plotly_theme(fig_tier, height=360, title="Workforce Performance Tier Distribution")
    st.plotly_chart(fig_tier, use_container_width=True)

with r3_c2:
    dept_train = (
        df_train.groupby("DepartmentType")["Training Cost"]
        .sum()
        .reset_index()
        .sort_values(by="Training Cost", ascending=False)
    )
    fig_train = px.bar(
        dept_train,
        x="DepartmentType",
        y="Training Cost",
        color="Training Cost",
        color_continuous_scale=[[0, "#1C2541"], [1, "#00D4FF"]]
    )
    apply_nexa_plotly_theme(fig_train, height=360, title="Total Training Budget Allocation by Department ($)")
    st.plotly_chart(fig_train, use_container_width=True)

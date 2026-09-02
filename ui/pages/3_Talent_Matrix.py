"""
NexaHRM — Talent Matrix & Promotion Scoring Hub
Evaluates workforce performance tiers, promotion readiness probabilities,
and 360-degree productivity index benchmarks.
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
from core.data_loader import get_performance_df
from core.predictor import predictor

st.set_page_config(page_title="Talent Matrix // NexaHRM", layout="wide")
st.markdown(NEXA_CSS, unsafe_allow_html=True)

# Page Header
st.markdown("""
<div class="nexa-badge"><span class="nexa-dot"></span> PERFORMANCE & PROMOTION SCORING</div>
<div class="nexa-hero-title">Workforce Talent <span>Matrix</span></div>
<div class="nexa-hero-subtitle">Evaluate performance distribution tiers, simulate employee promotion readiness, and view 360° capability radar charts.</div>
""", unsafe_allow_html=True)

df_perf = get_performance_df()

st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

# Individual Promotion Readiness Calculator
st.markdown("### 1. Interactive Promotion Readiness Evaluator")

p_c1, p_c2, p_c3 = st.columns(3)

with p_c1:
    eval_dept = st.selectbox("Department", ["Sales", "IT", "Operations", "Finance"])
    eval_kpi = st.slider("Quarterly KPI Score (0-100)", 50.0, 100.0, 88.0, step=0.5)
    eval_task = st.slider("Task Completion Velocity (%)", 50.0, 100.0, 92.0, step=0.5)

with p_c2:
    eval_att = st.slider("Attendance Consistency (%)", 70.0, 100.0, 96.0, step=0.5)
    eval_peer = st.slider("Peer Review Rating (1-5)", 1.0, 5.0, 4.5, step=0.1)

with p_c3:
    eval_mgr = st.slider("Manager Leadership Feedback (1-5)", 1.0, 5.0, 4.6, step=0.1)
    eval_hrs = st.number_input("Weekly Work Hours Logged", min_value=20.0, max_value=80.0, value=42.0)

eval_payload = {
    "Department": eval_dept, "KPI Score": eval_kpi, "Task Completion (%)": eval_task,
    "Attendance (%)": eval_att, "Peer Rating": eval_peer, "Manager Feedback": eval_mgr,
    "Work Hours Logged": eval_hrs
}

prom_res = predictor.predict_promotion(eval_payload)

st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

res_col1, res_col2 = st.columns([1.2, 1.8])

with res_col1:
    st.markdown(f"""
    <div class="nexa-card" style="text-align:center;">
        <span class="pill pill-cyan">PROMOTION READINESS</span>
        <div class="nexa-metric-val" style="font-size:3.5rem; color:#00D4FF; margin:15px 0 5px 0;">
            {prom_res['promotion_probability']}%
        </div>
        <div style="font-weight:700; color:#FFFFFF; font-size:1.1rem; margin-bottom:6px;">{prom_res['promotion_tier']}</div>
        <div class="nexa-metric-label">Calculated Productivity Index: <strong>{prom_res['productivity_index']}/100</strong></div>
    </div>
    """, unsafe_allow_html=True)

with res_col2:
    categories = ['KPI Score', 'Task Completion', 'Attendance', 'Peer Rating', 'Manager Feedback']
    values = [eval_kpi, eval_task, eval_att, eval_peer * 20, eval_mgr * 20]

    fig_radar = go.Figure(data=go.Scatterpolar(
        r=values + [values[0]],
        theta=categories + [categories[0]],
        fill='toself',
        fillcolor='rgba(0, 212, 255, 0.25)',
        line=dict(color='#00D4FF', width=2)
    ))

    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], gridcolor="rgba(255,255,255,0.1)"),
            angularaxis=dict(gridcolor="rgba(255,255,255,0.1)")
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#94A3B8"),
        margin=dict(l=40, r=40, t=30, b=30),
        height=320
    )
    st.plotly_chart(fig_radar, use_container_width=True)

st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

# 2. Performance Tier Distribution Matrix
st.markdown("### 2. Departmental Productivity Index Benchmark")

fig_box = px.box(
    df_perf,
    x="Department",
    y="ProductivityIndex",
    color="PerformanceTier",
    color_discrete_map={"High Performer": "#10B981", "Proficient": "#00D4FF", "Developing": "#EF4444"}
)
apply_nexa_plotly_theme(fig_box, height=360, title="Productivity Index Spread across Departments")
st.plotly_chart(fig_box, use_container_width=True)

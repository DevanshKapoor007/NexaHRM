"""
NexaHRM — O*NET Career Pathway & Skill Gap Recommendation Engine
Interactive occupation search, skill gap overlay, provider-filtered course catalog,
and downloadable 30-60-90 Day Upskilling Roadmap.
"""

import streamlit as st
import pandas as pd
import numpy as np
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from ui.theme import NEXA_CSS, apply_nexa_plotly_theme
from core.recommender import recommender
from core.course_matcher import course_matcher

st.set_page_config(page_title="Career Pathways // NexaHRM", layout="wide")
st.markdown(NEXA_CSS, unsafe_allow_html=True)

# Page Header
st.markdown("""
<div class="nexa-badge"><span class="nexa-dot"></span> CAREER INTELLIGENCE</div>
<div class="nexa-hero-title">O*NET Skill Gap & <span>Pathways Hub</span></div>
<div class="nexa-hero-subtitle">Compare current vs. target roles across 1,016 O*NET occupations, diagnose missing software tools, and generate 30-60-90 day course roadmaps.</div>
""", unsafe_allow_html=True)

st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

# Role Selection
sel_c1, sel_c2 = st.columns(2)

with sel_c1:
    st.markdown("#### Current Role Search")
    curr_q = st.text_input("Search Current Role", value="Sales Representatives", key="curr_q")
    curr_results = recommender.search_roles(curr_q, limit=10)
    curr_soc = st.selectbox("Select Current Role", [f"{r['O*NET-SOC Code']} — {r['Title']}" for r in curr_results], key="curr_soc")
    curr_code = curr_soc.split(" — ")[0] if curr_soc else "41-3091.00"

with sel_c2:
    st.markdown("#### Target Promotion Role Search")
    tgt_q = st.text_input("Search Target Role", value="Sales Managers", key="tgt_q")
    tgt_results = recommender.search_roles(tgt_q, limit=10)
    tgt_soc = st.selectbox("Select Target Role", [f"{r['O*NET-SOC Code']} — {r['Title']}" for r in tgt_results], key="tgt_soc")
    tgt_code = tgt_soc.split(" — ")[0] if tgt_soc else "11-2022.00"

# Enhancement: Provider Filter
st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
provider_filter = st.selectbox(
    "🎓 Filter Course Providers",
    ["All Providers", "Coursera", "edX", "Udemy", "AWS", "Google", "Wharton"],
    key="prov_filter"
)

st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

# Run Role Comparison
comp = recommender.compare_roles(curr_code, tgt_code)

# Role Comparison Metrics Header
m_col1, m_col2, m_col3 = st.columns(3)

with m_col1:
    st.markdown(f"""
    <div class="nexa-card">
        <div class="pill pill-cyan">COMPETENCY MATCH</div>
        <div class="nexa-metric-val" style="color:#00D4FF;">{comp['skill_match_pct']}%</div>
        <div class="nexa-metric-label">{comp['shared_skills_count']} Shared Core Skills</div>
    </div>
    """, unsafe_allow_html=True)

with m_col2:
    st.markdown(f"""
    <div class="nexa-card">
        <div class="pill pill-purple">TRANSITION DIFFICULTY</div>
        <div class="nexa-metric-val" style="font-size:1.5rem; color:{comp['diff_color']}; font-family:'Inter'; font-weight:700; margin:14px 0;">
            {comp['transition_difficulty']}
        </div>
        <div class="nexa-metric-label">O*NET Taxonomy Benchmark</div>
    </div>
    """, unsafe_allow_html=True)

with m_col3:
    st.markdown(f"""
    <div class="nexa-card">
        <div class="pill pill-emerald">TARGET ROLE</div>
        <div style="font-size:1.2rem; font-weight:700; color:#FFFFFF; margin:14px 0 6px 0;">{comp['target_title']}</div>
        <div class="nexa-metric-label">SOC: {tgt_code}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

# Missing Skills & Software Tools
gap_c1, gap_c2 = st.columns(2)

with gap_c1:
    st.markdown("### 1. Missing Core Competencies")
    if comp["missing_skills"]:
        for s in comp["missing_skills"][:6]:
            st.markdown(f"""
            <div class="nexa-card" style="padding:0.8rem 1.2rem; margin-bottom:8px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-weight:700; color:#FFFFFF;">{s['skill']}</span>
                    <span class="pill pill-amber">Importance: {s['importance']}/5.0</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success("No critical skill gaps identified! Excellent role overlap.")

with gap_c2:
    st.markdown("### 2. Required Software & Tech Stack")
    if comp["missing_software"]:
        for sw in comp["missing_software"][:6]:
            hot_badge = "<span class='pill pill-rose'>Hot Tech</span>" if sw.get("is_hot_tech") else ""
            st.markdown(f"""
            <div class="nexa-card" style="padding:0.8rem 1.2rem; margin-bottom:8px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-weight:700; color:#00D4FF;">{sw['tool']}</span>
                    {hot_badge}
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Software stack matches target requirements.")

# Generate 30-60-90 Day Roadmap
st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
st.markdown("### 📅 AI 30-60-90 Day Upskilling Roadmap")

plan = course_matcher.generate_30_60_90_plan(
    current_role=comp["current_title"],
    target_role=comp["target_title"],
    missing_skills=comp["missing_skills"],
    missing_tools=comp["missing_software"],
    provider_filter=provider_filter
)

for p in plan["phases"]:
    with st.container():
        st.markdown(f"""
        <div class="nexa-card">
            <h4>{p['phase']}: {p['title']}</h4>
            <p style="color:#94A3B8;">Focus Skill: <span class="pill pill-cyan">{p['focus_skill']}</span> | Target Tool: <span class="pill pill-purple">{p['target_tool']}</span></p>
            <p><strong>Deliverable:</strong> <em>{p['deliverable']}</em></p>
        </div>
        """, unsafe_allow_html=True)

# Export Plan
st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
plan_md = course_matcher.export_plan_markdown(plan)

st.download_button(
    label="📥 DOWNLOAD CAREER ROADMAP (MARKDOWN)",
    data=plan_md,
    file_name=f"roadmap_{comp['target_title'].lower().replace(' ', '_')}.md",
    mime="text/markdown",
    use_container_width=True
)

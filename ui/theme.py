"""
NexaHRM — Dark Glassmorphism Design System & Theme Engine
Premium dark mode styling with cyan/purple accents, glassmorphic cards,
glowing metric badges, and custom Plotly theme integration.
"""

import plotly.graph_objects as go
import plotly.express as px

NEXA_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600;700&display=swap');

/* Reset & Global Root Vars */
:root {
    --nexa-bg: #0B132B;
    --nexa-card: rgba(28, 37, 65, 0.55);
    --nexa-card-hover: rgba(28, 37, 65, 0.75);
    --nexa-border: rgba(0, 212, 255, 0.15);
    --nexa-border-glow: rgba(0, 212, 255, 0.4);
    --nexa-cyan: #00D4FF;
    --nexa-purple: #7C3AED;
    --nexa-emerald: #10B981;
    --nexa-amber: #F59E0B;
    --nexa-rose: #EF4444;
    --nexa-text-main: #F8FAFC;
    --nexa-text-sub: #94A3B8;
}

/* Base Body Theme Overrides */
.stApp {
    background: radial-gradient(circle at 50% 0%, #1C2541 0%, #0B132B 75%);
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    color: var(--nexa-text-main);
}

/* Header & Typography */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Inter', sans-serif !important;
    font-weight: 700 !important;
    color: #FFFFFF !important;
    letter-spacing: -0.02em;
}

/* Glassmorphism Cards */
.nexa-card {
    background: var(--nexa-card);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid var(--nexa-border);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1.2rem;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.nexa-card:hover {
    background: var(--nexa-card-hover);
    border-color: var(--nexa-border-glow);
    box-shadow: 0 12px 40px 0 rgba(0, 212, 255, 0.12);
    transform: translateY(-2px);
}

/* Badges & Pills */
.nexa-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 12px;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    background: rgba(0, 212, 255, 0.1);
    color: var(--nexa-cyan);
    border: 1px solid rgba(0, 212, 255, 0.25);
}

.nexa-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background-color: var(--nexa-cyan);
    box-shadow: 0 0 8px var(--nexa-cyan);
    display: inline-block;
}

.pill {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
}

.pill-cyan { background: rgba(0, 212, 255, 0.15); color: #38BDF8; border: 1px solid rgba(0, 212, 255, 0.3); }
.pill-purple { background: rgba(124, 58, 237, 0.2); color: #A78BFA; border: 1px solid rgba(124, 58, 237, 0.4); }
.pill-emerald { background: rgba(16, 185, 129, 0.15); color: #34D399; border: 1px solid rgba(16, 185, 129, 0.3); }
.pill-amber { background: rgba(245, 158, 11, 0.15); color: #FBBF24; border: 1px solid rgba(245, 158, 11, 0.3); }
.pill-rose { background: rgba(239, 68, 68, 0.15); color: #F87171; border: 1px solid rgba(239, 68, 68, 0.3); }

/* Metric Display Values */
.nexa-metric-val {
    font-family: 'JetBrains Mono', monospace;
    font-size: 2.2rem;
    font-weight: 700;
    color: #FFFFFF;
    margin: 8px 0 4px 0;
    letter-spacing: -0.03em;
    text-shadow: 0 0 20px rgba(0, 212, 255, 0.2);
}

.nexa-metric-label {
    color: var(--nexa-text-sub);
    font-size: 0.82rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* Custom Buttons */
.stButton > button {
    background: linear-gradient(135deg, #00D4FF 0%, #7C3AED 100%) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    padding: 0.6rem 1.4rem !important;
    letter-spacing: 0.02em !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 15px rgba(0, 212, 255, 0.2) !important;
}

.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 25px rgba(0, 212, 255, 0.4) !important;
    opacity: 0.95 !important;
}

/* Sidebar Dark Styling */
[data-testid="stSidebar"] {
    background: #070D1E !important;
    border-right: 1px solid var(--nexa-border) !important;
}

[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
    color: var(--nexa-cyan) !important;
}

/* Form Inputs */
.stTextInput input, .stSelectbox select, .stMultiselect {
    background: rgba(15, 23, 42, 0.7) !important;
    border: 1px solid var(--nexa-border) !important;
    border-radius: 8px !important;
    color: #FFFFFF !important;
}

.stTextInput input:focus {
    border-color: var(--nexa-cyan) !important;
    box-shadow: 0 0 10px rgba(0, 212, 255, 0.3) !important;
}

/* Hero titles */
.nexa-hero-title {
    font-size: 3rem;
    font-weight: 800;
    line-height: 1.15;
    background: linear-gradient(135deg, #FFFFFF 30%, #00D4FF 70%, #A78BFA 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.nexa-hero-subtitle {
    color: var(--nexa-text-sub);
    font-size: 1.1rem;
    line-height: 1.6;
}
</style>
"""


def apply_nexa_plotly_theme(fig, height=360, title=""):
    """Applies NexaHRM dark glassmorphism theme to Plotly figures."""
    fig.update_layout(
        height=height,
        title=dict(
            text=title,
            font=dict(family="Inter", size=15, color="#FFFFFF", weight="bold"),
            x=0.0,
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color="#94A3B8", size=12),
        margin=dict(l=20, r=20, t=50, b=20),
        xaxis=dict(
            gridcolor="rgba(255,255,255,0.06)",
            zerolinecolor="rgba(255,255,255,0.1)",
            tickfont=dict(color="#94A3B8"),
        ),
        yaxis=dict(
            gridcolor="rgba(255,255,255,0.06)",
            zerolinecolor="rgba(255,255,255,0.1)",
            tickfont=dict(color="#94A3B8"),
        ),
        legend=dict(
            font=dict(color="#F8FAFC"),
            bgcolor="rgba(15, 23, 42, 0.6)",
            bordercolor="rgba(0, 212, 255, 0.2)",
            borderwidth=1,
        ),
    )
    return fig

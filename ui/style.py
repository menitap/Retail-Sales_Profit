"""
UI Styling and Design Module for Retail Sales and Profitability Analysis.
Provides custom CSS, modern executive card components, color palettes,
and Plotly chart formatting for a unified business analytics presentation.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

# Enterprise Color Palette
PRIMARY_COLOR = "#3B82F6"      # Royal Blue
SECONDARY_COLOR = "#10B981"    # Emerald Green
ACCENT_COLOR = "#8B5CF6"       # Violet
WARNING_COLOR = "#F59E0B"      # Amber
DANGER_COLOR = "#EF4444"       # Crimson Rose
DARK_BG = "#0F172A"            # Slate 900
CARD_BG = "#1E293B"            # Slate 800
BORDER_COLOR = "#334155"       # Slate 700
TEXT_MUTED = "#94A3B8"         # Slate 400
TEXT_LIGHT = "#F8FAFC"         # Slate 50

def apply_custom_css():
    """Injects high-end, responsive executive CSS styles into the Streamlit app."""
    custom_css = """
    <style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }

    /* Main Container Padding */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2.5rem;
        padding-left: 2rem;
        padding-right: 2rem;
        max-width: 1400px;
    }

    /* Top Banner Styling */
    .app-header-container {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 1.5rem 2rem;
        margin-bottom: 1.75rem;
        box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.25);
    }

    .app-title {
        font-size: 1.85rem;
        font-weight: 800;
        letter-spacing: -0.025em;
        background: linear-gradient(90deg, #60A5FA 0%, #A78BFA 50%, #34D399 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        padding-bottom: 0.35rem;
    }

    .app-subtitle {
        font-size: 0.95rem;
        color: #94a3b8;
        margin: 0;
        font-weight: 400;
    }

    /* KPI Metric Cards */
    .kpi-card {
        background: linear-gradient(145deg, #1e293b, #172033);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1.25rem 1.2rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
        position: relative;
        overflow: hidden;
    }

    .kpi-card:hover {
        transform: translateY(-2px);
        border-color: #60a5fa;
        box-shadow: 0 8px 24px rgba(37, 99, 235, 0.18);
    }

    .kpi-card-glow-blue { border-left: 4px solid #3b82f6; }
    .kpi-card-glow-green { border-left: 4px solid #10b981; }
    .kpi-card-glow-purple { border-left: 4px solid #8b5cf6; }
    .kpi-card-glow-amber { border-left: 4px solid #f59e0b; }
    .kpi-card-glow-rose { border-left: 4px solid #ef4444; }

    .kpi-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 0.5rem;
    }

    .kpi-title {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #94a3b8;
        font-weight: 600;
    }

    .kpi-icon {
        font-size: 1.25rem;
        opacity: 0.9;
    }

    .kpi-value {
        font-size: 1.85rem;
        font-weight: 700;
        color: #f8fafc;
        line-height: 1.2;
        margin-bottom: 0.35rem;
    }

    .kpi-subtext {
        font-size: 0.78rem;
        color: #cbd5e1;
        display: flex;
        align-items: center;
        gap: 0.35rem;
    }

    /* Badges */
    .badge-chip {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 0.25rem 0.65rem;
        border-radius: 9999px;
    }

    .badge-success {
        background-color: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }

    .badge-info {
        background-color: rgba(59, 130, 246, 0.15);
        color: #60a5fa;
        border: 1px solid rgba(59, 130, 246, 0.3);
    }

    .badge-warning {
        background-color: rgba(245, 158, 11, 0.15);
        color: #fbbf24;
        border: 1px solid rgba(245, 158, 11, 0.3);
    }

    /* Insight Banner */
    .insight-card {
        background: linear-gradient(90deg, rgba(30, 41, 59, 0.9), rgba(15, 23, 42, 0.9));
        border: 1px solid #334155;
        border-left: 4px solid #6366f1;
        border-radius: 10px;
        padding: 1rem 1.25rem;
        margin-bottom: 1.25rem;
    }

    .insight-title {
        font-size: 0.9rem;
        font-weight: 700;
        color: #e2e8f0;
        margin-bottom: 0.3rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .insight-desc {
        font-size: 0.85rem;
        color: #94a3b8;
        line-height: 1.45;
        margin: 0;
    }

    /* Section Subheaders */
    .section-header {
        font-size: 1.25rem;
        font-weight: 700;
        color: #f1f5f9;
        margin-top: 1.25rem;
        margin-bottom: 0.75rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        border-bottom: 1px solid #334155;
        padding-bottom: 0.5rem;
    }

    /* Sidebar Customization */
    section[data-testid="stSidebar"] {
        background-color: #0b1120;
        border-right: 1px solid #1e293b;
    }

    /* Plotly Chart Card Container */
    .chart-container {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
    }

    /* Streamlit Buttons */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.85rem;
        transition: all 0.2s ease;
    }

    /* Code styling */
    code {
        font-family: 'JetBrains Mono', monospace !important;
        background-color: #1e293b !important;
        padding: 0.15rem 0.4rem !important;
        border-radius: 4px !important;
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

def render_kpi_card(title, value, subtitle=None, icon="📈", glow_color="blue"):
    """Renders a styled HTML KPI card."""
    valid_glows = ["blue", "green", "purple", "amber", "rose"]
    glow_class = f"kpi-card-glow-{glow_color if glow_color in valid_glows else 'blue'}"
    subtext_html = f"<div class='kpi-subtext'>{subtitle}</div>" if subtitle else ""

    html = f"""
    <div class="kpi-card {glow_class}">
        <div class="kpi-header">
            <span class="kpi-title">{title}</span>
            <span class="kpi-icon">{icon}</span>
        </div>
        <div class="kpi-value">{value}</div>
        {subtext_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def render_insight_box(title, message, icon="💡", border_color="#6366f1"):
    """Renders an executive highlight or strategic insight card."""
    html = f"""
    <div class="insight-card" style="border-left-color: {border_color};">
        <div class="insight-title">{icon} {title}</div>
        <div class="insight-desc">{message}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def render_section_title(title, icon="📌"):
    """Renders a clean styled section header with an icon."""
    html = f"""
    <div class="section-header">
        <span>{icon}</span> <span>{title}</span>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def get_plotly_layout(height=380, title="", showlegend=True):
    """Returns a unified, high-contrast dark Plotly layout dict."""
    return {
        "title": {
            "text": title,
            "font": {"size": 14, "color": "#f1f5f9", "family": "Inter"},
            "x": 0.02,
            "y": 0.96
        },
        "height": height,
        "margin": dict(l=40, r=30, t=50, b=40),
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {"family": "Inter", "color": "#94a3b8", "size": 11},
        "showlegend": showlegend,
        "legend": {
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "right",
            "x": 1,
            "font": {"size": 11, "color": "#cbd5e1"}
        },
        "xaxis": {
            "gridcolor": "#334155",
            "zerolinecolor": "#475569",
            "showgrid": True,
            "tickfont": {"color": "#94a3b8"}
        },
        "yaxis": {
            "gridcolor": "#334155",
            "zerolinecolor": "#475569",
            "showgrid": True,
            "tickfont": {"color": "#94a3b8"}
        },
        "hoverlabel": {
            "bgcolor": "#1e293b",
            "bordercolor": "#475569",
            "font": {"family": "Inter", "size": 12, "color": "#f8fafc"}
        }
    }

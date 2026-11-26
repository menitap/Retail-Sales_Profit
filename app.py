"""
Retail Sales and Profitability Analysis — Main Entry Point.
Green / Brown / Beige earthy professional theme.
Top horizontal navigation, light/dark toggle, zero-scroll viewport.
"""

import streamlit as st

st.set_page_config(
    page_title="Retail Sales & Profitability",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Initialise theme before CSS injection
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "dark"

from ui.style import apply_custom_css
apply_custom_css()

from backend import get_engine
from ui.home import render_home
from ui.dashboard import render_dashboard
from ui.data_overview import render_data_overview
from ui.data_cleaning import render_data_cleaning
from ui.visualizations import render_sales_analysis
from ui.discount_analysis import render_discount_analysis
from ui.time_analysis import render_time_analysis
from ui.performance import render_performance_evaluation
from ui.loss_detection import render_loss_detection
from ui.loss_dna import render_loss_dna
from ui.what_if import render_what_if


@st.cache_resource(show_spinner=False)
def load_backend_data():
    return get_engine()


def main():
    with st.spinner("Loading retail analytics engine…"):
        engine = load_backend_data()
        df     = engine.get_cleaned_data()
        status = engine.get_engine_status()

    PAGES = [
        "Home", "Dashboard", "Data Overview", "Data Cleaning",
        "Sales Analysis", "Discount Analysis", "Time Trends",
        "Performance", "Loss Detection", "Loss DNA", "What-If",
    ]
    LEGACY_MAP = {
        "🏠 Dashboard Home": "Dashboard",
        "📋 Data Overview": "Data Overview",
        "🧹 Data Cleaning": "Data Cleaning",
        "📊 Sales Analysis": "Sales Analysis",
        "🏷️ Discount Analysis": "Discount Analysis",
        "📈 Time-Based Analysis": "Time Trends",
        "⚡ Performance Evaluation": "Performance",
        "🎯 Profitability Risk Detection": "Loss Detection",
        "Loss DNA: SHAP Explainability": "Loss DNA",
        "What-If Simulator": "What-If",
    }

    if "current_page" not in st.session_state or st.session_state.current_page not in PAGES:
        raw = st.session_state.get("current_page", "Home")
        st.session_state.current_page = LEGACY_MAP.get(raw, "Home")

    light = st.session_state.theme_mode == "light"

    # ── Earthy theme token shortcuts for inline HTML ───────────────────────
    if light:
        brand_text   = "#2C1A0E"
        brand_accent = "#3D7A5A"
        sub_text     = "#7A6B58"
        btn_bg       = "#EDE8DC"
        btn_border   = "#C8BFA8"
        btn_text_col = "#4A3728"
        sb_title     = "#2C1A0E"
        sb_sub       = "#3D7A5A"
        sb_card_bg   = "#FDFAF4"
        sb_card_brd  = "#C8BFA8"
        sb_muted     = "#7A6B58"
        sb_green     = "#3D7A5A"
    else:
        brand_text   = "#F0EBD8"
        brand_accent = "#78C8A0"
        sub_text     = "#8A9E82"
        btn_bg       = "#1F2B1C"
        btn_border   = "#354A30"
        btn_text_col = "#D8D0BA"
        sb_title     = "#F0EBD8"
        sb_sub       = "#78C8A0"
        sb_card_bg   = "#1F2B1C"
        sb_card_brd  = "#354A30"
        sb_muted     = "#8A9E82"
        sb_green     = "#5C9E78"

    # ── Top navigation bar: brand | nav pills | theme toggle ──────────────
    nav_col1, nav_col2, nav_col3 = st.columns([0.26, 1.60, 0.14], vertical_alignment="center")

    with nav_col1:
        st.markdown(
            f"""<div style="display:flex;align-items:center;gap:0.35rem;height:34px;overflow:hidden;">
<span style="font-size:0.92rem;font-weight:800;color:{brand_accent};white-space:nowrap;letter-spacing:-0.01em;">🌿 Retail Analytics</span>
<span style="font-size:0.56rem;color:{sub_text};font-weight:600;text-transform:uppercase;letter-spacing:0.06em;white-space:nowrap;">Spark 4.3</span>
</div>""",
            unsafe_allow_html=True,
        )

    with nav_col2:
        selected_page = st.radio(
            "nav", PAGES,
            index=PAGES.index(st.session_state.current_page),
            key="nav_selection",
            horizontal=True,
            label_visibility="collapsed",
        )
        st.session_state.current_page = selected_page

    with nav_col3:
        icon  = "☀️" if st.session_state.theme_mode == "dark" else "🌙"
        label = "Light" if st.session_state.theme_mode == "dark" else "Dark"
        if st.button(f"{icon} {label}", key="theme_toggle", use_container_width=True):
            st.session_state.theme_mode = "light" if st.session_state.theme_mode == "dark" else "dark"
            st.rerun()

    # ── Sidebar ────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown(
            f"""<div style="padding:0.3rem 0 0.6rem 0;">
<div style="font-size:1.0rem;font-weight:800;color:{sb_title};">🌿 Retail Sales & Profit</div>
<div style="font-size:0.7rem;color:{sb_sub};font-weight:600;text-transform:uppercase;letter-spacing:0.06em;">Analytics • Apache Spark</div>
</div>""",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"""<div style="background:{sb_card_bg};border:1px solid {sb_card_brd};border-radius:8px;padding:0.6rem;font-size:0.74rem;margin-bottom:0.7rem;">
<div style="color:{sb_green};font-weight:700;margin-bottom:0.2rem;">● Dataset Loaded</div>
<div style="color:{sb_muted};font-family:monospace;font-size:0.68rem;">ecommerce_orders_dataset.csv</div>
<div style="color:{sb_muted};font-size:0.68rem;margin-top:0.2rem;">Rows: {len(df):,} | Cols: {len(df.columns)}</div>
</div>""",
            unsafe_allow_html=True,
        )
        spark_color = sb_green if status.get("is_pyspark_active", False) else sb_sub
        st.markdown(
            f"""<div style="background:{sb_card_bg};border:1px solid {sb_card_brd};border-radius:8px;padding:0.6rem;font-size:0.74rem;margin-bottom:0.7rem;">
<div style="color:{spark_color};font-weight:700;margin-bottom:0.2rem;">● {status.get('name','Backend')}</div>
<div style="color:{sb_muted};font-size:0.68rem;line-height:1.3;">{str(status.get('details',''))[:80]}…</div>
</div>""",
            unsafe_allow_html=True,
        )
        if st.button("🔄 Refresh Cache", use_container_width=True):
            st.cache_resource.clear()
            st.cache_data.clear()
            st.rerun()

    # ── Page routing ───────────────────────────────────────────────────────
    if   selected_page == "Home":            render_home(df)
    elif selected_page == "Dashboard":       render_dashboard(df)
    elif selected_page == "Data Overview":   render_data_overview()
    elif selected_page == "Data Cleaning":   render_data_cleaning()
    elif selected_page == "Sales Analysis":  render_sales_analysis(df)
    elif selected_page == "Discount Analysis": render_discount_analysis(df)
    elif selected_page == "Time Trends":     render_time_analysis(df)
    elif selected_page == "Performance":     render_performance_evaluation()
    elif selected_page == "Loss Detection":  render_loss_detection(df)
    elif selected_page == "Loss DNA":        render_loss_dna(df)
    elif selected_page == "What-If":         render_what_if(df)


if __name__ == "__main__":
    main()

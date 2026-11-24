"""
Retail Sales and Profitability Analysis Using Apache Spark
Main Streamlit Application Entry Point.
"""

import streamlit as st
import time

# Page configuration - must be first Streamlit command
st.set_page_config(
    page_title="Retail Sales & Profitability Analysis | Apache Spark",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply UI Styling & CSS
from ui.style import apply_custom_css
apply_custom_css()

# Import backend engine and analytics
from backend import get_engine
from ui.dashboard import render_dashboard
from ui.data_overview import render_data_overview
from ui.data_cleaning import render_data_cleaning
from ui.visualizations import render_sales_analysis
from ui.discount_analysis import render_discount_analysis
from ui.time_analysis import render_time_analysis
from ui.performance import render_performance_evaluation
from ui.what_if import render_what_if
from ui.loss_dna import render_loss_dna
from ui.loss_detection import render_loss_detection

# Cached backend engine getter to prevent re-computation across page navigations
@st.cache_resource(show_spinner=False)
def load_backend_data():
    engine = get_engine()
    return engine

def main():
    # Initialize backend engine and data
    with st.spinner("Connecting to Apache Spark backend and loading pre-existing dataset..."):
        engine = load_backend_data()
        df = engine.get_cleaned_data()
        status = engine.get_engine_status()

    # Sidebar Navigation & Telemetry
    with st.sidebar:
        # App Branding Header
        st.markdown(
            """
            <div style="padding: 0.5rem 0 1rem 0;">
                <div style="font-size: 1.2rem; font-weight: 800; color: #f8fafc; letter-spacing: -0.02em;">
                    ⚡ Retail Sales & Profit
                </div>
                <div style="font-size: 0.78rem; color: #60a5fa; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">
                    Big Data Analytics • Apache Spark
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("---")

        # Page Navigation
        st.markdown(
            "<div style='font-size: 0.75rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;'>Navigation</div>",
            unsafe_allow_html=True
        )

        pages = [
            "🏠 Dashboard Home",
            "📋 Data Overview",
            "🧹 Data Cleaning",
            "📊 Sales Analysis",
            "🏷️ Discount Analysis",
            "📈 Time-Based Analysis",
            "⚡ Performance Evaluation",
            "What-If Simulator",
            "Loss DNA: SHAP Explainability",
            "🎯 Profitability Risk Detection"
        ]

        # Use session state to retain active page
        if "current_page" not in st.session_state:
            st.session_state.current_page = pages[0]

        selected_page = st.radio(
            "Select Module",
            pages,
            index=pages.index(st.session_state.current_page) if st.session_state.current_page in pages else 0,
            label_visibility="collapsed"
        )
        st.session_state.current_page = selected_page

        st.markdown("---")

        # Pre-loaded Dataset Status (Strictly NO upload option)
        st.markdown(
            """
            <div style="font-size: 0.75rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;">
                Dataset Source
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown(
            f"""
            <div style="background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 0.75rem; font-size: 0.8rem;">
                <div style="color: #34d399; font-weight: 600; display: flex; align-items: center; gap: 0.35rem; margin-bottom: 0.25rem;">
                    ● Pre-loaded & Verified
                </div>
                <div style="color: #cbd5e1; word-break: break-all; font-family: monospace; font-size: 0.75rem;">
                    data/ecommerce_orders_dataset.csv
                </div>
                <div style="color: #94a3b8; font-size: 0.72rem; margin-top: 0.35rem;">
                    Rows: {len(df):,} | Attributes: {len(df.columns)}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("---")

        # Spark Backend Status Chip
        st.markdown(
            """
            <div style="font-size: 0.75rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;">
                Spark Backend Status
            </div>
            """,
            unsafe_allow_html=True
        )
        status_color = "#34d399" if status["is_pyspark_active"] else "#60a5fa"
        st.markdown(
            f"""
            <div style="background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 0.75rem; font-size: 0.8rem;">
                <div style="color: {status_color}; font-weight: 600; margin-bottom: 0.2rem;">
                    ● {status['name']}
                </div>
                <div style="color: #94a3b8; font-size: 0.72rem; line-height: 1.3;">
                    {status['details'][:80]}...
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)

        if st.button("🔄 Refresh Data Cache", use_container_width=True):
            st.cache_resource.clear()
            st.rerun()

        # Footer
        st.markdown(
            """
            <div style="font-size: 0.7rem; color: #64748b; text-align: center; margin-top: 2rem;">
                Apache Spark 4.3 • Streamlit • Plotly<br>
                Big Data Analytics Project
            </div>
            """,
            unsafe_allow_html=True
        )

    # Main Application Header Container
    st.markdown(
        """
        <div class="app-header-container">
            <h1 class="app-title">Retail Sales & Profitability Analysis Using Apache Spark</h1>
            <p class="app-subtitle">
                Enterprise big data analytics engine processing 2026 e-commerce orders with distributed Spark transformations.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Page Routing
    if selected_page == "🏠 Dashboard Home":
        render_dashboard(df)
    elif selected_page == "📋 Data Overview":
        render_data_overview()
    elif selected_page == "🧹 Data Cleaning":
        render_data_cleaning()
    elif selected_page == "📊 Sales Analysis":
        render_sales_analysis(df)
    elif selected_page == "🏷️ Discount Analysis":
        render_discount_analysis(df)
    elif selected_page == "📈 Time-Based Analysis":
        render_time_analysis(df)
    elif selected_page == "⚡ Performance Evaluation":
        render_performance_evaluation()
    elif selected_page == "What-If Simulator":
        render_what_if(df)
    elif selected_page == "Loss DNA: SHAP Explainability":
        render_loss_dna(df)
    elif selected_page == "🎯 Profitability Risk Detection":
        render_loss_detection(df)

if __name__ == "__main__":
    main()

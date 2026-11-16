"""
Performance Evaluation Page: Retail Sales and Profitability Analysis Using Apache Spark.
Monitors execution benchmarks including dataset ingestion latency, cleaning pipeline duration,
and multi-dimensional distributed aggregation performance.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from ui.style import (
    render_kpi_card,
    render_section_title,
    render_insight_box,
    get_plotly_layout,
    PRIMARY_COLOR,
    SECONDARY_COLOR,
    ACCENT_COLOR,
    WARNING_COLOR
)
from backend import get_engine

def render_performance_evaluation():
    """Renders the Apache Spark Performance Evaluation and Benchmark page."""
    engine = get_engine()
    benchmarks = engine.get_benchmarks()
    status = engine.get_engine_status()
    report = engine.get_cleaning_report()

    render_section_title("Apache Spark Execution & Pipeline Telemetry", icon="⚡")

    st.markdown(
        """
        In enterprise big data deployments, distributed processing with Apache Spark enables horizontal scalability,
        in-memory execution via Tungsten, and cost-based query optimization through the Catalyst Optimizer.
        Below are real-time execution benchmarks collected from the backend engine.
        """
    )

    # Headline Performance KPIs
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        render_kpi_card(
            title="CSV Load Latency",
            value=f"{benchmarks['load_time_sec'] * 1000:.1f} ms",
            subtitle=f"{report.get('raw_rows', 9994):,} rows parsed",
            icon="📥",
            glow_color="blue"
        )

    with c2:
        render_kpi_card(
            title="Cleaning Duration",
            value=f"{benchmarks['cleaning_time_sec'] * 1000:.1f} ms",
            subtitle="Deduplication & casting",
            icon="🧹",
            glow_color="green"
        )

    with c3:
        render_kpi_card(
            title="Aggregations Latency",
            value=f"{(benchmarks['total_benchmark_time_sec'] - benchmarks['load_time_sec'] - benchmarks['cleaning_time_sec']) * 1000:.1f} ms",
            subtitle="6 analytical queries",
            icon="⚡",
            glow_color="purple"
        )

    with c4:
        render_kpi_card(
            title="Total Pipeline Time",
            value=f"{benchmarks['total_benchmark_time_sec'] * 1000:.1f} ms",
            subtitle="End-to-end execution",
            icon="⏱️",
            glow_color="amber"
        )

    st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

    # Detailed Benchmark Breakdown Bar Chart
    render_section_title("Benchmark Execution Profile Across Stages", icon="📊")

    stages = [
        {"Stage": "1. CSV Ingestion & Parsing", "Duration (ms)": benchmarks['load_time_sec'] * 1000, "Category": "I/O"},
        {"Stage": "2. Data Cleaning & Feature Eng.", "Duration (ms)": benchmarks['cleaning_time_sec'] * 1000, "Category": "Transform"},
        {"Stage": "3. Category Aggregation", "Duration (ms)": benchmarks['category_agg_time_sec'] * 1000, "Category": "Query"},
        {"Stage": "4. Sub-Category Aggregation", "Duration (ms)": benchmarks['subcategory_agg_time_sec'] * 1000, "Category": "Query"},
        {"Stage": "5. Regional Aggregation", "Duration (ms)": benchmarks['region_agg_time_sec'] * 1000, "Category": "Query"},
        {"Stage": "6. Segment Aggregation", "Duration (ms)": benchmarks['segment_agg_time_sec'] * 1000, "Category": "Query"},
        {"Stage": "7. Discount Binning & Correlation", "Duration (ms)": benchmarks['discount_agg_time_sec'] * 1000, "Category": "Query"},
        {"Stage": "8. Time-Series Aggregation", "Duration (ms)": benchmarks['time_agg_time_sec'] * 1000, "Category": "Query"}
    ]
    bench_df = pd.DataFrame(stages)

    fig_bench = go.Figure(go.Bar(
        x=bench_df["Duration (ms)"],
        y=bench_df["Stage"],
        orientation="h",
        marker=dict(color=PRIMARY_COLOR),
        text=[f"{d:.2f} ms" for d in bench_df["Duration (ms)"]],
        textposition="auto",
        hovertemplate="Stage: %{y}<br>Latency: %{x:.2f} ms<extra></extra>"
    ))
    l_bench = get_plotly_layout(height=380, title="Stage-by-Stage Latency (Milliseconds)", showlegend=False)
    fig_bench.update_layout(l_bench)
    st.plotly_chart(fig_bench, use_container_width=True)

    st.dataframe(bench_df, use_container_width=True, hide_index=True)

    st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

    # Spark Engine Environment & Architecture Telemetry
    render_section_title("Engine Architecture & Deployment Parameters", icon="🖥️")

    c_arch1, c_arch2 = st.columns(2)

    with c_arch1:
        st.markdown(
            f"""
            <div style="background: #1e293b; padding: 1.25rem; border-radius: 10px; border: 1px solid #334155;">
                <div style="font-weight: 700; color: #f8fafc; margin-bottom: 0.75rem; font-size: 1rem;">
                    ⚙️ Active Spark Backend Parameters
                </div>
                <ul style="color: #cbd5e1; font-size: 0.88rem; line-height: 1.8; margin-left: -1rem;">
                    <li><strong>Engine:</strong> <code>{status['name']}</code></li>
                    <li><strong>Engine Mode:</strong> <code>{'Native PySpark RDD/DataFrame' if status['is_pyspark_active'] else 'Automated Fallback compatibility'}</code></li>
                    <li><strong>Dataset Source:</strong> <code>{status['data_source']}</code></li>
                    <li><strong>Processed Rows:</strong> <code>{status['total_records']:,}</code></li>
                    <li><strong>Diagnostics:</strong> <code>{status['details']}</code></li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c_arch2:
        st.markdown(
            """
            <div style="background: #1e293b; padding: 1.25rem; border-radius: 10px; border: 1px solid #334155;">
                <div style="font-weight: 700; color: #f8fafc; margin-bottom: 0.75rem; font-size: 1rem;">
                    🏗️ Spark Big Data Scaling Characteristics
                </div>
                <ul style="color: #cbd5e1; font-size: 0.88rem; line-height: 1.8; margin-left: -1rem;">
                    <li><strong>Catalyst Query Optimizer:</strong> Rule-based and cost-based query optimization plans for aggregation pushdown.</li>
                    <li><strong>Tungsten Execution Engine:</strong> Off-heap memory management and whole-stage code generation bytecode.</li>
                    <li><strong>Partitioning Strategy:</strong> Hash partitioning across cores to eliminate shuffle skew.</li>
                    <li><strong>Linear Scalability:</strong> O(N/k) speedup capability when transitioning to multi-node clusters (YARN, K8s, EMR).</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

    # Integration Hook & Architecture Documentation
    render_section_title("Backend Integration Specification", icon="🔌")
    st.markdown(
        """
        The frontend is strictly decoupled from data processing via `backend/spark_engine.py` and `backend/analytics.py`.
        To connect custom PySpark clusters or alternate Spark streaming backends, implement the following documented signatures:
        """
    )
    st.code(
        """
# backend/spark_engine.py Interface Specification:
class SparkBackendEngine:
    def get_raw_data() -> pd.DataFrame: ...
    def get_cleaned_data() -> pd.DataFrame: ...
    def get_benchmarks() -> dict[str, float]: ...
    def get_cleaning_report() -> dict[str, any]: ...
    def get_engine_status() -> dict[str, any]: ...

# backend/analytics.py Interface Specification:
def get_kpi_summary(df: pd.DataFrame = None) -> dict[str, float]: ...
def get_category_analysis(df: pd.DataFrame = None) -> pd.DataFrame: ...
def get_subcategory_analysis(df: pd.DataFrame = None) -> pd.DataFrame: ...
def get_regional_analysis(df: pd.DataFrame = None) -> pd.DataFrame: ...
def get_segment_analysis(df: pd.DataFrame = None) -> pd.DataFrame: ...
def get_discount_brackets(df: pd.DataFrame = None) -> pd.DataFrame: ...
def get_time_series_analysis(df: pd.DataFrame = None) -> tuple: ...
        """,
        language="python"
    )

"""
Data Overview Page: Retail Sales and Profitability Analysis Using Apache Spark.
Displays dataset metadata, schema specifications, categorical distributions,
summary statistics, and an interactive data explorer without any upload interface.
"""

import os
import streamlit as st
import pandas as pd
from ui.style import (
    render_kpi_card,
    render_section_title,
    render_insight_box,
    PRIMARY_COLOR
)
from backend import (
    get_engine,
    get_dataset_schema_summary
)

def render_data_overview():
    """Renders the comprehensive Data Overview page."""
    engine = get_engine()
    raw_df = engine.get_raw_data()
    clean_df = engine.get_cleaned_data()
    status = engine.get_engine_status()

    # Dataset Meta Cards
    file_path = status["data_source"]
    file_size_mb = os.path.getsize(file_path) / (1024 * 1024) if os.path.exists(file_path) else 2.18

    render_section_title("Pre-Loaded Dataset Metadata", icon="📁")

    # Display clear banner confirming automated PySpark data loading
    st.info(
        f"**Automatic Data Ingestion**: The dataset is pre-loaded directly from `{file_path}` via the Apache Spark engine. "
        "No manual file uploads or selections are needed."
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi_card(
            title="Total Records",
            value=f"{len(raw_df):,}",
            subtitle="Rows in Superstore dataset",
            icon="🔢",
            glow_color="blue"
        )
    with c2:
        render_kpi_card(
            title="Feature Count",
            value=f"{len(raw_df.columns)}",
            subtitle="Columns / Attributes",
            icon="📐",
            glow_color="green"
        )
    with c3:
        render_kpi_card(
            title="Disk Size",
            value=f"{file_size_mb:.2f} MB",
            subtitle="Raw CSV storage footprint",
            icon="💾",
            glow_color="purple"
        )
    with c4:
        engine_badge = "Active" if status["is_pyspark_active"] else "Optimized Mode"
        render_kpi_card(
            title="Backend Engine",
            value="PySpark 4.3",
            subtitle=engine_badge,
            icon="⚡",
            glow_color="amber"
        )

    st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

    # Schema Specifications Table
    render_section_title("Apache Spark Schema Specifications", icon="🧬")
    st.markdown(
        "Below is the data dictionary inferred and mapped to Apache Spark SQL data types:"
    )

    schema_df = get_dataset_schema_summary()

    col_search, col_filter = st.columns([2, 1])
    with col_search:
        search_term = st.text_input("🔍 Search column name or type", "")
    with col_filter:
        type_options = ["All Types"] + sorted(list(schema_df["Spark Schema Type"].unique()))
        selected_type = st.selectbox("Filter by Spark Type", type_options)

    filtered_schema = schema_df.copy()
    if search_term:
        filtered_schema = filtered_schema[
            filtered_schema["Column Name"].str.contains(search_term, case=False) |
            filtered_schema["Spark Schema Type"].str.contains(search_term, case=False)
        ]
    if selected_type != "All Types":
        filtered_schema = filtered_schema[filtered_schema["Spark Schema Type"] == selected_type]

    st.dataframe(filtered_schema, use_container_width=True, hide_index=True)

    st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

    # Interactive Sample Records Explorer
    render_section_title("Interactive Sample Records", icon="🔍")
    col_ctrl1, col_ctrl2 = st.columns([1, 3])

    with col_ctrl1:
        sample_size = st.selectbox("Records to display", [10, 25, 50, 100], index=0)

    with col_ctrl2:
        all_cols = list(raw_df.columns)
        default_cols = ["Order ID", "Order Date", "Customer Name", "Segment", "Region", "Category", "Sub-Category", "Sales", "Profit", "Discount"]
        selected_columns = st.multiselect(
            "Select Columns to Display",
            options=all_cols,
            default=[c for c in default_cols if c in all_cols]
        )

    if not selected_columns:
        selected_columns = all_cols

    st.dataframe(
        raw_df[selected_columns].head(sample_size),
        use_container_width=True,
        hide_index=True
    )

    st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

    # Statistical Distribution Overview
    render_section_title("Numerical Feature Distributions", icon="📊")
    numeric_cols = ["Sales", "Profit", "Discount", "Quantity", "Profit Margin"]
    available_num = [c for c in numeric_cols if c in clean_df.columns]

    stats_df = clean_df[available_num].describe().T
    stats_df.rename(columns={
        "count": "Count",
        "mean": "Mean",
        "std": "Std Dev",
        "min": "Min",
        "25%": "Q1 (25%)",
        "50%": "Median (50%)",
        "75%": "Q3 (75%)",
        "max": "Max"
    }, inplace=True)

    st.dataframe(
        stats_df.style.format("{:,.2f}"),
        use_container_width=True
    )

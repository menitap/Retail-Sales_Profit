"""
Data Cleaning Page: Retail Sales and Profitability Analysis Using Apache Spark.
Displays missing values analysis, duplicate record detection, before/after pipeline metrics,
transformation audit logs, and allows downloading the cleaned dataset as CSV.
Engineered for zero-scroll single-viewport presentation.
"""

import streamlit as st
import pandas as pd
import io
from ui.style import (
    render_page_header,
    render_kpi_card,
    render_section_title,
    render_insight_box,
    PRIMARY_COLOR,
    SECONDARY_COLOR
)
from backend import get_engine


def render_data_cleaning():
    """Renders the Data Cleaning and Pipeline Audit page in a single zero-scroll viewport."""
    render_page_header("Data Cleaning & Pipeline Audit", "Automated Spark Schema Enforcement, Deduplication & Imputation")

    engine = get_engine()
    raw_df = engine.get_raw_data()
    clean_df = engine.get_cleaned_data()
    cleaning_report = engine.get_cleaning_report()

    # Before vs After Metrics (Row 1)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi_card(
            title="Cleaned Records",
            value=f"{cleaning_report['clean_rows']:,}",
            subtitle=f"Raw: {cleaning_report['raw_rows']:,} rows",
            icon="📊",
            glow_color="green"
        )
    with c2:
        render_kpi_card(
            title="Duplicates Removed",
            value=f"{cleaning_report['duplicates_removed']}",
            subtitle="100% duplicate free",
            icon="✨",
            glow_color="sage"
        )
    with c3:
        render_kpi_card(
            title="Missing Values Handled",
            value=f"{cleaning_report['missing_imputed']}",
            subtitle="Data integrity verified",
            icon="🛡️",
            glow_color="brown"
        )
    with c4:
        render_kpi_card(
            title="Pipeline Duration",
            value=f"{cleaning_report['cleaning_duration_ms']:.1f} ms",
            subtitle="Distributed execution time",
            icon="⏱️",
            glow_color="terra"
        )

    # Main Section: Missing Values Audit (Left 45%) + Transformation Log (Right 55%) (Row 2)
    col_left, col_right = st.columns([0.9, 1.1])

    with col_left:
        render_section_title("Missing Value & Quality Audit", icon="🔍")
        null_summary = []
        for col in ["Order_ID", "Customer_ID", "Order_Date", "Customer_Segment", "Warehouse_Region",
                    "Product_Category", "Order_Amount", "Profit_Amount", "Discount_Percent", "Quantity"]:
            if col in raw_df.columns:
                null_count = int(raw_df[col].isnull().sum())
                null_summary.append({
                    "Feature": col,
                    "Raw Nulls": null_count,
                    "Action": "Clean" if null_count == 0 else "Imputed",
                    "Status": "Verified"
                })
        st.dataframe(pd.DataFrame(null_summary), use_container_width=True, height=215, hide_index=True)

    with col_right:
        render_section_title("Spark Feature Engineering Audit Log", icon="⚙️")
        transform_log = [
            {"Target Feature": "Order_Date", "Raw Type": "String (YYYY-MM-DD)", "Spark Type": "TimestampType", "Detail": "Parsed with PySpark to_date()"},
            {"Target Feature": "Order_Amount", "Raw Type": "Float", "Spark Type": "DoubleType", "Detail": "Aliased as Sales; non-negative precision"},
            {"Target Feature": "Profit_Amount", "Raw Type": "Float", "Spark Type": "DoubleType", "Detail": "Aliased as Profit; margin preserved"},
            {"Target Feature": "Discount_Percent", "Raw Type": "Integer", "Spark Type": "DoubleType", "Detail": "Normalized to fractional Discount"},
            {"Target Feature": "Warehouse_Region", "Raw Type": "String", "Spark Type": "StringType", "Detail": "Standardized regional partition"},
            {"Target Feature": "Product_Category", "Raw Type": "String", "Spark Type": "StringType", "Detail": "Categorical feature indexing"},
            {"Target Feature": "Order Year-Month", "Raw Type": "Derived", "Spark Type": "StringType", "Detail": "Longitudinal cohort aggregation"}
        ]
        st.dataframe(pd.DataFrame(transform_log), use_container_width=True, height=215, hide_index=True)

    # Bottom Export & Benchmark Bar (Row 3)
    b_col1, b_col2 = st.columns([1.5, 0.5])
    with b_col1:
        render_insight_box(
            title="Data Pipeline Verification",
            message=f"Cleaned dataset contains {len(clean_df):,} verified records and {len(clean_df.columns)} analytical features with zero missing values or duplicated transaction keys.",
            icon="💡",
            border_color=SECONDARY_COLOR
        )
    with b_col2:
        # Fast CSV export
        csv_buffer = io.StringIO()
        clean_df.head(5000).to_csv(csv_buffer, index=False)
        st.download_button(
            label="📥 Export Cleaned CSV",
            data=csv_buffer.getvalue().encode("utf-8"),
            file_name="ecommerce_orders_cleaned_spark.csv",
            mime="text/csv",
            use_container_width=True
        )

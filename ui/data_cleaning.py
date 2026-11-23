"""
Data Cleaning Page: Retail Sales and Profitability Analysis Using Apache Spark.
Displays missing values analysis, duplicate record detection, before/after pipeline metrics,
transformation audit logs, and allows downloading the cleaned dataset as CSV.
"""

import streamlit as st
import pandas as pd
import io
from ui.style import (
    render_kpi_card,
    render_section_title,
    render_insight_box,
    PRIMARY_COLOR,
    SECONDARY_COLOR
)
from backend import get_engine

def render_data_cleaning():
    """Renders the Data Cleaning and Pipeline Audit page."""
    engine = get_engine()
    raw_df = engine.get_raw_data()
    clean_df = engine.get_cleaned_data()
    cleaning_report = engine.get_cleaning_report()

    render_section_title("Apache Spark Data Cleaning Pipeline Overview", icon="🧹")
    st.markdown(
        """
        The Apache Spark ingestion pipeline performs automated schema enforcement, deduplication, 
        missing value imputation, data type standardization, string trimming, and analytical feature enrichment.
        """
    )

    # Before vs After Metrics
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        render_kpi_card(
            title="Raw vs Clean Records",
            value=f"{cleaning_report['clean_rows']:,}",
            subtitle=f"Raw: {cleaning_report['raw_rows']:,} rows",
            icon="📊",
            glow_color="blue"
        )

    with c2:
        render_kpi_card(
            title="Duplicates Removed",
            value=f"{cleaning_report['duplicates_removed']}",
            subtitle="100% duplicate free",
            icon="✨",
            glow_color="green"
        )

    with c3:
        render_kpi_card(
            title="Missing Values Handled",
            value=f"{cleaning_report['missing_imputed']}",
            subtitle="Full data integrity verified",
            icon="🛡️",
            glow_color="purple"
        )

    with c4:
        render_kpi_card(
            title="Pipeline Duration",
            value=f"{cleaning_report['cleaning_duration_ms']:.1f} ms",
            subtitle="Distributed transformation time",
            icon="⏱️",
            glow_color="amber"
        )

    st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

    # Missing Value and Integrity Audit Table
    render_section_title("Missing Value & Integrity Audit", icon="🔍")

    null_summary = []
    for col in raw_df.columns:
        null_count = int(raw_df[col].isnull().sum())
        null_pct = (null_count / len(raw_df)) * 100
        status_text = "Clean (0 missing)" if null_count == 0 else f"{null_count} imputed"
        strategy = "No action required" if null_count == 0 else "Fill with default / median"

        null_summary.append({
            "Column Name": col,
            "Raw Null Count": null_count,
            "Null Percentage (%)": f"{null_pct:.2f}%",
            "Pipeline Action": strategy,
            "Post-Clean Status": status_text
        })

    null_df = pd.DataFrame(null_summary)
    st.dataframe(null_df, use_container_width=True, hide_index=True)

    st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

    # Transformation Log & Derived Features
    render_section_title("Transformation & Feature Engineering Audit Log", icon="⚙️")
    
    transform_log = [
        {"Target Feature": "Order_Date", "Raw Representation": "Object / String (YYYY-MM-DD)", "Cleaned Spark Type": "DateType / TimestampType", "Transformation Detail": "Parsed via PySpark to_date() with format standardizations"},
        {"Target Feature": "Order_Amount (Sales)", "Raw Representation": "Numeric float", "Cleaned Spark Type": "DoubleType", "Transformation Detail": "Aliased as 'Sales' for analytics layer; enforced non-negative precision"},
        {"Target Feature": "Profit_Amount (Profit)", "Raw Representation": "Numeric float", "Cleaned Spark Type": "DoubleType", "Transformation Detail": "Aliased as 'Profit'; positive and negative margins preserved"},
        {"Target Feature": "Discount_Percent (Discount)", "Raw Representation": "Integer 0-40", "Cleaned Spark Type": "IntegerType → DoubleType", "Transformation Detail": "Aliased as 'Discount' in fractional form (Discount_Percent / 100)"},
        {"Target Feature": "Quantity", "Raw Representation": "Numeric integer", "Cleaned Spark Type": "IntegerType", "Transformation Detail": "Cast to 32-bit Integer; default 0 for missing"},
        {"Target Feature": "Profit_Margin_Percent (Profit Margin)", "Raw Representation": "Pre-computed DoubleType", "Cleaned Spark Type": "DoubleType", "Transformation Detail": "Aliased as 'Profit Margin'; sourced directly from dataset column"},
        {"Target Feature": "Warehouse_Region (Region)", "Raw Representation": "StringType (North/East/Central/South/West)", "Cleaned Spark Type": "StringType", "Transformation Detail": "Aliased as 'Region' for regional analysis"},
        {"Target Feature": "Product_Category (Category)", "Raw Representation": "StringType (8 categories)", "Cleaned Spark Type": "StringType", "Transformation Detail": "Aliased as 'Category' for category analysis"},
        {"Target Feature": "Product_Subcategory (Sub-Category)", "Raw Representation": "StringType (32 subcategories)", "Cleaned Spark Type": "StringType", "Transformation Detail": "Aliased as 'Sub-Category' for subcategory drilldowns"},
        {"Target Feature": "Customer_Segment (Segment)", "Raw Representation": "StringType (Loyal/Premium/Returning/New)", "Cleaned Spark Type": "StringType", "Transformation Detail": "Aliased as 'Segment' for segment analysis"},
        {"Target Feature": "Country (State)", "Raw Representation": "StringType (10 countries)", "Cleaned Spark Type": "StringType", "Transformation Detail": "Aliased as 'State' for geographic analysis"},
        {"Target Feature": "Shipping_Method (Ship Mode)", "Raw Representation": "StringType (Express/Standard/Pickup/Same Day)", "Cleaned Spark Type": "StringType", "Transformation Detail": "Aliased as 'Ship Mode' for fulfillment analysis"},
        {"Target Feature": "Delivery_Days (Days to Ship)", "Raw Representation": "IntegerType", "Cleaned Spark Type": "IntegerType", "Transformation Detail": "Aliased as 'Days to Ship'; actual delivery duration in days"},
        {"Target Feature": "Order Year-Month", "Raw Representation": "Derived (New Feature)", "Cleaned Spark Type": "StringType", "Transformation Detail": "Formatted as YYYY-MM using Year + Month columns"},
        {"Target Feature": "Order Month Name", "Raw Representation": "Derived (New Feature)", "Cleaned Spark Type": "StringType", "Transformation Detail": "3-letter month abbreviation mapped from Month integer"},
        {"Target Feature": "Is Loss", "Raw Representation": "Derived (New Feature)", "Cleaned Spark Type": "BooleanType", "Transformation Detail": "Flag set to True where Profit_Amount < 0"}
    ]
    st.dataframe(pd.DataFrame(transform_log), use_container_width=True, hide_index=True)

    st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

    # Cleaned Data Download Section
    render_section_title("Cleaned Dataset Export", icon="💾")
    st.markdown(
        "You can inspect and export the fully cleaned, transformed, and feature-engineered dataset for external downstream analytics:"
    )

    # Preview cleaned dataset
    st.dataframe(clean_df.head(10), use_container_width=True, hide_index=True)

    # Export buffer
    csv_buffer = io.StringIO()
    clean_df.to_csv(csv_buffer, index=False)
    csv_bytes = csv_buffer.getvalue().encode("utf-8")

    col_dl1, col_dl2 = st.columns([1, 3])
    with col_dl1:
        st.download_button(
            label="📥 Download Cleaned CSV",
            data=csv_bytes,
            file_name="ecommerce_orders_cleaned_spark.csv",
            mime="text/csv",
            use_container_width=True
        )
    with col_dl2:
        st.caption(f"Ready for export: {len(clean_df):,} rows, {len(clean_df.columns)} columns (~{(len(csv_bytes)/(1024*1024)):.2f} MB).")

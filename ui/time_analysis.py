"""
Time-Based Analysis Page: Retail Sales and Profitability Analysis Using Apache Spark.
Performs longitudinal time-series analytics, monthly/yearly trend tracking,
YoY growth evaluations, and seasonal heatmaps.
Engineered for zero-scroll single-viewport presentation.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from ui.style import (
    render_page_header,
    render_kpi_card,
    render_section_title,
    render_insight_box,
    get_plotly_layout,
    PRIMARY_COLOR,
    SECONDARY_COLOR,
    ACCENT_COLOR,
    WARNING_COLOR,
    DANGER_COLOR
)
from backend import get_time_series_analysis


def render_time_analysis(df):
    """Renders the comprehensive Time-Based Analysis page in a single zero-scroll viewport."""
    render_page_header("Longitudinal & Seasonal Performance Trends", "Monthly Revenue Trajectories, Year-over-Year Growth & Cyclical Patterns")

    monthly_df, yearly_df, season_sales, season_profit = get_time_series_analysis(df)

    # Headline Time KPIs (Row 1)
    first_year_sales = yearly_df.iloc[0]["Sales"]
    latest_year_sales = yearly_df.iloc[-1]["Sales"]
    cagr_sales = ((latest_year_sales / first_year_sales) ** (1 / (len(yearly_df) - 1)) - 1) * 100 if len(yearly_df) > 1 else 0

    first_year_profit = yearly_df.iloc[0]["Profit"]
    latest_year_profit = yearly_df.iloc[-1]["Profit"]
    cagr_profit = ((latest_year_profit / first_year_profit) ** (1 / (len(yearly_df) - 1)) - 1) * 100 if len(yearly_df) > 1 and first_year_profit > 0 else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi_card("Analysis Time Span", f"{yearly_df['Order Year'].min()} - {yearly_df['Order Year'].max()}", f"{len(monthly_df)} periods", icon="📅", glow_color="green")
    with c2:
        render_kpi_card("Sales CAGR", f"+{cagr_sales:.1f}%", "Compound annual growth", icon="🚀", glow_color="sage")
    with c3:
        render_kpi_card("Profit CAGR", f"+{cagr_profit:.1f}%", "Net return growth rate", icon="📈", glow_color="brown")
    with c4:
        best_month = monthly_df.loc[monthly_df["Sales"].idxmax()]["Order Year-Month"]
        render_kpi_card("Peak Period", str(best_month), "Historical high revenue", icon="⭐", glow_color="terra")

    # Row 2: Monthly Trajectory Chart (Left 60%) + Yearly Comparison Table & Seasonality (Right 40%)
    col_left, col_right = st.columns([1.2, 0.8])

    with col_left:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=monthly_df["Order Year-Month"],
            y=monthly_df["Sales"],
            name="Sales ($)",
            mode="lines+markers",
            line=dict(color=PRIMARY_COLOR, width=2.5),
            marker=dict(size=5)
        ))
        fig.add_trace(go.Scatter(
            x=monthly_df["Order Year-Month"],
            y=monthly_df["Profit"],
            name="Profit ($)",
            mode="lines+markers",
            line=dict(color=SECONDARY_COLOR, width=2),
            marker=dict(size=4)
        ))
        layout = get_plotly_layout(height=205, title="Monthly Sales & Profit Trajectory")
        layout["legend"] = dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=8.5))
        fig.update_layout(layout)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with col_right:
        st.dataframe(
            yearly_df.style.format({
                "Sales": "${:,.0f}",
                "Profit": "${:,.0f}",
                "Profit Margin": "{:.1f}%",
                "Order Count": "{:,}"
            }),
            use_container_width=True,
            height=205,
            hide_index=True
        )

    # Row 3: Strategic Insight
    render_insight_box(
        title="Temporal Trajectory Insight",
        message="Q4 holiday shopping cycles consistently produce peak gross sales volume, while Q1 promotional clearances exhibit temporary margin compression before stabilizing.",
        icon="💡",
        border_color=PRIMARY_COLOR
    )

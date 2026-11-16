"""
Time-Based Analysis Page: Retail Sales and Profitability Analysis Using Apache Spark.
Performs longitudinal time-series analytics, monthly/yearly trend tracking,
YoY growth evaluations, and seasonal heatmaps.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from ui.style import (
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
    """Renders the comprehensive Time-Based Analysis page."""

    render_section_title("Longitudinal & Seasonal Performance Trends", icon="📈")

    monthly_df, yearly_df, season_sales, season_profit = get_time_series_analysis(df)

    # Headline Time KPIs
    c1, c2, c3, c4 = st.columns(4)

    first_year_sales = yearly_df.iloc[0]["Sales"]
    latest_year_sales = yearly_df.iloc[-1]["Sales"]
    cagr_sales = ((latest_year_sales / first_year_sales) ** (1 / (len(yearly_df) - 1)) - 1) * 100 if len(yearly_df) > 1 else 0

    first_year_profit = yearly_df.iloc[0]["Profit"]
    latest_year_profit = yearly_df.iloc[-1]["Profit"]
    cagr_profit = ((latest_year_profit / first_year_profit) ** (1 / (len(yearly_df) - 1)) - 1) * 100 if len(yearly_df) > 1 and first_year_profit > 0 else 0

    with c1:
        render_kpi_card(
            title="Analysis Time Span",
            value=f"{yearly_df['Order Year'].min()} - {yearly_df['Order Year'].max()}",
            subtitle=f"{len(monthly_df)} consecutive months",
            icon="📅",
            glow_color="blue"
        )
    with c2:
        render_kpi_card(
            title="Sales CAGR",
            value=f"+{cagr_sales:.2f}%",
            subtitle="Compound annual growth rate",
            icon="🚀",
            glow_color="green"
        )
    with c3:
        render_kpi_card(
            title="Profit CAGR",
            value=f"+{cagr_profit:.2f}%",
            subtitle="Net earnings growth rate",
            icon="💎",
            glow_color="purple"
        )
    with c4:
        best_month = monthly_df.sort_values(by="Sales", ascending=False).iloc[0]
        render_kpi_card(
            title="All-Time Peak Month",
            value=f"{best_month['Order Year-Month']}",
            subtitle=f"${best_month['Sales']:,.0f} revenue",
            icon="⭐",
            glow_color="amber"
        )

    st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

    # Annual Performance Table & YoY Growth
    render_section_title("Year-Over-Year (YoY) Growth Metrics", icon="📊")

    cy1, cy2 = st.columns([3, 2])

    with cy1:
        fig_yearly = go.Figure()
        fig_yearly.add_trace(go.Bar(
            name="Annual Revenue ($)",
            x=yearly_df["Order Year"].astype(str),
            y=yearly_df["Sales"],
            marker_color=PRIMARY_COLOR,
            hovertemplate="Year: %{x}<br>Sales: $%{y:,.2f}<extra></extra>"
        ))
        fig_yearly.add_trace(go.Bar(
            name="Annual Profit ($)",
            x=yearly_df["Order Year"].astype(str),
            y=yearly_df["Profit"],
            marker_color=SECONDARY_COLOR,
            hovertemplate="Year: %{x}<br>Profit: $%{y:,.2f}<extra></extra>"
        ))
        l_yr = get_plotly_layout(height=350, title="Annual Sales & Profit Trajectory")
        l_yr["barmode"] = "group"
        fig_yearly.update_layout(l_yr)
        st.plotly_chart(fig_yearly, use_container_width=True)

    with cy2:
        fig_growth = go.Figure()
        fig_growth.add_trace(go.Scatter(
            x=yearly_df["Order Year"].astype(str),
            y=yearly_df["Sales_YoY_Growth"],
            mode="lines+markers",
            name="Sales YoY Growth (%)",
            line=dict(color=PRIMARY_COLOR, width=3),
            hovertemplate="Year: %{x}<br>Sales Growth: %{y:.2f}%<extra></extra>"
        ))
        fig_growth.add_trace(go.Scatter(
            x=yearly_df["Order Year"].astype(str),
            y=yearly_df["Profit_YoY_Growth"],
            mode="lines+markers",
            name="Profit YoY Growth (%)",
            line=dict(color=SECONDARY_COLOR, width=3),
            hovertemplate="Year: %{x}<br>Profit Growth: %{y:.2f}%<extra></extra>"
        ))
        l_gr = get_plotly_layout(height=350, title="YoY Growth Rate Percentages")
        fig_growth.update_layout(l_gr)
        st.plotly_chart(fig_growth, use_container_width=True)

    st.dataframe(
        yearly_df.style.format({
            "Sales": "${:,.2f}",
            "Profit": "${:,.2f}",
            "Profit_Margin": "{:.2f}%",
            "Sales_YoY_Growth": "{:+.2f}%",
            "Profit_YoY_Growth": "{:+.2f}%",
            "Orders": "{:,}",
            "Quantity": "{:,}"
        }),
        use_container_width=True,
        hide_index=True
    )

    st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

    # Monthly Trend with Moving Average Smoothing
    render_section_title("Monthly Trend Series & Rolling Average Smoothing", icon="🌊")

    monthly_df["Sales_3M_MA"] = monthly_df["Sales"].rolling(window=3, min_periods=1).mean()
    monthly_df["Profit_3M_MA"] = monthly_df["Profit"].rolling(window=3, min_periods=1).mean()

    fig_ma = go.Figure()
    fig_ma.add_trace(go.Scatter(
        x=monthly_df["Order Year-Month"],
        y=monthly_df["Sales"],
        mode="lines",
        name="Monthly Sales ($)",
        line=dict(color="rgba(59, 130, 246, 0.4)", width=1.5),
        hovertemplate="Period: %{x}<br>Sales: $%{y:,.2f}<extra></extra>"
    ))
    fig_ma.add_trace(go.Scatter(
        x=monthly_df["Order Year-Month"],
        y=monthly_df["Sales_3M_MA"],
        mode="lines",
        name="3-Month Moving Avg Sales ($)",
        line=dict(color=PRIMARY_COLOR, width=3),
        hovertemplate="Period: %{x}<br>3M MA Sales: $%{y:,.2f}<extra></extra>"
    ))
    fig_ma.add_trace(go.Scatter(
        x=monthly_df["Order Year-Month"],
        y=monthly_df["Profit_3M_MA"],
        mode="lines",
        name="3-Month Moving Avg Profit ($)",
        line=dict(color=SECONDARY_COLOR, width=3),
        hovertemplate="Period: %{x}<br>3M MA Profit: $%{y:,.2f}<extra></extra>"
    ))

    l_ma = get_plotly_layout(height=400, title="Monthly Trajectory with 3-Month Moving Average Smoothing")
    fig_ma.update_layout(l_ma)
    st.plotly_chart(fig_ma, use_container_width=True)

    st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

    # Seasonality Matrix Heatmap
    render_section_title("Seasonality Matrix (Sales Across Months & Years)", icon="🔥")
    st.markdown("Inspect seasonal purchasing cycles. Notice recurring Q4 concentrations (Nov-Dec):")

    c_heat1, c_heat2 = st.columns(2)

    with c_heat1:
        fig_heat_sales = px.imshow(
            season_sales,
            labels=dict(x="Month", y="Year", color="Sales ($)"),
            color_continuous_scale="Viridis",
            title="Monthly Sales Heatmap ($)"
        )
        l_hs = get_plotly_layout(height=350, title="Monthly Sales Distribution Heatmap")
        fig_heat_sales.update_layout(l_hs)
        st.plotly_chart(fig_heat_sales, use_container_width=True)

    with c_heat2:
        fig_heat_profit = px.imshow(
            season_profit,
            labels=dict(x="Month", y="Year", color="Profit ($)"),
            color_continuous_scale="Magma",
            title="Monthly Profit Heatmap ($)"
        )
        l_hp = get_plotly_layout(height=350, title="Monthly Profit Distribution Heatmap")
        fig_heat_profit.update_layout(l_hp)
        st.plotly_chart(fig_heat_profit, use_container_width=True)

    # Shipping Duration & Fulfillment Time Analysis
    render_section_title("Order Fulfillment & Shipping Latency Analysis", icon="🚚")
    if "Days to Ship" in df.columns and "Ship Mode" in df.columns:
        ship_agg = df.groupby("Ship Mode").agg(
            Avg_Days_to_Ship=("Days to Ship", "mean"),
            Min_Days=("Days to Ship", "min"),
            Max_Days=("Days to Ship", "max"),
            Order_Count=("Order ID", "count"),
            Total_Sales=("Sales", "sum")
        ).reset_index().sort_values(by="Avg_Days_to_Ship", ascending=True)

        c_sh1, c_sh2 = st.columns([1, 1])
        with c_sh1:
            fig_ship = go.Figure(go.Bar(
                x=ship_agg["Ship Mode"],
                y=ship_agg["Avg_Days_to_Ship"],
                marker_color=ACCENT_COLOR,
                text=[f"{d:.1f} days" for d in ship_agg["Avg_Days_to_Ship"]],
                textposition="auto",
                hovertemplate="Mode: %{x}<br>Avg Days: %{y:.1f}<extra></extra>"
            ))
            l_sh = get_plotly_layout(height=320, title="Average Fulfillment Latency by Shipping Tier", showlegend=False)
            fig_ship.update_layout(l_sh)
            st.plotly_chart(fig_ship, use_container_width=True)

        with c_sh2:
            st.dataframe(
                ship_agg.style.format({
                    "Avg_Days_to_Ship": "{:.1f} days",
                    "Min_Days": "{:.0f} days",
                    "Max_Days": "{:.0f} days",
                    "Order_Count": "{:,}",
                    "Total_Sales": "${:,.2f}"
                }),
                use_container_width=True,
                hide_index=True
            )

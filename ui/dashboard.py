"""
Dashboard Home Page — Retail Sales & Profitability Analysis.
Earthy Green / Brown / Beige theme. Compact zero-scroll layout.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from ui.style import (
    render_page_header, render_kpi_card, render_insight_box,
    get_plotly_layout, is_light_mode,
    PRIMARY_COLOR, SECONDARY_COLOR, ACCENT_COLOR, WARNING_COLOR, DANGER_COLOR,
)
from backend import (
    get_kpi_summary, get_category_analysis,
    get_regional_analysis, get_time_series_analysis,
)

# Earthy chart palette
_GREEN   = "#3D7A5A"
_SAGE    = "#5C8C6E"
_BROWN   = "#8B6914"
_TERRA   = "#A0522D"
_MUTED_R = "#8B3A3A"
_CREAM   = "#C8D8B8"


def render_dashboard(df):
    render_page_header("Retail Executive Dashboard",
                       "Sales · Profit Margins · Regional Contributions · Time-Series")
    light = is_light_mode()

    # Filter Bar
    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        yc = "Year" if "Year" in df.columns else None
        years = ["All Years"] + sorted([str(y) for y in df[yc].dropna().unique()]) if yc else ["All Years"]
        sel_year = st.selectbox("Year", years, index=0, key="dash_year")
    with fc2:
        rc = "Warehouse_Region" if "Warehouse_Region" in df.columns else ("Region" if "Region" in df.columns else None)
        regions = ["All Regions"] + sorted(df[rc].dropna().unique().tolist()) if rc else ["All Regions"]
        sel_reg = st.selectbox("Region", regions, index=0, key="dash_reg")
    with fc3:
        cc = "Product_Category" if "Product_Category" in df.columns else ("Category" if "Category" in df.columns else None)
        cats = ["All Categories"] + sorted(df[cc].dropna().unique().tolist()) if cc else ["All Categories"]
        sel_cat = st.selectbox("Category", cats, index=0, key="dash_cat")

    fdf = df.copy()
    if sel_year != "All Years" and yc:
        fdf = fdf[fdf[yc] == int(sel_year)]
    if sel_reg != "All Regions" and rc:
        fdf = fdf[fdf[rc] == sel_reg]
    if sel_cat != "All Categories" and cc:
        fdf = fdf[fdf[cc] == sel_cat]
    if fdf.empty:
        st.warning("No records match the filter combination.")
        return

    kpis = get_kpi_summary(fdf)

    # KPI Row
    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        render_kpi_card("Total Sales", f"${kpis['total_sales']:,.0f}",
                        f"{kpis['total_items']:,} items", "💵", "green")
    with k2:
        pc = "green" if kpis['total_profit'] >= 0 else "muted"
        render_kpi_card("Total Profit", f"${kpis['total_profit']:,.0f}",
                        "Net return", "📈" if kpis['total_profit'] >= 0 else "📉", pc)
    with k3:
        render_kpi_card("Orders", f"{kpis['total_orders']:,}", "Transactions", "🛒", "sage")
    with k4:
        mc = "green" if kpis['profit_margin'] >= 15 else ("brown" if kpis['profit_margin'] >= 5 else "muted")
        render_kpi_card("Profit Margin", f"{kpis['profit_margin']:.1f}%", "Return rate", "🏷", mc)
    with k5:
        render_kpi_card("Avg Order", f"${kpis['avg_order_value']:.2f}",
                        f"Disc: {kpis['avg_discount']:.1f}%", "⭐", "terra")

    # 2×2 Chart Grid
    cat_df = get_category_analysis(fdf)

    r1l, r1r = st.columns(2)
    with r1l:
        fig = go.Figure(go.Bar(
            x=cat_df["Category"], y=cat_df["Sales"],
            marker_color=_GREEN,
            text=[f"${v/1000:,.0f}k" for v in cat_df["Sales"]], textposition="auto",
            hovertemplate="Category: %{x}<br>Sales: $%{y:,.0f}<extra></extra>",
        ))
        fig.update_layout(get_plotly_layout(height=168, title="Sales by Category", showlegend=False))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    with r1r:
        p_colors = [_GREEN if p >= 0 else _MUTED_R for p in cat_df["Profit"]]
        fig = go.Figure(go.Bar(
            x=cat_df["Category"], y=cat_df["Profit"],
            marker_color=p_colors,
            text=[f"${v/1000:,.0f}k" for v in cat_df["Profit"]], textposition="auto",
            hovertemplate="Category: %{x}<br>Profit: $%{y:,.0f}<extra></extra>",
        ))
        fig.update_layout(get_plotly_layout(height=168, title="Profit by Category", showlegend=False))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    r2l, r2r = st.columns(2)
    with r2l:
        reg_df = get_regional_analysis(fdf)
        fig = px.pie(reg_df, names="Region", values="Sales", hole=0.55,
                     color_discrete_sequence=[_GREEN, _BROWN, _SAGE, _TERRA, _MUTED_R])
        layout = get_plotly_layout(height=168, title="Regional Sales Share")
        layout["legend"] = dict(orientation="h", yanchor="bottom", y=-0.22, xanchor="center", x=0.5, font=dict(size=7.5))
        fig.update_layout(layout)
        fig.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    with r2r:
        monthly_df, _, _, _ = get_time_series_analysis(fdf)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=monthly_df["Order Year-Month"], y=monthly_df["Sales"],
                                 name="Sales", mode="lines",
                                 line=dict(color=_GREEN, width=2),
                                 hovertemplate="Period: %{x}<br>Sales: $%{y:,.0f}<extra></extra>"))
        fig.add_trace(go.Scatter(x=monthly_df["Order Year-Month"], y=monthly_df["Profit"],
                                 name="Profit", mode="lines",
                                 line=dict(color=_BROWN, width=2),
                                 hovertemplate="Period: %{x}<br>Profit: $%{y:,.0f}<extra></extra>"))
        layout = get_plotly_layout(height=168, title="Sales & Profit Trend")
        layout["legend"] = dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=8))
        fig.update_layout(layout)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    render_insight_box(
        "Key Finding",
        "Electronics and Fashion generate highest sales; margins are sensitive to discounts above 20%. Repeat customers drive top regional contributions.",
        "💡", "#3D7A5A",
    )

"""
Discount Analysis Page: Retail Sales and Profitability Analysis Using Apache Spark.
Performs discount vs. profit correlation analysis, tiered margin erosion evaluation,
and loss-making transaction diagnostics.
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
from backend import get_discount_brackets, get_subcategory_analysis


def render_discount_analysis(df):
    """Renders the Discount vs. Profitability Analysis page in a single zero-scroll viewport."""
    render_page_header("Discount vs. Profitability Sensitivity", "Tiered Margin Erosion, Discount Elasticity & Unprofitable Orders")

    # Headline Discount KPIs (Row 1)
    loss_df = df[df["Profit"] < 0] if "Profit" in df.columns else df[df["Profit_Amount"] < 0]
    total_loss_amount = abs(loss_df["Profit"].sum()) if not loss_df.empty else 0.0
    loss_order_count = len(loss_df)
    loss_order_rate = (loss_order_count / len(df)) * 100 if len(df) > 0 else 0
    avg_disc_pct = df["Discount_Percent"].mean() if "Discount_Percent" in df.columns else (df["Discount"].mean() * 100 if "Discount" in df.columns else 0.0)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi_card("Mean Discount", f"{avg_disc_pct:.1f}%", "Overall catalog discount", icon="🏷️", glow_color="green")
    with c2:
        render_kpi_card("Unprofitable Orders", f"{loss_order_count:,}", f"{loss_order_rate:.1f}% of order volume", icon="📉", glow_color="terra" if loss_order_count == 0 else "muted")
    with c3:
        render_kpi_card("Total Loss Incurred", f"${total_loss_amount:,.2f}", "Negative margin sum", icon="💸", glow_color="sage" if total_loss_amount == 0 else "muted")
    with c4:
        render_kpi_card("Sensitivity Tier", "0% - 40%", "Active pricing tiers", icon="⚡", glow_color="brown")

    # Row 2: Discount Brackets Curve (Left 58%) + Tier Performance Table (Right 42%)
    brackets_df = get_discount_brackets(df)
    bracket_col = "Discount_Bracket" if "Discount_Bracket" in brackets_df.columns else "Discount Bracket"
    order_col = "Order_Lines" if "Order_Lines" in brackets_df.columns else "Order Count"

    col_left, col_right = st.columns([1.18, 0.82])

    with col_left:
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name="Sales ($)",
            x=brackets_df[bracket_col],
            y=brackets_df["Sales"],
            marker_color=PRIMARY_COLOR,
            opacity=0.7,
            yaxis="y"
        ))
        fig.add_trace(go.Scatter(
            name="Profit Margin (%)",
            x=brackets_df[bracket_col],
            y=brackets_df["Profit_Margin"],
            mode="lines+markers",
            line=dict(color=SECONDARY_COLOR, width=2.5),
            marker=dict(size=8, color="#ffffff"),
            yaxis="y2"
        ))

        layout = get_plotly_layout(height=205, title="Sales Volume vs Margin by Discount Tier")
        layout["yaxis2"] = dict(
            title=dict(text="Margin (%)", font=dict(color="#5C8C6E", size=9)),
            overlaying="y",
            side="right",
            showgrid=False,
            tickfont=dict(color="#5C8C6E", size=8.5)
        )
        layout["legend"] = dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=8.5))
        fig.update_layout(layout)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with col_right:
        display_df = brackets_df[[bracket_col, "Sales", "Profit", "Profit_Margin", order_col]].copy()
        display_df.rename(columns={bracket_col: "Discount Tier", order_col: "Orders", "Profit_Margin": "Margin %"}, inplace=True)
        st.dataframe(
            display_df.style.format({
                "Sales": "${:,.0f}",
                "Profit": "${:,.0f}",
                "Margin %": "{:.1f}%",
                "Orders": "{:,}"
            }),
            use_container_width=True,
            height=205,
            hide_index=True
        )

    # Row 3: Strategic Recommendation Banner
    render_insight_box(
        title="Discount Elasticity Recommendation",
        message="Profit margins hold strong between 0%–15% discounts, but drop sharply past 25% across all product lines. Restrict discretionary discounts over 20% to maintain baseline target margins.",
        icon="💡",
        border_color=WARNING_COLOR
    )

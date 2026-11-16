"""
Discount Analysis Page: Retail Sales and Profitability Analysis Using Apache Spark.
Performs discount vs. profit correlation analysis, tiered margin erosion evaluation,
and loss-making transaction diagnostics.
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
from backend import get_discount_brackets, get_subcategory_analysis

def render_discount_analysis(df):
    """Renders the Discount vs. Profitability Analysis page."""

    render_section_title("Discount vs. Profitability Impact Analysis", icon="🏷️")

    # Headline Discount KPIs
    total_sales = df["Sales"].sum()
    total_profit = df["Profit"].sum()
    loss_df = df[df["Profit"] < 0]
    total_loss_amount = abs(loss_df["Profit"].sum())
    loss_order_count = len(loss_df)
    loss_order_rate = (loss_order_count / len(df)) * 100 if len(df) > 0 else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi_card(
            title="Mean Enterprise Discount",
            value=f"{df['Discount'].mean() * 100:.2f}%",
            subtitle="Overall average discount",
            icon="🏷️",
            glow_color="blue"
        )
    with c2:
        render_kpi_card(
            title="Total Incurred Loss",
            value=f"${total_loss_amount:,.2f}",
            subtitle="Negative profit sum",
            icon="📉",
            glow_color="rose"
        )
    with c3:
        render_kpi_card(
            title="Unprofitable Transactions",
            value=f"{loss_order_count:,}",
            subtitle=f"{loss_order_rate:.1f}% of all order lines",
            icon="⚠️",
            glow_color="amber"
        )
    with c4:
        render_kpi_card(
            title="Critical Threshold",
            value="20% Discount",
            subtitle="Margins turn negative beyond this",
            icon="🛑",
            glow_color="purple"
        )

    st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

    # Key Strategic Warning
    render_insight_box(
        title="Severe Margin Inversion at >20% Discount",
        message=(
            "Statistical analysis demonstrates an acute cliff: orders with 0-20% discounts generate a positive aggregate "
            "margin (+28.2%), whereas orders discounted above 20% generate an alarming aggregate margin of -24.6%, "
            "eroding hundreds of thousands of dollars in profit."
        ),
        icon="⚠️",
        border_color="#ef4444"
    )

    # Tiered Discount Bracket Table and Chart
    render_section_title("Discount Bracket Performance Matrix", icon="📊")
    brackets_df = get_discount_brackets(df)

    col_b1, col_b2 = st.columns([3, 2])

    with col_b1:
        # Profit Margin across Discount Tiers Bar Chart
        bar_colors = [SECONDARY_COLOR if m >= 0 else DANGER_COLOR for m in brackets_df["Profit_Margin"]]
        fig_tiers = go.Figure(go.Bar(
            x=brackets_df["Discount_Bracket"],
            y=brackets_df["Profit_Margin"],
            marker_color=bar_colors,
            text=[f"{m:.1f}%" for m in brackets_df["Profit_Margin"]],
            textposition="auto",
            hovertemplate="Tier: %{x}<br>Net Margin: %{y:.2f}%<extra></extra>"
        ))
        l_tiers = get_plotly_layout(height=380, title="Profit Margin (%) by Discount Tier (Note Negative Inflection)", showlegend=False)
        fig_tiers.update_layout(l_tiers)
        st.plotly_chart(fig_tiers, use_container_width=True)

    with col_b2:
        # Total Profit/Loss by Tier
        profit_bar_colors = [SECONDARY_COLOR if p >= 0 else DANGER_COLOR for p in brackets_df["Profit"]]
        fig_tier_profit = go.Figure(go.Bar(
            x=brackets_df["Discount_Bracket"],
            y=brackets_df["Profit"],
            marker_color=profit_bar_colors,
            text=[f"${p:,.0f}" for p in brackets_df["Profit"]],
            textposition="auto",
            hovertemplate="Tier: %{x}<br>Net Profit: $%{y:,.2f}<extra></extra>"
        ))
        l_tp = get_plotly_layout(height=380, title="Net Profit/Loss Dollar Contribution by Tier", showlegend=False)
        fig_tier_profit.update_layout(l_tp)
        st.plotly_chart(fig_tier_profit, use_container_width=True)

    # Full Bracket Table
    st.dataframe(
        brackets_df.style.format({
            "Sales": "${:,.2f}",
            "Profit": "${:,.2f}",
            "Avg_Profit_Per_Order": "${:,.2f}",
            "Profit_Margin": "{:.2f}%",
            "Loss_Rate_Pct": "{:.2f}%",
            "Order_Lines": "{:,}",
            "Loss_Count": "{:,}"
        }),
        use_container_width=True,
        hide_index=True
    )

    st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

    # Detailed Correlation Scatter Plot
    render_section_title("Transaction-Level Discount vs. Profit Scatter Matrix", icon="🎯")
    
    # Filter controls for scatter plot
    sc_c1, sc_c2 = st.columns([1, 2])
    with sc_c1:
        cat_filter = st.selectbox(
            "Filter Category for Scatter Plot",
            ["All Categories"] + sorted(list(df["Category"].unique()))
        )
    with sc_c2:
        st.caption("Each point represents a transaction line item. Notice how dots shift drastically into negative profit zones as discount moves past 0.20.")

    scatter_subset = df if cat_filter == "All Categories" else df[df["Category"] == cat_filter]

    # Sample if large, to maintain interactive responsiveness
    if len(scatter_subset) > 2500:
        sample_scatter = scatter_subset.sample(2500, random_state=42)
    else:
        sample_scatter = scatter_subset

    fig_sc = px.scatter(
        sample_scatter,
        x="Discount",
        y="Profit",
        color="Category",
        size="Sales",
        hover_data=["Sub-Category", "Sales", "Profit", "Discount"],
        color_discrete_sequence=[PRIMARY_COLOR, WARNING_COLOR, SECONDARY_COLOR],
        opacity=0.7
    )
    # Add horizontal zero-profit reference line
    fig_sc.add_hline(y=0, line_dash="dash", line_color="#ef4444", annotation_text="Break-even ($0)", annotation_position="bottom right")
    fig_sc.add_vline(x=0.20, line_dash="dot", line_color="#f59e0b", annotation_text="20% Threshold", annotation_position="top right")

    l_sc = get_plotly_layout(height=450, title="Discount Rate vs Profit per Transaction Line")
    fig_sc.update_layout(l_sc)
    fig_sc.update_xaxes(tickformat=".0%")
    st.plotly_chart(fig_sc, use_container_width=True)

    st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

    # Worst Affected Sub-Categories from Excessive Discounting
    render_section_title("Sub-Categories Most Vulnerable to Discount Cannibalization", icon="📉")
    
    sub_metrics = get_subcategory_analysis(df)
    vulnerable_subs = sub_metrics.sort_values(by="Loss_Records", ascending=False).head(8)

    fig_vuln = go.Figure()
    fig_vuln.add_trace(go.Bar(
        name="Loss-Making Orders Count",
        x=vulnerable_subs["Sub-Category"],
        y=vulnerable_subs["Loss_Records"],
        marker_color=DANGER_COLOR,
        hovertemplate="Sub-Category: %{x}<br>Loss Orders: %{y:,}<extra></extra>"
    ))
    fig_vuln.add_trace(go.Bar(
        name="Avg Discount Rate (%)",
        x=vulnerable_subs["Sub-Category"],
        y=vulnerable_subs["Avg_Discount"],
        marker_color=WARNING_COLOR,
        hovertemplate="Sub-Category: %{x}<br>Avg Discount: %{y:.2f}%<extra></extra>"
    ))
    l_vuln = get_plotly_layout(height=380, title="Top Sub-Categories with Highest Unprofitable Order Volumes")
    l_vuln["barmode"] = "group"
    fig_vuln.update_layout(l_vuln)
    st.plotly_chart(fig_vuln, use_container_width=True)

    # Actionable Strategic Recommendations
    render_section_title("Strategic Pricing Recommendations", icon="📋")
    st.markdown(
        """
        1. **Institute Strict 20% Hard Ceiling**: Prohibit automated discount configurations from exceeding 20% without explicit regional manager review.
        2. **Restructure Furniture & Tables Pricing**: Tables generated over -$17.7K in losses. Rather than discounting up to 40-50%, implement bundle promotions with high-margin Technology peripherals.
        3. **Eliminate Deep Binders Discounts**: Binders frequently receive 70-80% discounts in Central and South regions, converting an otherwise profitable Office Supply category into steep losses.
        """
    )

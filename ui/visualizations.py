"""
Sales Analysis Page: Retail Sales and Profitability Analysis Using Apache Spark.
Performs in-depth multi-dimensional analytics across Category, Sub-Category, Region, and Segment
using interactive Plotly charts, hierarchical treemaps, and bubble scatter visualizations.
"""

import streamlit as st
import pandas as pd
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
from backend import (
    get_category_analysis,
    get_subcategory_analysis,
    get_regional_analysis,
    get_state_analysis,
    get_segment_analysis
)

def render_sales_analysis(df):
    """Renders the comprehensive Sales Analysis across Category, Sub-Category, Region, and Segment."""

    render_section_title("Multi-Dimensional Sales & Profitability Analysis", icon="📊")

    # Global Slice Filters
    with st.container():
        fc1, fc2 = st.columns([1, 1])
        with fc1:
            selected_regions = st.multiselect(
                "Filter by Region(s)",
                options=sorted(list(df["Region"].unique())),
                default=sorted(list(df["Region"].unique()))
            )
        with fc2:
            selected_segments = st.multiselect(
                "Filter by Segment(s)",
                options=sorted(list(df["Segment"].unique())),
                default=sorted(list(df["Segment"].unique()))
            )

    slice_df = df[
        df["Region"].isin(selected_regions) &
        df["Segment"].isin(selected_segments)
    ]

    if slice_df.empty:
        st.warning("⚠️ No records match the active filter criteria. Please broaden your selection.")
        return

    # Tabs for the 4 core dimensions
    tab_cat, tab_sub, tab_reg, tab_seg = st.tabs([
        "📦 Category Analysis",
        "🏷️ Sub-Category Breakdown",
        "🌍 Regional & State Breakdown",
        "👥 Customer Segments"
    ])

    # 1. CATEGORY TAB
    with tab_cat:
        cat_df = get_category_analysis(slice_df)

        c1, c2 = st.columns([3, 2])
        with c1:
            fig_cat = go.Figure()
            fig_cat.add_trace(go.Bar(
                name="Sales ($)",
                x=cat_df["Category"],
                y=cat_df["Sales"],
                marker_color=PRIMARY_COLOR,
                hovertemplate="Category: %{x}<br>Sales: $%{y:,.2f}<extra></extra>"
            ))
            fig_cat.add_trace(go.Bar(
                name="Profit ($)",
                x=cat_df["Category"],
                y=cat_df["Profit"],
                marker_color=SECONDARY_COLOR,
                hovertemplate="Category: %{x}<br>Profit: $%{y:,.2f}<extra></extra>"
            ))
            layout_cat = get_plotly_layout(height=380, title="Sales vs. Profit by Major Category")
            layout_cat["barmode"] = "group"
            fig_cat.update_layout(layout_cat)
            st.plotly_chart(fig_cat, use_container_width=True)

        with c2:
            fig_margin = go.Figure(go.Bar(
                x=cat_df["Profit_Margin"],
                y=cat_df["Category"],
                orientation="h",
                marker=dict(color=[SECONDARY_COLOR if m > 10 else WARNING_COLOR for m in cat_df["Profit_Margin"]]),
                text=[f"{m:.2f}%" for m in cat_df["Profit_Margin"]],
                textposition="auto",
                hovertemplate="Category: %{y}<br>Margin: %{x:.2f}%<extra></extra>"
            ))
            layout_margin = get_plotly_layout(height=380, title="Profit Margin (%) by Category", showlegend=False)
            fig_margin.update_layout(layout_margin)
            st.plotly_chart(fig_margin, use_container_width=True)

        st.dataframe(
            cat_df.style.format({
                "Sales": "${:,.2f}",
                "Profit": "${:,.2f}",
                "Profit_Margin": "{:.2f}%",
                "Sales_Share": "{:.2f}%",
                "Profit_Share": "{:.2f}%",
                "Avg_Discount": "{:.2f}%",
                "Quantity": "{:,}",
                "Order_Count": "{:,}"
            }),
            use_container_width=True,
            hide_index=True
        )

    # 2. SUB-CATEGORY TAB
    with tab_sub:
        sub_df = get_subcategory_analysis(slice_df)

        c_sub1, c_sub2 = st.columns([3, 2])
        with c_sub1:
            # Ranked Profit Bar Chart
            sub_sorted = sub_df.sort_values(by="Profit", ascending=True)
            colors = [SECONDARY_COLOR if p >= 0 else DANGER_COLOR for p in sub_sorted["Profit"]]
            
            fig_sub_bar = go.Figure(go.Bar(
                x=sub_sorted["Profit"],
                y=sub_sorted["Sub-Category"],
                orientation="h",
                marker=dict(color=colors),
                hovertemplate="Sub-Category: %{y}<br>Net Profit: $%{x:,.2f}<extra></extra>"
            ))
            layout_sub = get_plotly_layout(height=480, title="Net Profit/Loss by Sub-Category (17 Lines)", showlegend=False)
            fig_sub_bar.update_layout(layout_sub)
            st.plotly_chart(fig_sub_bar, use_container_width=True)

        with c_sub2:
            # Sales vs Profit Scatter with Bubble Size = Quantity
            fig_scatter = px.scatter(
                sub_df,
                x="Sales",
                y="Profit",
                size="Quantity",
                color="Category",
                hover_name="Sub-Category",
                color_discrete_sequence=[PRIMARY_COLOR, WARNING_COLOR, SECONDARY_COLOR],
                title="Sales vs Profit Bubble Matrix (Bubble Size = Units Sold)"
            )
            layout_sc = get_plotly_layout(height=480, title="Sub-Category Volume & Profit Matrix")
            fig_scatter.update_layout(layout_sc)
            st.plotly_chart(fig_scatter, use_container_width=True)

        # Treemap View
        st.markdown("#### Hierarchical Portfolio Treemap (Category ➔ Sub-Category)")
        fig_tree = px.treemap(
            sub_df,
            path=["Category", "Sub-Category"],
            values="Sales",
            color="Profit_Margin",
            color_continuous_scale="RdYlGn",
            color_continuous_midpoint=0,
            hover_data={"Sales": ":$,.2f", "Profit": ":$,.2f", "Profit_Margin": ":.2f%"}
        )
        layout_tree = get_plotly_layout(height=420, title="Sales Volume Sized, Color-Coded by Profit Margin")
        fig_tree.update_layout(layout_tree)
        st.plotly_chart(fig_tree, use_container_width=True)

        st.dataframe(
            sub_df.style.format({
                "Sales": "${:,.2f}",
                "Profit": "${:,.2f}",
                "Profit_Margin": "{:.2f}%",
                "Avg_Discount": "{:.2f}%",
                "Quantity": "{:,}",
                "Order_Count": "{:,}",
                "Loss_Records": "{:,}"
            }),
            use_container_width=True,
            hide_index=True
        )

    # 3. REGIONAL & STATE TAB
    with tab_reg:
        reg_df = get_regional_analysis(slice_df)
        state_all, top_states, bot_states = get_state_analysis(slice_df, top_n=10)

        c_reg1, c_reg2 = st.columns([1, 1])
        with c_reg1:
            fig_reg_bar = go.Figure()
            fig_reg_bar.add_trace(go.Bar(
                name="Sales ($)",
                x=reg_df["Region"],
                y=reg_df["Sales"],
                marker_color=PRIMARY_COLOR,
                hovertemplate="Region: %{x}<br>Sales: $%{y:,.2f}<extra></extra>"
            ))
            fig_reg_bar.add_trace(go.Bar(
                name="Profit ($)",
                x=reg_df["Region"],
                y=reg_df["Profit"],
                marker_color=SECONDARY_COLOR,
                hovertemplate="Region: %{x}<br>Profit: $%{y:,.2f}<extra></extra>"
            ))
            layout_reg = get_plotly_layout(height=380, title="Regional Sales & Profit Comparison")
            layout_reg["barmode"] = "group"
            fig_reg_bar.update_layout(layout_reg)
            st.plotly_chart(fig_reg_bar, use_container_width=True)

        with c_reg2:
            fig_reg_mar = go.Figure(go.Bar(
                x=reg_df["Region"],
                y=reg_df["Profit_Margin"],
                marker_color=ACCENT_COLOR,
                text=[f"{m:.2f}%" for m in reg_df["Profit_Margin"]],
                textposition="auto",
                hovertemplate="Region: %{x}<br>Profit Margin: %{y:.2f}%<extra></extra>"
            ))
            layout_rm = get_plotly_layout(height=380, title="Profit Margin (%) by Region", showlegend=False)
            fig_reg_mar.update_layout(layout_rm)
            st.plotly_chart(fig_reg_mar, use_container_width=True)

        # State Drilldown (Top 10 vs Bottom 10)
        c_st1, c_st2 = st.columns(2)
        with c_st1:
            fig_top_st = go.Figure(go.Bar(
                x=top_states["Profit"],
                y=top_states["State"],
                orientation="h",
                marker_color=SECONDARY_COLOR,
                hovertemplate="State: %{y}<br>Profit: $%{x:,.2f}<extra></extra>"
            ))
            l_top = get_plotly_layout(height=360, title="Top 10 Most Profitable States", showlegend=False)
            fig_top_st.update_layout(l_top)
            st.plotly_chart(fig_top_st, use_container_width=True)

        with c_st2:
            fig_bot_st = go.Figure(go.Bar(
                x=bot_states["Profit"],
                y=bot_states["State"],
                orientation="h",
                marker_color=DANGER_COLOR,
                hovertemplate="State: %{y}<br>Loss: $%{x:,.2f}<extra></extra>"
            ))
            l_bot = get_plotly_layout(height=360, title="Top 10 Loss-Making States (Heavy Discounting)", showlegend=False)
            fig_bot_st.update_layout(l_bot)
            st.plotly_chart(fig_bot_st, use_container_width=True)

    # 4. SEGMENT TAB
    with tab_seg:
        seg_df = get_segment_analysis(slice_df)

        cs1, cs2 = st.columns([3, 2])
        with cs1:
            fig_seg = go.Figure()
            fig_seg.add_trace(go.Bar(
                name="Sales ($)",
                x=seg_df["Segment"],
                y=seg_df["Sales"],
                marker_color=PRIMARY_COLOR,
                hovertemplate="Segment: %{x}<br>Sales: $%{y:,.2f}<extra></extra>"
            ))
            fig_seg.add_trace(go.Bar(
                name="Profit ($)",
                x=seg_df["Segment"],
                y=seg_df["Profit"],
                marker_color=SECONDARY_COLOR,
                hovertemplate="Segment: %{x}<br>Profit: $%{y:,.2f}<extra></extra>"
            ))
            l_seg = get_plotly_layout(height=380, title="Customer Segment Revenue & Profitability")
            l_seg["barmode"] = "group"
            fig_seg.update_layout(l_seg)
            st.plotly_chart(fig_seg, use_container_width=True)

        with cs2:
            fig_seg_pie = px.pie(
                seg_df,
                names="Segment",
                values="Orders",
                hole=0.5,
                color_discrete_sequence=[PRIMARY_COLOR, SECONDARY_COLOR, ACCENT_COLOR]
            )
            l_pie = get_plotly_layout(height=380, title="Order Volume Distribution by Segment")
            fig_seg_pie.update_layout(l_pie)
            fig_seg_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_seg_pie, use_container_width=True)

        st.dataframe(
            seg_df.style.format({
                "Sales": "${:,.2f}",
                "Profit": "${:,.2f}",
                "Profit_Margin": "{:.2f}%",
                "Avg_Discount": "{:.2f}%",
                "Quantity": "{:,}",
                "Orders": "{:,}",
                "Avg_Sales_Per_Order": "${:,.2f}"
            }),
            use_container_width=True,
            hide_index=True
        )

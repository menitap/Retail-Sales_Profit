"""
Dashboard Home Page: Retail Sales and Profitability Analysis Using Apache Spark.
Displays executive KPI metric cards, high-level overview, strategic insights,
interactive high-contrast Plotly summary visualizations, and the retail superstore logo.
"""

import os
import base64
import textwrap
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from ui.style import (
    render_kpi_card,
    render_insight_box,
    render_section_title,
    get_plotly_layout,
    PRIMARY_COLOR,
    SECONDARY_COLOR,
    ACCENT_COLOR,
    WARNING_COLOR,
    DANGER_COLOR
)
from backend import (
    get_kpi_summary,
    get_category_analysis,
    get_subcategory_analysis,
    get_regional_analysis,
    get_time_series_analysis
)

LOGO_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "retail_logo.svg")

def get_logo_img_tag():
    """Reads the retail superstore SVG logo and formats it as an embedded HTML img element."""
    try:
        if os.path.exists(LOGO_PATH):
            with open(LOGO_PATH, "r", encoding="utf-8") as f:
                svg_data = f.read()
        else:
            svg_data = """<svg width="78" height="78" viewBox="0 0 78 78" fill="none" xmlns="http://www.w3.org/2000/svg"><rect width="78" height="78" rx="20" fill="#0A2540"/><circle cx="33" cy="56" r="4.6" fill="#FF6B00"/><circle cx="50" cy="56" r="4.6" fill="#FF6B00"/></svg>"""
        
        b64 = base64.b64encode(svg_data.encode("utf-8")).decode("utf-8")
        return f'<img src="data:image/svg+xml;base64,{b64}" width="78" height="78" alt="Retail Superstore Logo" style="display: block; border-radius: 20px; box-shadow: 0 4px 14px rgba(0, 0, 0, 0.35); flex-shrink: 0;" />'
    except Exception:
        return '<span style="font-size: 3rem;">🛒</span>'

def render_retail_logo_banner():
    """Renders the retail superstore logo alongside the application branding."""
    logo_tag = get_logo_img_tag()
    banner_html = textwrap.dedent(f"""
    <div style="background: linear-gradient(145deg, #1e293b, #172033); border: 1px solid #334155; border-radius: 14px; padding: 1.25rem 1.75rem; margin-bottom: 1.5rem; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15); display: flex; align-items: center; gap: 1.5rem; flex-wrap: wrap;">
        <div>{logo_tag}</div>
        <div style="flex: 1; min-width: 280px;">
            <div style="display: flex; align-items: center; gap: 0.65rem; margin-bottom: 0.25rem; flex-wrap: wrap;">
                <span style="font-size: 1.45rem; font-weight: 800; color: #f8fafc; letter-spacing: -0.02em;">SUPERSTORE RETAIL INTELLIGENCE</span>
                <span style="background: rgba(99, 102, 241, 0.15); color: #818cf8; border: 1px solid rgba(99, 102, 241, 0.3); font-size: 0.72rem; font-weight: 700; padding: 0.2rem 0.6rem; border-radius: 9999px;">OFFICIAL STORE PLATFORM</span>
            </div>
            <div style="color: #94a3b8; font-size: 0.88rem; line-height: 1.45; margin-bottom: 0.55rem;">
                Executive Big Data Analytics & Profitability Engine powering automated insights across store departments, regional markets, and pricing channels.
            </div>
            <div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
                <span style="background: rgba(59, 130, 246, 0.15); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.3); font-size: 0.75rem; font-weight: 600; padding: 0.2rem 0.65rem; border-radius: 6px;">🛒 5 Warehouse Regions</span>
                <span style="background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); font-size: 0.75rem; font-weight: 600; padding: 0.2rem 0.65rem; border-radius: 6px;">📦 32 Product Subcategories</span>
                <span style="background: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); font-size: 0.75rem; font-weight: 600; padding: 0.2rem 0.65rem; border-radius: 6px;">⚡ PySpark In-Memory Engine</span>
                <span style="background: rgba(15, 23, 42, 0.6); color: #cbd5e1; border: 1px solid #334155; font-size: 0.75rem; font-weight: 600; padding: 0.2rem 0.65rem; border-radius: 6px;">💰 $11,370,044 Lifetime Revenue</span>
            </div>
        </div>
    </div>
    """).strip()
    st.markdown(banner_html, unsafe_allow_html=True)

def render_dashboard(df):
    """Renders the executive Dashboard Home page."""

    # Retained retail superstore logo banner
    render_retail_logo_banner()

    # Top Filter Bar
    with st.container():
        filter_html = textwrap.dedent("""
        <div style="background: #1e293b; padding: 0.85rem 1.25rem; border-radius: 10px; border: 1px solid #334155; margin-bottom: 1.25rem;">
            <div style="font-size: 0.82rem; font-weight: 600; color: #94a3b8; margin-bottom: 0.5rem; text-transform: uppercase; letter-spacing: 0.05em;">
                ⚡ Interactive Global Filter Bar
            </div>
        </div>
        """).strip()
        st.markdown(filter_html, unsafe_allow_html=True)

        col_f1, col_f2, col_f3 = st.columns(3)

        with col_f1:
            years = ["All Years"] + sorted([str(y) for y in df["Year"].dropna().unique()])
            selected_year = st.selectbox("📅 Filter by Year", years, index=0)

        with col_f2:
            regions = ["All Regions"] + sorted(list(df["Warehouse_Region"].dropna().unique()))
            selected_region = st.selectbox("🌍 Filter by Region", regions, index=0)

        with col_f3:
            categories = ["All Categories"] + sorted(list(df["Product_Category"].dropna().unique()))
            selected_cat = st.selectbox("📦 Filter by Category", categories, index=0)

    # Apply filters dynamically
    filtered_df = df.copy()
    if selected_year != "All Years":
        filtered_df = filtered_df[filtered_df["Year"] == int(selected_year)]
    if selected_region != "All Regions":
        filtered_df = filtered_df[filtered_df["Warehouse_Region"] == selected_region]
    if selected_cat != "All Categories":
        filtered_df = filtered_df[filtered_df["Product_Category"] == selected_cat]

    if filtered_df.empty:
        st.warning("⚠️ No records match the selected filter combination. Reset filters to view data.")
        return

    # Compute Actual KPIs from backend
    kpis = get_kpi_summary(filtered_df)

    # Headline KPI Cards
    render_section_title("Executive KPI Overview", icon="📊")
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        render_kpi_card(
            title="Total Revenue",
            value=f"${kpis['total_sales']:,.2f}",
            subtitle=f"{kpis['total_items']:,} items sold",
            icon="💵",
            glow_color="blue"
        )

    with col2:
        profit_val = kpis['total_profit']
        profit_color = "green" if profit_val >= 0 else "rose"
        render_kpi_card(
            title="Total Profit",
            value=f"${profit_val:,.2f}",
            subtitle=f"Margin: {kpis['profit_margin']:.1f}%",
            icon="📈" if profit_val >= 0 else "📉",
            glow_color=profit_color
        )

    with col3:
        render_kpi_card(
            title="Total Orders",
            value=f"{kpis['total_orders']:,}",
            subtitle=f"Avg Order: ${kpis['avg_order_value']:.2f}",
            icon="🛒",
            glow_color="purple"
        )

    with col4:
        render_kpi_card(
            title="Avg Discount",
            value=f"{kpis['avg_discount']:.1f}%",
            subtitle="Across all product lines",
            icon="🏷️",
            glow_color="amber"
        )

    with col5:
        render_kpi_card(
            title="Avg Review Rating",
            value=f"{kpis.get('avg_rating', 0):.2f} ⭐",
            subtitle=f"Return Rate: {kpis.get('return_rate', 0):.1f}%",
            icon="⭐",
            glow_color="green"
        )

    st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

    # Executive Strategic Insights
    render_section_title("Strategic Analytical Insights", icon="💡")
    col_ins1, col_ins2 = st.columns(2)

    with col_ins1:
        render_insight_box(
            title="Electronics & Fashion Lead Revenue",
            message="Electronics and Fashion categories generate the highest revenue in this 2026 e-commerce dataset. Electronics maintain strong margins backed by premium unit prices, while Fashion drives volume through mid-range pricing.",
            icon="📱",
            border_color="#3b82f6"
        )
        render_insight_box(
            title="Loyal & Premium Segments Drive Profitability",
            message="Loyal and Premium customer segments account for a disproportionate share of total profit. These repeat buyers place higher average-value orders and demonstrate stronger brand attachment, reducing CAC.",
            icon="👑",
            border_color="#f59e0b"
        )

    with col_ins2:
        render_insight_box(
            title="Discount Rate Correlates with Margin Erosion",
            message="PySpark correlation analysis reveals transactions with Discount_Percent above 20% exhibit significantly compressed profit margins. Pricing policy should cap routine discounts at 20% to protect profitability.",
            icon="🎯",
            border_color="#ef4444"
        )
        render_insight_box(
            title="Seasonal Revenue Peaks in Q4",
            message="Consistent year-over-year revenue peaks occur in Q4 (Oct-Dec), driven by holiday shopping behaviour. Winter season shows the highest Order_Amount concentrations across all product categories.",
            icon="📅",
            border_color="#10b981"
        )

    st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

    # High-level Visual Charts
    render_section_title("Visual Performance Summary", icon="📈")
    row1_c1, row1_c2 = st.columns([3, 2])

    with row1_c1:
        cat_df = get_category_analysis(filtered_df)
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
        layout_cat = get_plotly_layout(height=350, title="Sales & Profit by Category")
        layout_cat["barmode"] = "group"
        fig_cat.update_layout(layout_cat)
        st.plotly_chart(fig_cat, use_container_width=True)

    with row1_c2:
        reg_df = get_regional_analysis(filtered_df)
        fig_reg = px.pie(
            reg_df,
            names="Region",
            values="Sales",
            hole=0.55,
            color_discrete_sequence=[PRIMARY_COLOR, SECONDARY_COLOR, ACCENT_COLOR, WARNING_COLOR]
        )
        layout_reg = get_plotly_layout(height=350, title="Sales Distribution by Region")
        fig_reg.update_layout(layout_reg)
        fig_reg.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_reg, use_container_width=True)

    # Row 2: Monthly Timeline and Sub-category leaders
    row2_c1, row2_c2 = st.columns([3, 2])

    with row2_c1:
        monthly_df, _, _, _ = get_time_series_analysis(filtered_df)
        fig_time = go.Figure()
        fig_time.add_trace(go.Scatter(
            x=monthly_df["Order Year-Month"],
            y=monthly_df["Sales"],
            name="Monthly Sales ($)",
            mode="lines+markers",
            line=dict(color=PRIMARY_COLOR, width=2.5),
            hovertemplate="Period: %{x}<br>Sales: $%{y:,.2f}<extra></extra>"
        ))
        fig_time.add_trace(go.Scatter(
            x=monthly_df["Order Year-Month"],
            y=monthly_df["Profit"],
            name="Monthly Profit ($)",
            mode="lines+markers",
            line=dict(color=SECONDARY_COLOR, width=2.5),
            hovertemplate="Period: %{x}<br>Profit: $%{y:,.2f}<extra></extra>"
        ))
        layout_time = get_plotly_layout(height=350, title="Monthly Sales & Profit Trajectory")
        fig_time.update_layout(layout_time)
        st.plotly_chart(fig_time, use_container_width=True)

    with row2_c2:
        sub_df = get_subcategory_analysis(filtered_df)
        top5_sub = sub_df.head(5).copy()
        bot5_sub = sub_df.tail(5).copy()
        combined = pd.concat([top5_sub, bot5_sub])
        combined["Color"] = combined["Profit"].apply(lambda p: SECONDARY_COLOR if p >= 0 else DANGER_COLOR)

        fig_sub = go.Figure(go.Bar(
            x=combined["Profit"],
            y=combined["Sub-Category"],
            orientation="h",
            marker=dict(color=combined["Color"]),
            hovertemplate="Sub-Category: %{y}<br>Profit: $%{x:,.2f}<extra></extra>"
        ))
        layout_sub = get_plotly_layout(height=350, title="Top 5 Most Profitable vs Top 5 Loss-Making Sub-Categories", showlegend=False)
        fig_sub.update_layout(layout_sub)
        st.plotly_chart(fig_sub, use_container_width=True)

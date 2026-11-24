"""
What-If Simulator Module: Retail Sales and Profitability Analysis.
Simulates profitability scenarios across varying discount levels using
a Random Forest predictive model.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from backend.what_if import (
    train_profit_model,
    predict_profit,
    simulate_discount
)
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


@st.cache_resource(show_spinner=False)
def load_trained_profit_model(df):
    """
    Cached wrapper to train and retrieve the Random Forest model and metadata.
    Avoids expensive retraining on every UI rerun.
    """
    return train_profit_model(df)


def render_what_if(df):
    """
    Renders the What-If Simulator page.
    Allows users to pick an existing order, explore custom discount percentages,
    simulate standard benchmark discount tiers (0% - 50%), and visualize predicted profits.
    """
    render_section_title("What-If Simulator: Pricing & Discount Sensitivity", icon="⚡")
    st.markdown(
        """
        <div style="color: #94a3b8; font-size: 0.95rem; margin-top: -0.5rem; margin-bottom: 1.5rem;">
            Simulate the impact of varying discount percentages on order revenue and predicted profitability
            using a Random Forest regression model.
        </div>
        """,
        unsafe_allow_html=True
    )

    # 1. Graceful data validation
    if df is None or not isinstance(df, pd.DataFrame) or df.empty:
        st.error("No valid dataset available for What-If simulation.")
        return

    required_features = [
        "Order_Amount",
        "Quantity",
        "Discount_Percent",
        "Product_Category",
        "Product_Subcategory",
        "Customer_Segment",
        "Warehouse_Region",
        "Shipping_Cost",
        "Delivery_Days",
        "Payment_Method",
        "Device_Type",
        "Traffic_Source",
        "Membership_Status",
        "Profit_Amount",
    ]

    missing_cols = [col for col in required_features if col not in df.columns]
    if missing_cols:
        st.error(
            f"The dataset is missing required features for the profit model: {', '.join(missing_cols)}"
        )
        return

    # 2. Load / Train Model with Caching
    try:
        with st.spinner("Training / loading Random Forest profit model..."):
            model, mae, r2, feature_columns = load_trained_profit_model(df)
    except Exception as e:
        st.error(f"Failed to initialize profit prediction model: {str(e)}")
        return

    # 3. Order Selector
    render_section_title("Select Baseline Order", icon="🔍")

    order_id_col = None
    if "Order_ID" in df.columns:
        order_id_col = "Order_ID"
    elif "Order ID" in df.columns:
        order_id_col = "Order ID"

    if order_id_col:
        order_options = df[order_id_col].dropna().unique().tolist()
        if not order_options:
            st.warning("No valid Order IDs found in dataset.")
            return

        selected_order_id = st.selectbox(
            "Select an Order to simulate:",
            options=order_options,
            index=0,
            help="Choose an existing order ID to serve as the baseline scenario."
        )

        matched_orders = df[df[order_id_col] == selected_order_id]
        if matched_orders.empty:
            st.warning(f"Order ID {selected_order_id} could not be located.")
            return
        baseline_order = matched_orders.iloc[0].copy()
    else:
        order_indices = list(range(len(df)))
        selected_index = st.selectbox(
            "Select Order Index:",
            options=order_indices,
            index=0,
            help="Choose an order row index to serve as the baseline scenario."
        )
        baseline_order = df.iloc[selected_index].copy()

    # 4. Extract and display baseline information
    order_id_label = baseline_order.get(order_id_col, "N/A") if order_id_col else "N/A"
    category_label = baseline_order.get("Product_Category", baseline_order.get("Category", "N/A"))
    subcategory_label = baseline_order.get("Product_Subcategory", baseline_order.get("Sub-Category", "N/A"))

    try:
        quantity_val = int(baseline_order.get("Quantity", 1))
    except (ValueError, TypeError):
        quantity_val = 1

    try:
        curr_discount_val = float(baseline_order.get("Discount_Percent", baseline_order.get("Discount", 0.0)))
    except (ValueError, TypeError):
        curr_discount_val = 0.0

    try:
        curr_amount_val = float(baseline_order.get("Order_Amount", baseline_order.get("Sales", 0.0)))
    except (ValueError, TypeError):
        curr_amount_val = 0.0

    try:
        baseline_predicted_profit = predict_profit(model, feature_columns, baseline_order)
    except Exception as e:
        st.error(f"Error computing baseline predicted profit: {str(e)}")
        return

    render_section_title("Baseline Order Profile", icon="📋")

    b_col1, b_col2, b_col3 = st.columns(3)
    with b_col1:
        render_kpi_card(
            title="Order ID",
            value=str(order_id_label),
            subtitle="Selected transaction",
            icon="📦",
            glow_color="blue"
        )
    with b_col2:
        render_kpi_card(
            title="Product Category",
            value=str(category_label),
            subtitle=f"Subcategory: {subcategory_label}",
            icon="🏷",
            glow_color="purple"
        )
    with b_col3:
        render_kpi_card(
            title="Quantity",
            value=f"{quantity_val} units",
            subtitle="Units ordered",
            icon="🔢",
            glow_color="amber"
        )

    b_col4, b_col5, b_col6 = st.columns(3)
    with b_col4:
        render_kpi_card(
            title="Current Discount %",
            value=f"{curr_discount_val:.1f}%",
            subtitle="Original discount applied",
            icon="✂",
            glow_color="blue"
        )
    with b_col5:
        render_kpi_card(
            title="Current Order Amount",
            value=f"${curr_amount_val:,.2f}",
            subtitle="Baseline order revenue",
            icon="💵",
            glow_color="green"
        )
    with b_col6:
        glow = "green" if baseline_predicted_profit >= 0 else "rose"
        icon_profit = "📈" if baseline_predicted_profit >= 0 else "📉"
        render_kpi_card(
            title="Predicted Profit",
            value=f"${baseline_predicted_profit:,.2f}",
            subtitle="Baseline model forecast",
            icon=icon_profit,
            glow_color=glow
        )

    # 5. Discount Slider for Single-Order Simulation
    render_section_title("Interactive Discount Slider", icon="⚙")

    # Round current discount to the nearest 5 for default slider value (bounded in [0, 50])
    default_slider_val = int(round(curr_discount_val / 5.0) * 5)
    default_slider_val = max(0, min(50, default_slider_val))

    simulated_slider_discount = st.slider(
        "Simulate Custom Discount Percentage (%):",
        min_value=0,
        max_value=50,
        value=default_slider_val,
        step=5,
        help="Adjust this slider to simulate the order under a specific discount level."
    )

    try:
        single_sim_df = simulate_discount(model, feature_columns, baseline_order, [simulated_slider_discount])
        if not single_sim_df.empty:
            single_sim = single_sim_df.iloc[0]
            sim_disc_amt = single_sim["Discount_Amount"]
            sim_order_amt = single_sim["Order_Amount"]
            sim_profit = single_sim["Predicted_Profit"]
            profit_diff = sim_profit - baseline_predicted_profit

            s_col1, s_col2, s_col3 = st.columns(3)
            with s_col1:
                render_kpi_card(
                    title="Simulated Discount Amount",
                    value=f"${sim_disc_amt:,.2f}",
                    subtitle=f"{simulated_slider_discount}% discount applied",
                    icon="🏷",
                    glow_color="purple"
                )
            with s_col2:
                render_kpi_card(
                    title="Simulated Order Amount",
                    value=f"${sim_order_amt:,.2f}",
                    subtitle="Recalculated order total",
                    icon="💳",
                    glow_color="blue"
                )
            with s_col3:
                glow_s = "green" if sim_profit >= 0 else "rose"
                diff_sign = "+" if profit_diff >= 0 else ""
                render_kpi_card(
                    title="Simulated Predicted Profit",
                    value=f"${sim_profit:,.2f}",
                    subtitle=f"{diff_sign}${profit_diff:,.2f} vs baseline",
                    icon="💰",
                    glow_color=glow_s
                )
    except Exception as e:
        st.warning(f"Could not compute single slider simulation: {str(e)}")

    # 6. Simulate Discount Range (0%, 10%, 20%, 30%, 40%, 50%)
    render_section_title("Simulate Discount Range", icon="📊")
    st.write("Simulating profitability across standard benchmark discount tiers (0% to 50%):")

    discount_range = [0, 10, 20, 30, 40, 50]
    try:
        scenario_results = simulate_discount(model, feature_columns, baseline_order, discount_range)
    except Exception as e:
        st.error(f"Error executing discount range simulation: {str(e)}")
        return

    # 7. Display Resulting Table
    formatted_display_df = scenario_results.copy()
    st.dataframe(
        formatted_display_df.style.format({
            "Discount_Percent": "{:.0f}%",
            "Discount_Amount": "${:,.2f}",
            "Order_Amount": "${:,.2f}",
            "Predicted_Profit": "${:,.2f}"
        }),
        use_container_width=True
    )

    # 8. Plotly Line Chart: Predicted Profit vs Discount
    best_idx = scenario_results["Predicted_Profit"].idxmax()
    best_row = scenario_results.loc[best_idx]
    best_discount = best_row["Discount_Percent"]
    best_profit = best_row["Predicted_Profit"]

    fig = go.Figure()

    # Scenario trend line
    fig.add_trace(go.Scatter(
        x=scenario_results["Discount_Percent"],
        y=scenario_results["Predicted_Profit"],
        mode="lines+markers",
        name="Predicted Profit",
        line=dict(color=PRIMARY_COLOR, width=3),
        marker=dict(size=9, color=ACCENT_COLOR, line=dict(color="#ffffff", width=1.5)),
        hovertemplate="Discount: %{x}%<br>Predicted Profit: $%{y:,.2f}<extra></extra>"
    ))

    # Highlight optimal discount point
    fig.add_trace(go.Scatter(
        x=[best_discount],
        y=[best_profit],
        mode="markers",
        name="Optimal Profit Tier",
        marker=dict(size=14, color=SECONDARY_COLOR, symbol="star", line=dict(color="#ffffff", width=2)),
        hovertemplate="Optimal Discount: %{x}%<br>Max Profit: $%{y:,.2f}<extra></extra>"
    ))

    chart_layout = get_plotly_layout(height=420, title="Predicted Profit vs Discount")
    chart_layout["xaxis"].update(
        title=dict(text="Discount_Percent (%)", font=dict(color="#cbd5e1")),
        tickmode="array",
        tickvals=discount_range,
        ticktext=[f"{d}%" for d in discount_range]
    )
    chart_layout["yaxis"].update(
        title=dict(text="Predicted_Profit ($)", font=dict(color="#cbd5e1")),
        zeroline=True,
        zerolinecolor="#ef4444"
    )
    fig.update_layout(chart_layout)

    st.plotly_chart(fig, use_container_width=True)

    # 9 & 10. Highlight Optimal Discount & Interpretation
    render_section_title("Optimal Strategy & Recommendation", icon="🎯")

    opt_col1, opt_col2 = st.columns([1, 2])
    with opt_col1:
        render_kpi_card(
            title="Highest Profit Tier",
            value=f"{best_discount:.0f}% Discount",
            subtitle=f"Predicted Profit: ${best_profit:,.2f}",
            icon="⭐",
            glow_color="green"
        )
    with opt_col2:
        render_insight_box(
            title="Strategic Profit Recommendation",
            message=f"For this order, the model predicts the highest profit at {best_discount:.0f}% discount.",
            icon="💡",
            border_color=SECONDARY_COLOR
        )

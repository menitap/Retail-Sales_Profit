"""
Loss DNA / Profit-Risk Explainability UI Module.
Visualizes SHAP-based feature attributions for individual transactions and
global model behavior using a trained Random Forest Regressor.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from backend.what_if import train_profit_model, predict_profit
from backend.loss_dna import get_shap_explanation, get_global_shap_importance
from ui.style import (
    render_kpi_card,
    render_section_title,
    render_insight_box,
    get_plotly_layout,
    PRIMARY_COLOR,
    SECONDARY_COLOR,
    DANGER_COLOR
)


@st.cache_resource(show_spinner=False)
def load_trained_profit_model(df):
    """
    Cached wrapper to train and retrieve the Random Forest model and column metadata.
    Prevents expensive retraining during UI interactions.
    """
    return train_profit_model(df)


@st.cache_data(show_spinner=False)
def load_cached_global_shap(_model, feature_columns, df, sample_size=1000):
    """
    Cached wrapper for computing global SHAP feature importance.
    Caches results across user interactions to keep the UI responsive.
    """
    return get_global_shap_importance(_model, feature_columns, df, sample_size=sample_size)


def render_loss_dna(df):
    """
    Renders the Loss DNA / Profit-Risk Explainability page.
    Analyzes local and global SHAP feature contributions for predicted profitability.
    """
    # 1. Page Header & Informational Scope Note
    render_section_title("Loss DNA: SHAP Profit Explainability", icon="🔍")
    st.markdown(
        """
        <div style="color: #94a3b8; font-size: 0.95rem; margin-top: -0.5rem; margin-bottom: 0.75rem;">
            Understand which factors push a transaction's predicted profit higher or lower.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.info(
        "SHAP explains the model's prediction for a transaction. These contributions indicate model influence, "
        "not causal relationships. This dataset contains no negative-profit transactions, so the analysis focuses on "
        "profit-risk explainability rather than historical loss classification."
    )

    # 2. Dataframe Validation
    if df is None or not isinstance(df, pd.DataFrame) or df.empty:
        st.error("No valid dataset available for Loss DNA analysis.")
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

    # 3. Load Trained Model with Caching
    try:
        with st.spinner("Training / loading Random Forest model..."):
            model, mae, r2, feature_columns = load_trained_profit_model(df)
    except Exception as e:
        st.error(f"Failed to initialize profit model: {str(e)}")
        return

    # 4. Transaction Selector
    render_section_title("Select Transaction", icon="📦")

    order_id_col = None
    if "Order_ID" in df.columns:
        order_id_col = "Order_ID"
    elif "Order ID" in df.columns:
        order_id_col = "Order ID"

    if order_id_col:
        order_options = df[order_id_col].dropna().unique().tolist()
        if not order_options:
            st.warning("No Order IDs available in dataset.")
            return

        selected_order_id = st.selectbox(
            "Select an Order ID to inspect SHAP attributions:",
            options=order_options,
            index=0,
            help="Choose a transaction to analyze feature-level SHAP impact on predicted profit."
        )

        matched_orders = df[df[order_id_col] == selected_order_id]
        if matched_orders.empty:
            st.warning(f"Order ID {selected_order_id} could not be found.")
            return
        selected_order = matched_orders.iloc[0].copy()
    else:
        order_indices = list(range(len(df)))
        selected_idx = st.selectbox(
            "Select Order Index:",
            options=order_indices,
            index=0,
            help="Choose an order row index to inspect."
        )
        selected_order = df.iloc[selected_idx].copy()

    # Extract Baseline Metrics
    order_id_label = selected_order.get(order_id_col, "N/A") if order_id_col else "N/A"
    category_label = selected_order.get("Product_Category", selected_order.get("Category", "N/A"))

    try:
        quantity_val = int(selected_order.get("Quantity", 1))
    except (ValueError, TypeError):
        quantity_val = 1

    try:
        discount_pct_val = float(selected_order.get("Discount_Percent", selected_order.get("Discount", 0.0)))
    except (ValueError, TypeError):
        discount_pct_val = 0.0

    try:
        order_amount_val = float(selected_order.get("Order_Amount", selected_order.get("Sales", 0.0)))
    except (ValueError, TypeError):
        order_amount_val = 0.0

    try:
        predicted_profit_val = predict_profit(model, feature_columns, selected_order)
    except Exception as e:
        st.error(f"Error computing predicted profit: {str(e)}")
        return

    # Render Baseline KPI Cards
    render_section_title("Transaction Profile", icon="📋")

    c1, c2, c3 = st.columns(3)
    with c1:
        render_kpi_card(
            title="Order ID",
            value=str(order_id_label),
            subtitle="Selected transaction",
            icon="📦",
            glow_color="blue"
        )
    with c2:
        render_kpi_card(
            title="Product Category",
            value=str(category_label),
            subtitle=f"Subcategory: {selected_order.get('Product_Subcategory', 'N/A')}",
            icon="🏷",
            glow_color="purple"
        )
    with c3:
        render_kpi_card(
            title="Quantity",
            value=f"{quantity_val} units",
            subtitle="Items purchased",
            icon="🔢",
            glow_color="amber"
        )

    c4, c5, c6 = st.columns(3)
    with c4:
        render_kpi_card(
            title="Discount %",
            value=f"{discount_pct_val:.1f}%",
            subtitle="Applied discount rate",
            icon="✂",
            glow_color="blue"
        )
    with c5:
        render_kpi_card(
            title="Order Amount",
            value=f"${order_amount_val:,.2f}",
            subtitle="Gross transaction revenue",
            icon="💵",
            glow_color="green"
        )
    with c6:
        glow = "green" if predicted_profit_val >= 0 else "rose"
        render_kpi_card(
            title="Predicted Profit",
            value=f"${predicted_profit_val:,.2f}",
            subtitle="Model forecast",
            icon="📈" if predicted_profit_val >= 0 else "📉",
            glow_color=glow
        )

    # 5. Transaction-level SHAP explanation
    try:
        with st.spinner("Computing transaction SHAP values..."):
            explanation_df = get_shap_explanation(model, feature_columns, selected_order)
    except Exception as e:
        st.error(f"Error computing SHAP values: {str(e)}")
        return

    render_section_title("Transaction-Level SHAP Attributions", icon="🔬")

    col_neg, col_pos = st.columns(2)

    # Factors decreasing predicted profit (SHAP_Value < 0)
    with col_neg:
        st.subheader("Factors Decreasing Predicted Profit")
        st.caption("Top 10 features pulling the model's predicted profit lower for this order:")

        neg_df = explanation_df[explanation_df["SHAP_Value"] < 0].copy()
        if not neg_df.empty:
            neg_df["Abs_SHAP"] = neg_df["SHAP_Value"].abs()
            neg_top10 = neg_df.sort_values(by="Abs_SHAP", ascending=False).head(10)
            neg_display = neg_top10[["Feature", "Feature_Value", "SHAP_Value"]].rename(
                columns={
                    "Feature": "Feature",
                    "Feature_Value": "Feature Value",
                    "SHAP_Value": "SHAP Contribution"
                }
            )
            st.dataframe(
                neg_display.style.format({
                    "SHAP Contribution": "{:.2f}",
                    "Feature Value": lambda v: f"{v:,.2f}" if isinstance(v, (int, float)) else str(v)
                }),
                use_container_width=True
            )
        else:
            st.info("No features decrease the predicted profit for this transaction.")

    # Factors increasing predicted profit (SHAP_Value > 0)
    with col_pos:
        st.subheader("Factors Increasing Predicted Profit")
        st.caption("Top 10 features pushing the model's predicted profit higher for this order:")

        pos_df = explanation_df[explanation_df["SHAP_Value"] > 0].copy()
        if not pos_df.empty:
            pos_df["Abs_SHAP"] = pos_df["SHAP_Value"].abs()
            pos_top10 = pos_df.sort_values(by="Abs_SHAP", ascending=False).head(10)
            pos_display = pos_top10[["Feature", "Feature_Value", "SHAP_Value"]].rename(
                columns={
                    "Feature": "Feature",
                    "Feature_Value": "Feature Value",
                    "SHAP_Value": "SHAP Contribution"
                }
            )
            st.dataframe(
                pos_display.style.format({
                    "SHAP Contribution": "{:.2f}",
                    "Feature Value": lambda v: f"{v:,.2f}" if isinstance(v, (int, float)) else str(v)
                }),
                use_container_width=True
            )
        else:
            st.info("No features increase the predicted profit for this transaction.")

    # 6. SHAP Contribution Chart
    render_section_title("Top SHAP Contributors to Predicted Profit", icon="📊")

    top10_overall = explanation_df.head(10).copy()
    top10_plot = top10_overall.iloc[::-1]

    bar_colors = [
        SECONDARY_COLOR if val > 0 else DANGER_COLOR
        for val in top10_plot["SHAP_Value"]
    ]

    fig_local = go.Figure()
    fig_local.add_trace(go.Bar(
        x=top10_plot["SHAP_Value"],
        y=top10_plot["Feature"],
        orientation="h",
        marker=dict(
            color=bar_colors,
            line=dict(color="#334155", width=1)
        ),
        hovertemplate="<b>%{y}</b><br>SHAP Contribution: %{x:.2f}<extra></extra>"
    ))

    layout_local = get_plotly_layout(height=450, title="Top SHAP Contributors to Predicted Profit")
    layout_local["xaxis"].update(
        title=dict(text="SHAP Contribution to Predicted Profit ($)", font=dict(color="#cbd5e1")),
        zeroline=True,
        zerolinecolor="#94a3b8",
        zerolinewidth=2
    )
    layout_local["yaxis"].update(
        title=dict(text="Feature", font=dict(color="#cbd5e1"))
    )
    fig_local.update_layout(layout_local)

    st.plotly_chart(fig_local, use_container_width=True)

    # 7. Global SHAP Feature Importance
    render_section_title("Global SHAP Feature Importance", icon="🌐")
    st.write(
        "This shows which features have the greatest average influence on the model's predicted profit "
        "across the sampled transactions."
    )

    try:
        with st.spinner("Computing global SHAP feature importance..."):
            global_importance_df = load_cached_global_shap(model, feature_columns, df, sample_size=1000)
    except Exception as e:
        st.error(f"Error computing global SHAP importance: {str(e)}")
        return

    top15_global = global_importance_df.head(15).copy()
    top15_plot = top15_global.iloc[::-1]

    fig_global = go.Figure()
    fig_global.add_trace(go.Bar(
        x=top15_plot["Mean_Absolute_SHAP"],
        y=top15_plot["Feature"],
        orientation="h",
        marker=dict(
            color=PRIMARY_COLOR,
            line=dict(color="#334155", width=1)
        ),
        hovertemplate="<b>%{y}</b><br>Mean |SHAP|: %{x:.2f}<extra></extra>"
    ))

    layout_global = get_plotly_layout(height=480, title="Global SHAP Feature Importance")
    layout_global["xaxis"].update(
        title=dict(text="Mean Absolute SHAP Value ($)", font=dict(color="#cbd5e1")),
        zeroline=True,
        zerolinecolor="#334155"
    )
    layout_global["yaxis"].update(
        title=dict(text="Feature", font=dict(color="#cbd5e1"))
    )
    fig_global.update_layout(layout_global)

    st.plotly_chart(fig_global, use_container_width=True)

    # 8. Interpretation Section
    render_section_title("Strategic Attribution Insights", icon="💡")

    neg_contributors = explanation_df[explanation_df["SHAP_Value"] < 0]
    pos_contributors = explanation_df[explanation_df["SHAP_Value"] > 0]

    if not neg_contributors.empty:
        strongest_neg = neg_contributors.loc[neg_contributors["SHAP_Value"].idxmin()]
        neg_feature = strongest_neg["Feature"]
        neg_value = strongest_neg["SHAP_Value"]
        neg_phrase = (
            f"the strongest factor decreasing predicted profit is **{neg_feature}**, with a SHAP contribution "
            f"of **{neg_value:.2f}**"
        )
    else:
        neg_phrase = "no feature pushes the model prediction lower"

    if not pos_contributors.empty:
        strongest_pos = pos_contributors.loc[pos_contributors["SHAP_Value"].idxmax()]
        pos_feature = strongest_pos["Feature"]
        pos_value = strongest_pos["SHAP_Value"]
        pos_phrase = (
            f"the strongest factor increasing predicted profit is **{pos_feature}**, with a SHAP contribution "
            f"of **+{pos_value:.2f}**"
        )
    else:
        pos_phrase = "no feature pushes the model prediction higher"

    interpretation_text = (
        f"For Order **{order_id_label}**, {neg_phrase}. Conversely, {pos_phrase}. "
        f"These figures demonstrate feature contributions that the model associates with the predicted outcome, "
        f"explaining the model's prediction rather than making causal claims."
    )

    render_insight_box(
        title="Model Prediction Attribution",
        message=interpretation_text,
        icon="💡",
        border_color=PRIMARY_COLOR
    )

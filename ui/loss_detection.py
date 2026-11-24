"""
Retail Profitability Risk Detection Dashboard Page.

Displays model predictions, risk distribution, category-wise risk analysis,
individual transaction lookup, and business insights — all powered by the
pre-trained pipeline in ``backend/loss_detector.py``.

The model is loaded once via ``st.cache_resource`` and is NOT retrained on
each Streamlit rerun.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from ui.style import (
    render_kpi_card,
    render_section_title,
    render_insight_box,
    get_plotly_layout,
    PRIMARY_COLOR,
    SECONDARY_COLOR,
    ACCENT_COLOR,
    WARNING_COLOR,
    DANGER_COLOR,
)
from backend.loss_detector import (
    load_data,
    add_target,
    load_pipeline,
    evaluate_model,
    split_data,
    LOW_MARGIN_THRESHOLD,
    _EXCLUDED_COLUMNS,
)


# ---------------------------------------------------------------------------
# Cached loaders  (run once, survive Streamlit reruns)
# ---------------------------------------------------------------------------

@st.cache_resource(show_spinner=False)
def _cached_load_pipeline():
    """Load the saved sklearn pipeline and threshold exactly once."""
    return load_pipeline()


@st.cache_data(show_spinner=False)
def _cached_predictions():
    """Load dataset, compute actual labels, run predictions, and return
    evaluation metrics — all cached so the model is never retrained.

    Returns
    -------
    df : pd.DataFrame
        Full dataset with ``Is_Low_Margin`` (actual), ``Predicted_Risk``
        (predicted label), and ``Risk_Probability`` (predicted proba).
    metrics : dict
        Test-set evaluation metrics from the most recent training run
        (accuracy, precision, recall, F1, confusion matrix).
    threshold : float
        The saved probability decision threshold.
    """
    pipeline, threshold = _cached_load_pipeline()

    # --- Load raw data and add actual labels ---------------------------------
    raw_df = load_data()
    df = add_target(raw_df)  # adds Is_Low_Margin

    # --- Prepare features (drop prohibited columns) --------------------------
    drop_cols = [c for c in _EXCLUDED_COLUMNS if c in df.columns]
    # We also need to drop Is_Low_Margin since it's a target column
    feature_df = df.drop(columns=drop_cols, errors='ignore')

    # --- Predict probabilities using the saved pipeline ----------------------
    proba = pipeline.predict_proba(feature_df)[:, 1]
    preds = (proba >= threshold).astype(int)

    df = df.copy()
    df['Risk_Probability'] = proba
    df['Predicted_Risk'] = preds
    df['Predicted_Label'] = df['Predicted_Risk'].map(
        {1: 'Low-Margin Risk', 0: 'Normal Margin'}
    )
    df['Actual_Label'] = df['Is_Low_Margin'].map(
        {1: 'Low-Margin (Actual)', 0: 'Normal Margin (Actual)'}
    )

    # --- Compute test-set metrics using the same split as training -----------
    y = df['Is_Low_Margin']
    _, X_test, _, y_test = split_data(df, y)

    metrics = evaluate_model(pipeline, X_test, y_test, threshold=threshold)

    return df, metrics, threshold


# ---------------------------------------------------------------------------
# Main render function
# ---------------------------------------------------------------------------

def render_loss_detection(df_unused=None):
    """Entry point called by ``app.py``."""

    render_section_title(
        "Retail Profitability Risk Detection", icon="🎯"
    )

    # Context banner
    render_insight_box(
        title="About This Model",
        message=(
            f"This Random Forest classifier predicts whether an order's profit margin "
            f"falls below the business-defined threshold of <b>{LOW_MARGIN_THRESHOLD}%</b>. "
            f"All transactions in this dataset have positive profit — the model identifies "
            f"<i>low-margin risk</i>, not actual financial losses. "
            f"The {LOW_MARGIN_THRESHOLD}% threshold is a configurable business parameter."
        ),
        icon="ℹ️",
        border_color="#3b82f6",
    )

    # Load cached predictions
    try:
        df, metrics, threshold = _cached_predictions()
    except FileNotFoundError:
        st.error(
            "⚠️ No trained model found. Run `python -m backend.loss_detector` "
            "to train and save the pipeline first."
        )
        return
    except Exception as e:
        st.error(f"⚠️ Error loading model or computing predictions: {e}")
        return

    total = len(df)
    actual_low = int(df['Is_Low_Margin'].sum())
    predicted_low = int(df['Predicted_Risk'].sum())
    predicted_normal = total - predicted_low
    pct_risk = predicted_low / total * 100 if total > 0 else 0

    # ===================================================================
    # A.  RISK OVERVIEW  —  KPI Cards
    # ===================================================================
    render_section_title("Risk Overview", icon="📊")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi_card(
            title="Total Transactions",
            value=f"{total:,}",
            subtitle="Analysed from ecommerce dataset",
            icon="📦",
            glow_color="blue",
        )
    with c2:
        render_kpi_card(
            title="Predicted Low-Margin",
            value=f"{predicted_low:,}",
            subtitle=f"{pct_risk:.1f}% of transactions",
            icon="⚠️",
            glow_color="rose",
        )
    with c3:
        render_kpi_card(
            title="Predicted Normal",
            value=f"{predicted_normal:,}",
            subtitle=f"{100 - pct_risk:.1f}% of transactions",
            icon="✅",
            glow_color="green",
        )
    with c4:
        render_kpi_card(
            title="Actual Low-Margin",
            value=f"{actual_low:,}",
            subtitle=f"{actual_low / total * 100:.1f}% historical rate",
            icon="📋",
            glow_color="purple",
        )

    st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

    # ===================================================================
    # D.  MODEL PERFORMANCE  —  Metrics + Confusion Matrix
    # ===================================================================
    render_section_title("Model Performance (Test Set)", icon="📈")

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        render_kpi_card(
            title="Accuracy",
            value=f"{metrics['accuracy']:.2%}",
            subtitle="Overall correctness",
            icon="🎯",
            glow_color="blue",
        )
    with m2:
        render_kpi_card(
            title="Precision (Low-Margin)",
            value=f"{metrics['precision']:.2%}",
            subtitle="Of predicted risk, % correct",
            icon="🔬",
            glow_color="purple",
        )
    with m3:
        render_kpi_card(
            title="Recall (Low-Margin)",
            value=f"{metrics['recall']:.2%}",
            subtitle="Of actual risk, % detected",
            icon="📡",
            glow_color="amber",
        )
    with m4:
        render_kpi_card(
            title="F1-Score (Low-Margin)",
            value=f"{metrics['f1']:.2%}",
            subtitle="Harmonic mean of P & R",
            icon="⚡",
            glow_color="green",
        )

    st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)

    # Confusion Matrix heatmap
    cm = metrics['confusion_matrix']
    cm_labels = ['Normal Margin (0)', 'Low-Margin Risk (1)']
    fig_cm = go.Figure(data=go.Heatmap(
        z=cm,
        x=cm_labels,
        y=cm_labels,
        text=[[f"{v:,}" for v in row] for row in cm],
        texttemplate="%{text}",
        textfont={"size": 16, "color": "#f8fafc"},
        colorscale=[[0, "#1e293b"], [0.5, "#3b82f6"], [1, "#8b5cf6"]],
        showscale=False,
        hovertemplate="Actual: %{y}<br>Predicted: %{x}<br>Count: %{text}<extra></extra>",
    ))
    layout_cm = get_plotly_layout(height=360, title="Confusion Matrix (Test Set)", showlegend=False)
    layout_cm['xaxis']['title'] = 'Predicted'
    layout_cm['yaxis']['title'] = 'Actual'
    layout_cm['yaxis']['autorange'] = 'reversed'
    fig_cm.update_layout(layout_cm)
    st.plotly_chart(fig_cm, use_container_width=True)

    st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

    # ===================================================================
    # B.  RISK DISTRIBUTION  —  Donut + Probability Histogram
    # ===================================================================
    render_section_title("Risk Distribution", icon="📊")
    dist_c1, dist_c2 = st.columns(2)

    with dist_c1:
        risk_counts = df['Predicted_Label'].value_counts()
        fig_donut = go.Figure(data=[go.Pie(
            labels=risk_counts.index.tolist(),
            values=risk_counts.values.tolist(),
            hole=0.55,
            marker=dict(colors=[SECONDARY_COLOR, DANGER_COLOR]),
            textinfo='percent+label',
            textfont=dict(size=12, color='#f8fafc'),
            hovertemplate="Classification: %{label}<br>Count: %{value:,}<br>Share: %{percent}<extra></extra>",
        )])
        layout_donut = get_plotly_layout(
            height=380,
            title="Predicted Risk Distribution",
        )
        fig_donut.update_layout(layout_donut)
        st.plotly_chart(fig_donut, use_container_width=True)

    with dist_c2:
        fig_hist = go.Figure()
        fig_hist.add_trace(go.Histogram(
            x=df['Risk_Probability'],
            nbinsx=50,
            marker_color=PRIMARY_COLOR,
            opacity=0.85,
            hovertemplate="Probability: %{x:.2f}<br>Count: %{y:,}<extra></extra>",
            name='Transactions',
        ))
        # Decision threshold line
        fig_hist.add_vline(
            x=threshold,
            line_dash='dash',
            line_color=DANGER_COLOR,
            line_width=2,
            annotation_text=f"Threshold = {threshold:.2f}",
            annotation_position="top right",
            annotation_font_color="#ef4444",
            annotation_font_size=12,
        )
        layout_hist = get_plotly_layout(
            height=380,
            title="Distribution of Predicted Low-Margin Probability",
            showlegend=False,
        )
        layout_hist['xaxis']['title'] = 'Predicted Probability'
        layout_hist['yaxis']['title'] = 'Transaction Count'
        fig_hist.update_layout(layout_hist)
        st.plotly_chart(fig_hist, use_container_width=True)

    st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

    # ===================================================================
    # C.  CATEGORY-WISE RISK ANALYSIS
    # ===================================================================
    render_section_title("Category-Wise Risk Analysis", icon="📦")

    cat_risk = (
        df.groupby('Product_Category')['Predicted_Risk']
        .agg(['sum', 'count'])
        .rename(columns={'sum': 'Low_Margin_Count', 'count': 'Total'})
    )
    cat_risk['Risk_Pct'] = (cat_risk['Low_Margin_Count'] / cat_risk['Total'] * 100)
    cat_risk = cat_risk.sort_values('Risk_Pct', ascending=True).reset_index()

    fig_cat = go.Figure(go.Bar(
        y=cat_risk['Product_Category'],
        x=cat_risk['Risk_Pct'],
        orientation='h',
        marker=dict(
            color=cat_risk['Risk_Pct'],
            colorscale=[[0, SECONDARY_COLOR], [0.5, WARNING_COLOR], [1, DANGER_COLOR]],
            showscale=False,
        ),
        text=[f"{v:.1f}%" for v in cat_risk['Risk_Pct']],
        textposition='auto',
        hovertemplate=(
            "Category: %{y}<br>"
            "Risk Rate: %{x:.1f}%<br>"
            "<extra></extra>"
        ),
    ))
    layout_cat = get_plotly_layout(
        height=380,
        title="Low-Margin Risk Rate by Product Category",
        showlegend=False,
    )
    layout_cat['xaxis']['title'] = 'Predicted Low-Margin Risk (%)'
    fig_cat.update_layout(layout_cat)
    st.plotly_chart(fig_cat, use_container_width=True)

    st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

    # ===================================================================
    # D.  INDIVIDUAL TRANSACTION PREDICTION
    # ===================================================================
    render_section_title("Individual Transaction Prediction", icon="🔍")

    order_ids = df['Order_ID'].tolist()
    selected_id = st.selectbox(
        "Select an Order ID",
        options=order_ids,
        index=0,
        help="Choose a transaction to view its profitability risk prediction.",
    )

    row = df[df['Order_ID'] == selected_id]
    if not row.empty:
        row = row.iloc[0]
        prob = row['Risk_Probability']
        pred_label = row['Predicted_Label']
        actual_label = row['Actual_Label']

        is_risk = row['Predicted_Risk'] == 1
        result_color = DANGER_COLOR if is_risk else SECONDARY_COLOR
        result_icon = "⚠️" if is_risk else "✅"
        badge_class = "badge-warning" if is_risk else "badge-success"

        detail_c1, detail_c2 = st.columns([3, 2])

        with detail_c1:
            st.markdown(
                f"""
                <div style="background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 1.25rem; margin-bottom: 1rem;">
                    <div style="font-size: 0.8rem; color: #94a3b8; text-transform: uppercase; font-weight: 600; letter-spacing: 0.05em; margin-bottom: 0.75rem;">
                        Transaction Details
                    </div>
                    <table style="width: 100%; font-size: 0.85rem; color: #cbd5e1; border-collapse: collapse;">
                        <tr><td style="padding: 0.35rem 0; color: #94a3b8;">Order ID</td><td style="padding: 0.35rem 0; font-weight: 600;">{row['Order_ID']}</td></tr>
                        <tr><td style="padding: 0.35rem 0; color: #94a3b8;">Category</td><td style="padding: 0.35rem 0;">{row.get('Product_Category', 'N/A')}</td></tr>
                        <tr><td style="padding: 0.35rem 0; color: #94a3b8;">Sub-Category</td><td style="padding: 0.35rem 0;">{row.get('Product_Subcategory', 'N/A')}</td></tr>
                        <tr><td style="padding: 0.35rem 0; color: #94a3b8;">Region</td><td style="padding: 0.35rem 0;">{row.get('Warehouse_Region', 'N/A')}</td></tr>
                        <tr><td style="padding: 0.35rem 0; color: #94a3b8;">Order Amount</td><td style="padding: 0.35rem 0;">${row.get('Order_Amount', 0):,.2f}</td></tr>
                        <tr><td style="padding: 0.35rem 0; color: #94a3b8;">Discount</td><td style="padding: 0.35rem 0;">{row.get('Discount_Percent', 0)}%</td></tr>
                        <tr><td style="padding: 0.35rem 0; color: #94a3b8;">Unit Price</td><td style="padding: 0.35rem 0;">${row.get('Unit_Price', 0):,.2f}</td></tr>
                        <tr><td style="padding: 0.35rem 0; color: #94a3b8;">Quantity</td><td style="padding: 0.35rem 0;">{row.get('Quantity', 'N/A')}</td></tr>
                    </table>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with detail_c2:
            st.markdown(
                f"""
                <div style="background: #1e293b; border: 1px solid #334155; border-left: 4px solid {result_color}; border-radius: 12px; padding: 1.25rem; margin-bottom: 1rem;">
                    <div style="font-size: 0.8rem; color: #94a3b8; text-transform: uppercase; font-weight: 600; letter-spacing: 0.05em; margin-bottom: 0.75rem;">
                        Prediction Result
                    </div>
                    <div style="font-size: 1.5rem; font-weight: 700; color: {result_color}; margin-bottom: 0.5rem;">
                        {result_icon} {pred_label}
                    </div>
                    <div style="font-size: 0.85rem; color: #cbd5e1; margin-bottom: 0.4rem;">
                        <b>Probability:</b> {prob:.4f} ({prob:.1%})
                    </div>
                    <div style="font-size: 0.85rem; color: #cbd5e1; margin-bottom: 0.75rem;">
                        <b>Decision Threshold:</b> {threshold:.2f}
                    </div>
                    <div style="border-top: 1px solid #334155; padding-top: 0.6rem; margin-top: 0.4rem;">
                        <div style="font-size: 0.75rem; color: #94a3b8; text-transform: uppercase; font-weight: 600; margin-bottom: 0.3rem;">
                            Historical Actual
                        </div>
                        <div style="font-size: 0.9rem; color: #a78bfa; font-weight: 600;">
                            {actual_label}
                        </div>
                        <div style="font-size: 0.75rem; color: #64748b; margin-top: 0.2rem;">
                            Profit Margin: {row.get('Profit_Margin_Percent', 0):.2f}%
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

    # ===================================================================
    # E.  TRANSACTION PREDICTION TABLE
    # ===================================================================
    render_section_title("Transaction Prediction Table", icon="📋")

    filter_option = st.radio(
        "Filter transactions:",
        ["All Transactions", "Low-Margin Risk", "Normal Margin"],
        horizontal=True,
    )

    display_cols = [
        'Order_ID', 'Product_Category', 'Warehouse_Region',
        'Order_Amount', 'Discount_Percent', 'Risk_Probability',
        'Predicted_Label', 'Actual_Label',
    ]
    # Only keep columns that exist
    display_cols = [c for c in display_cols if c in df.columns]

    table_df = df[display_cols].copy()

    if filter_option == "Low-Margin Risk":
        table_df = table_df[df['Predicted_Risk'] == 1]
    elif filter_option == "Normal Margin":
        table_df = table_df[df['Predicted_Risk'] == 0]

    st.dataframe(
        table_df.head(500).style.format({
            'Order_Amount': '${:,.2f}',
            'Discount_Percent': '{:.0f}%',
            'Risk_Probability': '{:.4f}',
        }),
        use_container_width=True,
        hide_index=True,
        height=420,
    )

    st.caption(
        f"Showing {min(500, len(table_df)):,} of {len(table_df):,} "
        f"transactions. 'Predicted_Label' is the model output; "
        f"'Actual_Label' is the historical ground truth."
    )

    st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

    # ===================================================================
    # F.  BUSINESS INSIGHTS
    # ===================================================================
    render_section_title("Business Insights", icon="💡")

    # Find the riskiest category
    riskiest = cat_risk.iloc[-1]  # sorted ascending, last is highest
    riskiest_name = riskiest['Product_Category']
    riskiest_pct = riskiest['Risk_Pct']

    # Find the safest category
    safest = cat_risk.iloc[0]
    safest_name = safest['Product_Category']
    safest_pct = safest['Risk_Pct']

    # Average discount for predicted risk vs normal
    avg_disc_risk = df.loc[df['Predicted_Risk'] == 1, 'Discount_Percent'].mean()
    avg_disc_normal = df.loc[df['Predicted_Risk'] == 0, 'Discount_Percent'].mean()

    render_insight_box(
        title="Highest Risk Category",
        message=(
            f"<b>{riskiest_name}</b> has the highest predicted low-margin risk rate at "
            f"<b>{riskiest_pct:.1f}%</b>. Transactions in this category warrant closer "
            f"scrutiny on pricing, discount policies, and supplier cost negotiations."
        ),
        icon="🔴",
        border_color=DANGER_COLOR,
    )

    render_insight_box(
        title="Discount Correlation with Risk",
        message=(
            f"Transactions predicted as low-margin risk have an average discount of "
            f"<b>{avg_disc_risk:.1f}%</b>, compared to <b>{avg_disc_normal:.1f}%</b> for "
            f"normal-margin transactions. Higher discounts correlate strongly with margin erosion."
        ),
        icon="🏷️",
        border_color=WARNING_COLOR,
    )

    render_insight_box(
        title="Safest Category",
        message=(
            f"<b>{safest_name}</b> has the lowest predicted risk rate at "
            f"<b>{safest_pct:.1f}%</b>, indicating robust margin performance. "
            f"Best practices from this category can inform pricing strategies elsewhere."
        ),
        icon="🟢",
        border_color=SECONDARY_COLOR,
    )

    render_insight_box(
        title="Methodology Note",
        message=(
            f"The model uses a Random Forest classifier with {LOW_MARGIN_THRESHOLD}% profit "
            f"margin as the business-defined risk threshold. The classification threshold of "
            f"<b>{threshold:.2f}</b> was selected via 3-fold cross-validation on training data. "
            f"All transactions are profitable — 'low-margin risk' means margin below "
            f"{LOW_MARGIN_THRESHOLD}%, not an actual loss."
        ),
        icon="📐",
        border_color="#6366f1",
    )

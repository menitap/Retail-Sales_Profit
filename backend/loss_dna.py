"""
Loss DNA / Profit-Risk Explainability Module.
Provides SHAP (SHapley Additive exPlanations) for the Random Forest profit model.

Dataset Context & Architecture:
- In the retail dataset, Profit_Amount is uniformly non-negative (no historical loss transactions).
- Rather than manufacturing synthetic loss classifications, this module explains the
  Random Forest Regressor's predicted profit, isolating specific feature contributions
  that depress margins or drive low-profit outcomes ("Profit-Risk / Loss DNA").
"""

import numpy as np
import pandas as pd
import shap


def prepare_model_input(order_data, feature_columns):
    """
    Prepare order data as model input matching train_profit_model.

    Parameters:
        order_data: pandas Series, dictionary, or single-row DataFrame.
        feature_columns: list or Index of feature names expected by the model.

    Returns:
        pd.DataFrame: A single-row DataFrame encoded and reindexed to feature_columns.
    """
    if order_data is None:
        raise ValueError("order_data cannot be None")

    if isinstance(order_data, pd.DataFrame):
        if order_data.empty:
            raise ValueError("order_data DataFrame is empty")
        order_df = order_data.iloc[[0]].copy()
    elif isinstance(order_data, pd.Series):
        if order_data.empty:
            raise ValueError("order_data Series is empty")
        order_df = pd.DataFrame([order_data])
    elif isinstance(order_data, dict):
        if not order_data:
            raise ValueError("order_data dictionary is empty")
        order_df = pd.DataFrame([order_data])
    else:
        order_df = pd.DataFrame([dict(order_data)])

    # Apply one-hot encoding for categorical variables.
    # Note: feature_columns was constructed using pd.get_dummies(..., drop_first=True)
    # during train_profit_model. Reindexing against feature_columns retains precisely
    # the non-dropped category dummy indicators and fills absent ones with 0.
    encoded_df = pd.get_dummies(order_df)
    model_input = encoded_df.reindex(columns=feature_columns, fill_value=0)

    # Ensure all columns are numeric
    model_input = model_input.astype(float)
    return model_input


def get_shap_explanation(model, feature_columns, order_data):
    """
    Compute local SHAP explanations for a single transaction.

    Parameters:
        model: Trained Random Forest Regressor from train_profit_model.
        feature_columns: Feature names expected by the model.
        order_data: pandas Series, dictionary, or single-row DataFrame.

    Returns:
        pd.DataFrame: DataFrame containing Feature, Feature_Value, SHAP_Value, Impact,
                      sorted by absolute SHAP value descending.
    """
    if model is None:
        raise ValueError("model cannot be None")

    model_input = prepare_model_input(order_data, feature_columns)

    # Initialize SHAP TreeExplainer for the Random Forest model
    explainer = shap.TreeExplainer(model)
    shap_vals = explainer.shap_values(model_input)

    # TreeExplainer for regressors returns an ndarray (1, n_features)
    if isinstance(shap_vals, list):
        vals = shap_vals[0]
    else:
        vals = shap_vals[0] if shap_vals.ndim > 1 else shap_vals

    feature_values = model_input.iloc[0].values

    # Determine impact direction for each feature
    impacts = []
    for val in vals:
        if val > 0:
            impacts.append("Increases Predicted Profit")
        elif val < 0:
            impacts.append("Decreases Predicted Profit")
        else:
            impacts.append("No Impact")

    explanation_df = pd.DataFrame({
        "Feature": list(feature_columns),
        "Feature_Value": feature_values,
        "SHAP_Value": vals,
        "Impact": impacts
    })

    # Sort by absolute SHAP value descending
    explanation_df["Abs_SHAP"] = explanation_df["SHAP_Value"].abs()
    explanation_df = explanation_df.sort_values(by="Abs_SHAP", ascending=False).drop(columns=["Abs_SHAP"]).reset_index(drop=True)

    return explanation_df


def get_global_shap_importance(model, feature_columns, df, sample_size=1000):
    """
    Calculate global feature importance across a representative sample of transactions using SHAP.

    Parameters:
        model: Trained Random Forest Regressor.
        feature_columns: Feature names expected by the model.
        df: pandas DataFrame containing dataset transactions.
        sample_size: Maximum number of rows to sample for responsiveness (default 1000).

    Returns:
        pd.DataFrame: DataFrame containing Feature and Mean_Absolute_SHAP, sorted descending.
    """
    if model is None:
        raise ValueError("model cannot be None")
    if df is None or df.empty:
        return pd.DataFrame(columns=["Feature", "Mean_Absolute_SHAP"])

    # Draw representative sample
    n = min(len(df), max(1, sample_size))
    if len(df) > n:
        sample_df = df.sample(n=n, random_state=42)
    else:
        sample_df = df.copy()

    # Encode sample matching model inputs
    encoded_sample = pd.get_dummies(sample_df)
    X_sample = encoded_sample.reindex(columns=feature_columns, fill_value=0).astype(float)

    # Compute SHAP values for the sample
    explainer = shap.TreeExplainer(model)
    shap_vals = explainer.shap_values(X_sample)

    if isinstance(shap_vals, list):
        shap_vals = shap_vals[0]

    # Calculate mean absolute SHAP value per feature
    mean_abs_shap = np.abs(shap_vals).mean(axis=0)

    importance_df = pd.DataFrame({
        "Feature": list(feature_columns),
        "Mean_Absolute_SHAP": mean_abs_shap
    })

    importance_df = importance_df.sort_values(by="Mean_Absolute_SHAP", ascending=False).reset_index(drop=True)
    return importance_df


def get_top_negative_contributors(model, feature_columns, order_data, top_n=10):
    """
    Extract the top features that depress predicted profit (negative SHAP values) for a transaction.
    Identifies the 'Loss DNA' / risk drivers pulling profit down.

    Parameters:
        model: Trained Random Forest Regressor.
        feature_columns: Feature names expected by the model.
        order_data: Single transaction data.
        top_n: Maximum number of negative contributors to return (default 10).

    Returns:
        pd.DataFrame: Negative contributors sorted from most negative to least negative.
    """
    explanation_df = get_shap_explanation(model, feature_columns, order_data)

    # Filter to features that decrease predicted profit
    negative_df = explanation_df[explanation_df["SHAP_Value"] < 0].copy()

    # Sort from most negative to least negative (ascending)
    negative_df = negative_df.sort_values(by="SHAP_Value", ascending=True).head(top_n).reset_index(drop=True)

    return negative_df

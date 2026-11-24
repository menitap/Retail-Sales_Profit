"""
Retail Profitability Risk Detection
====================================

Identifies e-commerce orders at risk of low profitability using a
scikit-learn Pipeline (ColumnTransformer + RandomForestClassifier).

Target definition
-----------------
``Is_Low_Margin`` = 1 when ``Profit_Margin_Percent < LOW_MARGIN_THRESHOLD``
(default **10 %**), else 0.

.. important::

   The 10 % threshold is a **configurable business parameter**, not an
   empirical loss boundary.  Every row in this dataset has strictly positive
   ``Profit_Amount`` (minimum 0.27), so none of these orders are actual
   losses.  The model flags orders whose profit margin falls below a
   business-defined acceptable level.  Adjust ``LOW_MARGIN_THRESHOLD`` to
   match the organisation's risk appetite.

Order-ID handling
-----------------
Every ``Order_ID`` in the dataset is unique (30 000 unique IDs for
30 000 rows), so group-based splitting is unnecessary.  A standard
stratified train / test split is used, and an assertion verifies that
no Order_ID appears in both sets.

Preprocessing-leakage prevention
---------------------------------
1. The raw DataFrame is split **before** any preprocessing.
2. ``OneHotEncoder`` and ``StandardScaler`` are fitted **only** on the
   training fold via the sklearn ``Pipeline``.
3. Test data is transformed using the already-fitted pipeline.

Feature selection
-----------------
The following columns are **excluded** from features:

* ``Profit_Amount``, ``Profit_Margin_Percent``, ``Is_Low_Margin`` –
  target / target-derived (leakage).
* ``Order_ID``, ``Customer_ID``, ``Product_ID`` – identifiers that lead
  to memorisation.
* ``Order_Date`` – raw date string with 1 461 unique values; the
  calendar information is already encoded in ``Year``, ``Month``,
  ``Day``, ``Day_Of_Week``, ``Quarter``, ``Season``.
* ``High_Value_Order`` – derived from ``Order_Amount``; keeping it adds
  no independent information and risks subtle leakage.

Data-type handling
------------------
* Object-dtype columns → ``OneHotEncoder`` (with ``handle_unknown='ignore'``).
* Boolean-like Yes/No strings (``Coupon_Used``, ``Returned``,
  ``Holiday_Season``) are treated as categoricals and one-hot encoded.
* Integer / float columns → ``StandardScaler``.

Threshold tuning
----------------
Because the dataset is imbalanced (~10 % positive class), the default
0.5 probability threshold can produce zero recall.  After fitting the
pipeline on the **full training set**, we select the optimal
classification threshold via **stratified 3-fold cross-validation on
the training data only**.  For each fold the pipeline is re-fitted on
the fold-train split, probabilities are predicted on the fold-val split,
and we sweep thresholds to maximise F1 for the positive class.  The
median best threshold across folds is selected.  The test set is
**never** used during threshold selection.
"""

from __future__ import annotations

import os
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(_THIS_DIR, '..', 'data', 'ecommerce_orders_dataset.csv')
MODEL_DIR = os.path.join(_THIS_DIR, 'models')
MODEL_PATH = os.path.join(MODEL_DIR, 'profitability_risk_pipeline.pkl')
RANDOM_STATE = 42

# Business-configurable margin threshold.
# Orders with Profit_Margin_Percent below this value are flagged as
# "low margin" (Is_Low_Margin = 1).  This is NOT an actual-loss boundary;
# it is a risk-appetite parameter that the business can tune.
LOW_MARGIN_THRESHOLD = 10  # percent

# Columns that must NEVER appear as model inputs.
_EXCLUDED_COLUMNS: set[str] = {
    # Target / target-derived  — leak the answer
    'Profit_Amount',
    'Profit_Margin_Percent',
    'Is_Low_Margin',
    # Identifiers  — lead to memorisation, not generalisation
    'Order_ID',
    'Customer_ID',
    'Product_ID',
    # Raw date string  — calendar fields (Year, Month, …) already present
    'Order_Date',
    # Derived flag  — computed from Order_Amount, adds no independent info
    'High_Value_Order',
}


# ---------------------------------------------------------------------------
# Data loading & target creation
# ---------------------------------------------------------------------------

def load_data() -> pd.DataFrame:
    """Load the raw e-commerce CSV."""
    return pd.read_csv(DATA_PATH)


def add_target(df: pd.DataFrame) -> pd.DataFrame:
    """Create binary target ``Is_Low_Margin``.

    ``Is_Low_Margin = 1`` when ``Profit_Margin_Percent < LOW_MARGIN_THRESHOLD``.

    The threshold (default 10 %) is a **configurable business parameter**.
    All orders in this dataset are profitable (``Profit_Amount > 0``);
    the flag identifies orders whose margin falls below an acceptable level,
    not orders that incur an actual financial loss.

    Raises
    ------
    ValueError
        If ``Profit_Margin_Percent`` is missing.
    """
    if 'Profit_Margin_Percent' not in df.columns:
        raise ValueError(
            'Profit_Margin_Percent column not found – cannot create target.'
        )
    df = df.copy()
    df['Is_Low_Margin'] = (
        df['Profit_Margin_Percent'] < LOW_MARGIN_THRESHOLD
    ).astype(int)
    return df


# ---------------------------------------------------------------------------
# Feature identification
# ---------------------------------------------------------------------------

def _identify_feature_columns(
    df: pd.DataFrame,
) -> tuple[list[str], list[str], list[str]]:
    """Return ``(categorical_cols, numeric_cols, dropped_cols)``.

    * Drops every column in ``_EXCLUDED_COLUMNS`` that exists in *df*.
    * Object / string dtype → categorical.
    * Int / float dtype → numeric.
    * Bool dtype columns (if any) are cast to int and treated as numeric.
    """
    dropped = sorted(c for c in _EXCLUDED_COLUMNS if c in df.columns)
    feature_df = df.drop(columns=dropped)

    categorical_cols = feature_df.select_dtypes(
        include=['object', 'string']
    ).columns.tolist()

    numeric_cols = feature_df.select_dtypes(
        include=['int64', 'int32', 'float64', 'float32']
    ).columns.tolist()

    # Safety: boolean columns → numeric
    bool_cols = feature_df.select_dtypes(include=['bool']).columns.tolist()
    if bool_cols:
        numeric_cols.extend(bool_cols)

    return categorical_cols, numeric_cols, dropped


# ---------------------------------------------------------------------------
# Splitting
# ---------------------------------------------------------------------------

def split_data(
    df: pd.DataFrame,
    y: pd.Series,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """Split into train / test (80 / 20), stratified by *y*.

    ``Order_ID`` is unique across all rows, so a plain stratified split is
    correct.  When ``Order_ID`` is present the function still verifies zero
    overlap between splits.

    Returns
    -------
    X_train, X_test, y_train, y_test
    """
    X_train, X_test, y_train, y_test = train_test_split(
        df, y,
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    # Verify no Order_ID leakage between train and test
    if 'Order_ID' in df.columns:
        train_ids = set(X_train['Order_ID'])
        test_ids = set(X_test['Order_ID'])
        overlap = train_ids & test_ids
        assert len(overlap) == 0, (
            f'Order_ID leak: {len(overlap)} IDs in both train and test!'
        )

    return X_train, X_test, y_train, y_test


# ---------------------------------------------------------------------------
# Pipeline construction
# ---------------------------------------------------------------------------

def _build_preprocessor(
    categorical_cols: list[str],
    numeric_cols: list[str],
) -> ColumnTransformer:
    """Column transformer: OHE for categoricals, standard-scale for numerics.

    Not fitted here — fitting happens inside the full pipeline on training
    data only.
    """
    return ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False),
             categorical_cols),
            ('num', StandardScaler(), numeric_cols),
        ],
        remainder='drop',           # silently drop any unlisted columns
    )


def build_pipeline(
    categorical_cols: list[str],
    numeric_cols: list[str],
) -> Pipeline:
    """Create the full preprocessing + classifier pipeline."""
    preprocessor = _build_preprocessor(categorical_cols, numeric_cols)
    clf = RandomForestClassifier(
        n_estimators=300,
        max_depth=20,
        min_samples_leaf=5,
        class_weight='balanced',     # handle class imbalance
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )
    return Pipeline([
        ('preprocess', preprocessor),
        ('clf', clf),
    ])


# ---------------------------------------------------------------------------
# Threshold tuning  (cross-validated on training data only)
# ---------------------------------------------------------------------------

def _find_best_threshold_cv(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    categorical_cols: list[str],
    numeric_cols: list[str],
    n_splits: int = 3,
) -> float:
    """Select the probability threshold that maximises positive-class F1.

    Uses **stratified k-fold cross-validation on the training set only**
    so the held-out test set is never touched.

    For each fold:
      1. A fresh pipeline is built and fitted on the fold-train portion.
      2. ``predict_proba`` is called on the fold-validation portion.
      3. We sweep thresholds (0.05 – 0.95) and record the one with the
         highest F1 for class 1.

    The final threshold is the **median** of the per-fold best thresholds,
    which is more robust than the mean to outlier folds.
    """
    skf = StratifiedKFold(
        n_splits=n_splits, shuffle=True, random_state=RANDOM_STATE,
    )
    fold_thresholds: list[float] = []

    for fold_idx, (tr_idx, val_idx) in enumerate(
        skf.split(X_train, y_train), start=1,
    ):
        X_tr  = X_train.iloc[tr_idx]
        y_tr  = y_train.iloc[tr_idx]
        X_val = X_train.iloc[val_idx]
        y_val = y_train.iloc[val_idx]

        fold_pipe = build_pipeline(categorical_cols, numeric_cols)
        fold_pipe.fit(X_tr, y_tr)

        proba_val = fold_pipe.predict_proba(X_val)[:, 1]

        best_f1, best_thr = 0.0, 0.5
        for thr in np.arange(0.05, 0.96, 0.01):
            preds = (proba_val >= thr).astype(int)
            f = f1_score(y_val, preds, zero_division=0)
            if f > best_f1:
                best_f1 = f
                best_thr = float(thr)

        fold_thresholds.append(round(best_thr, 2))
        print(f'  Fold {fold_idx}/{n_splits}: best threshold = '
              f'{best_thr:.2f}, F1(val) = {best_f1:.4f}')

    chosen = round(float(np.median(fold_thresholds)), 2)
    print(f'  Median threshold across {n_splits} folds: {chosen}')
    return chosen


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------

def evaluate_model(
    pipeline: Pipeline,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    threshold: float = 0.5,
) -> dict[str, Any]:
    """Predict on *X_test* using *threshold* and return a metrics dict.

    The test set is used **only here**, for final evaluation after all
    training and threshold selection are complete.
    """
    proba = pipeline.predict_proba(X_test)[:, 1]
    preds = (proba >= threshold).astype(int)
    return {
        'accuracy':  accuracy_score(y_test, preds),
        'precision': precision_score(y_test, preds, zero_division=0),
        'recall':    recall_score(y_test, preds, zero_division=0),
        'f1':        f1_score(y_test, preds, zero_division=0),
        'confusion_matrix': confusion_matrix(y_test, preds).tolist(),
        'classification_report': classification_report(
            y_test, preds, zero_division=0, output_dict=True,
        ),
        'class_distribution_test': y_test.value_counts().to_dict(),
        'threshold': threshold,
    }


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------

def save_pipeline(pipeline: Pipeline, threshold: float) -> None:
    """Persist the **fitted** pipeline and optimal threshold to disk."""
    os.makedirs(MODEL_DIR, exist_ok=True)
    artifact = {'pipeline': pipeline, 'threshold': threshold}
    joblib.dump(artifact, MODEL_PATH)


def load_pipeline() -> tuple[Pipeline, float]:
    """Load a previously saved pipeline and its threshold."""
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            'Saved pipeline not found.  Train the model first.'
        )
    artifact = joblib.load(MODEL_PATH)
    # Backward compatibility: if the saved file is a bare pipeline
    if isinstance(artifact, Pipeline):
        return artifact, 0.5
    return artifact['pipeline'], artifact['threshold']


# ---------------------------------------------------------------------------
# Prediction (inference)
# ---------------------------------------------------------------------------

def predict(df: pd.DataFrame) -> pd.Series:
    """Predict ``Is_Low_Margin`` for new data.

    The input DataFrame must have the same schema as the training source.
    Target-derived columns (``Profit_Amount``, ``Profit_Margin_Percent``,
    ``Is_Low_Margin``) are **not allowed** and will raise ``ValueError``.
    Identifier and excluded columns are dropped automatically.
    Missing or incompatible features raise ``ValueError``.
    """
    pipeline, threshold = load_pipeline()

    # ---- Guard: reject any target-derived columns ------------------------
    prohibited = {'Profit_Amount', 'Profit_Margin_Percent', 'Is_Low_Margin'}
    found = prohibited & set(df.columns)
    if found:
        raise ValueError(
            f'Input contains prohibited target-derived columns: {found}'
        )

    # ---- Drop identifiers / excluded columns (same as training) ----------
    drop_cols = {'Order_ID', 'Customer_ID', 'Product_ID',
                 'Order_Date', 'High_Value_Order'}
    df_features = df.drop(columns=[c for c in drop_cols if c in df.columns])

    # ---- Verify that the expected feature columns are present ------------
    ct: ColumnTransformer = pipeline.named_steps['preprocess']
    expected_cols: set[str] = set()
    for _, _, cols in ct.transformers:
        if isinstance(cols, list):
            expected_cols.update(cols)

    present = set(df_features.columns)
    missing = expected_cols - present
    if missing:
        raise ValueError(
            f'Input is missing required feature columns: {sorted(missing)}'
        )

    proba = pipeline.predict_proba(df_features)[:, 1]
    preds = (proba >= threshold).astype(int)
    return pd.Series(preds, index=df.index, name='Is_Low_Margin_Pred')


# ---------------------------------------------------------------------------
# End-to-end execution (audit / local testing)
# ---------------------------------------------------------------------------

def train_and_evaluate() -> dict[str, Any]:
    """Run the full pipeline: load → split → fit → evaluate → save.

    Returns a dict of metrics and diagnostics so callers (including a
    future dashboard) can present them without re-running.
    """
    # 1. Load raw data
    raw_df = load_data()
    print(f'Rows loaded: {len(raw_df):,}')

    # 2. Order_ID inspection
    if 'Order_ID' in raw_df.columns:
        n_unique = raw_df['Order_ID'].nunique()
        n_rows   = len(raw_df)
        all_unique = (n_unique == n_rows)
        dup_count  = n_rows - n_unique
        print(f'Order_ID unique? {all_unique}  '
              f'(unique: {n_unique:,}, duplicates: {dup_count:,})')
        if all_unique:
            print('  → Each row is an independent order; '
                  'stratified split is appropriate.')
    else:
        print('Order_ID column not present in dataset.')

    # 3. Create target
    df = add_target(raw_df)
    y  = df['Is_Low_Margin']

    # 4. Report class distribution
    dist = y.value_counts()
    total = len(y)
    print(f'\nTarget: Is_Low_Margin  (Profit_Margin_Percent < '
          f'{LOW_MARGIN_THRESHOLD}%)')
    print(f'NOTE: {LOW_MARGIN_THRESHOLD}% is a configurable business '
          f'threshold, not an actual loss boundary.')
    print(f'      All orders in this dataset have positive Profit_Amount.')
    print(f'\nClass distribution (full dataset):')
    for cls_label in sorted(dist.index):
        cnt = dist[cls_label]
        pct = cnt / total * 100
        label = 'Low-margin' if cls_label == 1 else 'Normal-margin'
        print(f'  {label} (Is_Low_Margin={cls_label}): {cnt:,} ({pct:.1f}%)')

    imbalance_ratio = dist.min() / dist.max()
    if imbalance_ratio < 0.2:
        print(f'  ⚠  Class imbalance detected (minority / majority = '
              f'{imbalance_ratio:.3f}).  Using class_weight="balanced".')

    # 5. Identify features
    cat_cols, num_cols, dropped = _identify_feature_columns(df)
    all_features = sorted(cat_cols + num_cols)
    print(f'\nColumns EXCLUDED from features ({len(dropped)}): {dropped}')
    print(f'Categorical features ({len(cat_cols)}): {sorted(cat_cols)}')
    print(f'Numeric features     ({len(num_cols)}): {sorted(num_cols)}')
    print(f'Total feature columns: {len(all_features)}')

    # 6. Split BEFORE preprocessing (no leakage)
    X_train, X_test, y_train, y_test = split_data(df, y)
    print(f'\nTrain records: {len(y_train):,}   Test records: {len(y_test):,}')

    if 'Order_ID' in df.columns:
        train_ids = set(X_train['Order_ID'])
        test_ids  = set(X_test['Order_ID'])
        overlap   = train_ids & test_ids
        print(f'Order_ID overlap between train and test: {len(overlap)}')

    # Report train / test class distribution
    for label, ys in [('Train', y_train), ('Test', y_test)]:
        d = ys.value_counts()
        print(f'  {label} class distribution: '
              + ', '.join(f'{k}={v}' for k, v in sorted(d.items())))

    # 7. Find optimal threshold via cross-validation on TRAINING data only.
    #    The test set is NOT used here.
    print('\nThreshold tuning (3-fold stratified CV on training data):')
    threshold = _find_best_threshold_cv(
        X_train, y_train, cat_cols, num_cols, n_splits=3,
    )

    # 8. Build & fit the FINAL pipeline on the full training set.
    #    Preprocessing is fitted here — only on training data.
    pipeline = build_pipeline(cat_cols, num_cols)
    pipeline.fit(X_train, y_train)
    print('\nFinal pipeline fitted on full training data.')

    # 9. Evaluate on the held-out test set (first and only use of test data).
    metrics = evaluate_model(pipeline, X_test, y_test, threshold=threshold)

    print('\n' + '=' * 50)
    print('  FINAL EVALUATION  (test set — first and only use)')
    print('=' * 50)
    print(f"Threshold:              {metrics['threshold']}")
    print(f"Accuracy:               {metrics['accuracy']:.4f}")
    print(f"Precision (class 1):    {metrics['precision']:.4f}")
    print(f"Recall    (class 1):    {metrics['recall']:.4f}")
    print(f"F1-score  (class 1):    {metrics['f1']:.4f}")

    cm = metrics['confusion_matrix']
    print(f"\nConfusion Matrix:")
    print(f"                 Predicted 0   Predicted 1")
    print(f"  Actual 0       {cm[0][0]:>10,}   {cm[0][1]:>10,}")
    print(f"  Actual 1       {cm[1][0]:>10,}   {cm[1][1]:>10,}")

    print(f"\nClassification Report:")
    print(pd.DataFrame(metrics['classification_report']).transpose()
            .to_string())
    print(f"\nTest-set class distribution: "
          f"{metrics['class_distribution_test']}")

    # 10. Save the fitted pipeline + threshold
    save_pipeline(pipeline, threshold)
    print(f'\n✓ Pipeline saved to {MODEL_PATH}')

    # 11. Verify persistence: reload and predict on a sample.
    #     Drop target-derived columns before calling predict().
    sample_raw = raw_df.head(5).drop(
        columns=['Profit_Amount', 'Profit_Margin_Percent'],
        errors='ignore',
    )
    sample_preds = predict(sample_raw)
    print(f'\nPersistence check — sample predictions: {sample_preds.tolist()}')
    print('✓ Saved pipeline loads and predicts successfully.')

    # Return for programmatic consumers
    metrics['features_used']     = all_features
    metrics['features_excluded'] = dropped
    metrics['train_count']       = len(y_train)
    metrics['test_count']        = len(y_test)
    return metrics


if __name__ == '__main__':
    train_and_evaluate()

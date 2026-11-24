"""Quick validation of the loss_detection dashboard integration."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

# 1. Import test
from ui.loss_detection import render_loss_detection
from backend.loss_detector import (
    load_data, add_target, load_pipeline, _EXCLUDED_COLUMNS,
    LOW_MARGIN_THRESHOLD, evaluate_model, split_data,
)
print("All imports OK")

# 2. Model loads
pipeline, threshold = load_pipeline()
print(f"Pipeline loaded OK, threshold = {threshold}")

# 3. Predictions
import pandas as pd
raw_df = load_data()
df = add_target(raw_df)
drop_cols = [c for c in _EXCLUDED_COLUMNS if c in df.columns]
feature_df = df.drop(columns=drop_cols, errors="ignore")
proba = pipeline.predict_proba(feature_df)[:, 1]
preds = (proba >= threshold).astype(int)
print(f"Predictions computed: {preds.sum()} low-margin out of {len(preds)}")

# 4. Eval metrics
y = df["Is_Low_Margin"]
_, X_test, _, y_test = split_data(df, y)
metrics = evaluate_model(pipeline, X_test, y_test, threshold=threshold)
print(f"Accuracy:  {metrics['accuracy']:.4f}")
print(f"Precision: {metrics['precision']:.4f}")
print(f"Recall:    {metrics['recall']:.4f}")
print(f"F1-score:  {metrics['f1']:.4f}")
print(f"Confusion: {metrics['confusion_matrix']}")

# 5. Verify app.py has the route
with open("app.py", "r") as f:
    app_src = f.read()
assert "render_loss_detection" in app_src, "render_loss_detection not in app.py!"
assert "Profitability Risk Detection" in app_src, "Nav entry missing in app.py!"
print("app.py integration verified")

print("\nALL CHECKS PASSED")

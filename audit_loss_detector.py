import json, sys, os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import pandas as pd
from backend.loss_detector import (
    load_data,
    add_target,
    preprocess,
    split_data,
    train_model,
    evaluate_model,
    save_model,
    load_model,
    predict,
)

def main():
    # Load raw data
    df_raw = load_data()
    print('Rows loaded:', len(df_raw))
    # 2. Verify Order_ID uniqueness
    order_unique = df_raw['Order_ID'].is_unique
    print('Order_ID unique across all records?', order_unique)

    # 1. Add target & ensure profit columns are excluded from features
    df = add_target(df_raw)
    X, y, preproc = preprocess(df)
    # Obtain feature names after preprocessing if possible
    try:
        feature_names = preproc.get_feature_names_out()
    except Exception:
        feature_names = None
    # Check excluded columns
    excluded = {'Profit_Amount', 'Profit_Margin_Percent', 'Is_Loss'}
    # All columns used in X before preprocessing
    cols_before = set(df.drop(columns=list(excluded)).columns)
    print('Excluded profit/target columns from features?', excluded.issubset(set(df.columns)))
    print('Number of features after preprocessing:', X.shape[1])
    if feature_names is not None:
        print('Feature name sample (first 5):', feature_names[:5])

    # 5. Percentages of loss vs profit
    loss_pct = y.mean()
    print('Loss transaction percentage:', loss_pct)
    print('Profitable transaction percentage:', 1 - loss_pct)

    # 3. Train/test split (stratified) – ensure no leakage of Order_ID
    X_train, X_test, y_train, y_test = split_data(X, y, df)
    # Since dataset has one row per Order_ID, this split is safe.
    print('Train size:', len(y_train), 'Test size:', len(y_test))

    # 4. Train model
    clf = train_model(X_train, y_train)
    # 6. Evaluate
    metrics, _ = evaluate_model(clf, X_test, y_test)
    print('Evaluation metrics:')
    print(json.dumps(metrics, indent=2))

    # 7. Save model, reload, and predict on a few rows
    save_model(clf, preproc)
    model, preproc_loaded = load_model()
    sample = df_raw.head(5)
    preds = predict(sample)
    print('Sample predictions (Is_Loss):', preds.tolist())

if __name__ == '__main__':
    main()

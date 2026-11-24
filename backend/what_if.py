import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score


def train_profit_model(df):
    """
    Train a Random Forest model to predict Profit_Amount.
    """

    features = [
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
    ]

    target = "Profit_Amount"

    # Select features and target
    data = df[features + [target]].copy()

    # Convert categorical columns into numbers
    data = pd.get_dummies(data, drop_first=True)

    X = data.drop(columns=[target])
    y = data[target]

    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42
    )

    # Create and train the model
    model = RandomForestRegressor(
        n_estimators=100,
        random_state=42
    )

    model.fit(X_train, y_train)

    # Make predictions
    predictions = model.predict(X_test)

    # Evaluate the model
    mae = mean_absolute_error(y_test, predictions)
    r2 = r2_score(y_test, predictions)

    return model, mae, r2, X.columns


def predict_profit(model, feature_columns, order_data):
    """
    Predict Profit_Amount for a single order.
    """
    # Accept one order as a dictionary or pandas DataFrame
    if isinstance(order_data, pd.DataFrame):
        order_df = order_data.copy()
    elif isinstance(order_data, pd.Series):
        order_df = pd.DataFrame([order_data])
    else:
        order_df = pd.DataFrame([order_data])

    # Apply one-hot encoding for categorical variables
    encoded_df = pd.get_dummies(order_df)

    # Ensure resulting columns match feature_columns
    encoded_df = encoded_df.reindex(columns=feature_columns, fill_value=0)

    # Return predicted Profit_Amount as a float
    prediction = model.predict(encoded_df)
    return float(prediction[0])


def _safe_numeric(value, default=0.0):
    """
    Safely convert a value (scalar, Series, string, etc.) to float.
    """
    if value is None:
        return default
    if isinstance(value, (pd.Series, list, tuple)):
        if len(value) == 0:
            return default
        value = value[0] if isinstance(value, (list, tuple)) else value.iloc[0]
        if value is None:
            return default
    if pd.isna(value):
        return default
    if isinstance(value, (int, float)):
        return float(value)
    try:
        cleaned = str(value).replace("$", "").replace(",", "").strip()
        return float(cleaned)
    except (ValueError, TypeError):
        return default


def _get_field(order, key, default=0.0):
    """
    Retrieve a field from order_data regardless of whether it is a DataFrame, Series, or dict.
    """
    if isinstance(order, pd.DataFrame):
        return order[key] if key in order.columns else default
    elif isinstance(order, pd.Series):
        return order[key] if key in order.index else default
    elif isinstance(order, dict):
        return order.get(key, default)
    try:
        return order[key]
    except Exception:
        return default


def simulate_discount(model, feature_columns, order_data, discount_values):
    """
    Simulate predicted Profit_Amount across various discount percentages for an order.
    Recalculates Discount_Amount and Order_Amount according to the verified financial relationship:
        Base_Amount = Unit_Price * Quantity
        Discount_Amount = Base_Amount * (Discount_Percent / 100)
        Order_Amount = Base_Amount - Discount_Amount + Shipping_Cost + Tax_Amount
    """
    results = []

    for discount in discount_values:
        # 1. Copy the original order
        if isinstance(order_data, pd.DataFrame):
            scenario_order = order_data.copy()
        elif isinstance(order_data, pd.Series):
            scenario_order = order_data.copy()
        else:
            scenario_order = dict(order_data)

        # 2. Set Discount_Percent to the simulated value
        scenario_order["Discount_Percent"] = discount

        # Safely extract and convert numeric values
        unit_price = _safe_numeric(_get_field(scenario_order, "Unit_Price"))
        quantity = _safe_numeric(_get_field(scenario_order, "Quantity"))
        shipping_cost = _safe_numeric(_get_field(scenario_order, "Shipping_Cost"))
        tax_amount = _safe_numeric(_get_field(scenario_order, "Tax_Amount"))

        # 3. Calculate Base_Amount
        base_amount = unit_price * quantity

        # 4. Recalculate Discount_Amount
        discount_val = _safe_numeric(discount)
        discount_amount = base_amount * (discount_val / 100.0)

        # 5. Recalculate Order_Amount
        order_amount = base_amount - discount_amount + shipping_cost + tax_amount

        # Update scenario order with recalculated numeric fields
        scenario_order["Unit_Price"] = unit_price
        scenario_order["Quantity"] = quantity
        scenario_order["Shipping_Cost"] = shipping_cost
        scenario_order["Tax_Amount"] = tax_amount
        scenario_order["Discount_Amount"] = discount_amount
        scenario_order["Order_Amount"] = order_amount

        # 6. Pass this modified order to predict_profit()
        predicted_profit = predict_profit(model, feature_columns, scenario_order)

        # 7. Collect results
        results.append({
            "Discount_Percent": discount,
            "Discount_Amount": discount_amount,
            "Order_Amount": order_amount,
            "Predicted_Profit": predicted_profit
        })

    return pd.DataFrame(
        results,
        columns=["Discount_Percent", "Discount_Amount", "Order_Amount", "Predicted_Profit"]
    )

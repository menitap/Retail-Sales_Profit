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
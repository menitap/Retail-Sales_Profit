"""
Analytics and Aggregation Backend Module.
Provides high-performance analytical functions for E-Commerce Sales and Profitability Analysis.
All results are computed directly from data/ecommerce_orders_dataset.csv via the backend engine.

Column aliases used throughout (set by spark_engine._clean_data):
  Sales          = Order_Amount
  Profit         = Profit_Amount
  Discount       = Discount_Percent / 100  (fractional)
  Category       = Product_Category
  Sub-Category   = Product_Subcategory
  Region         = Warehouse_Region
  Segment        = Customer_Segment
  Order ID       = Order_ID (str)
  Order Year     = Year
  Order Month    = Month
  Order Month Name = calendar month abbreviation
  Order Year-Month = "YYYY-MM"
  Profit Margin  = Profit_Margin_Percent
  State          = Country
  Ship Mode      = Shipping_Method
  Days to Ship   = Delivery_Days
"""

import pandas as pd
import numpy as np
from backend.spark_engine import get_engine


def get_kpi_summary(df=None):
    """Computes headline KPIs from the e-commerce dataset."""
    if df is None:
        df = get_engine().get_cleaned_data()

    total_sales = float(df["Sales"].sum())
    total_profit = float(df["Profit"].sum())
    total_orders = int(df["Order ID"].nunique())
    total_items = int(df["Quantity"].sum())
    avg_discount = float(df["Discount_Percent"].mean())   # already a percentage (0-40)
    profit_margin = float((total_profit / total_sales) * 100) if total_sales > 0 else 0.0

    loss_records = df[df["Profit"] < 0]
    total_loss = float(loss_records["Profit"].sum())
    loss_orders_pct = float((len(loss_records) / len(df)) * 100) if len(df) > 0 else 0.0
    avg_order_value = float(total_sales / total_orders) if total_orders > 0 else 0.0

    # E-commerce specific extras
    avg_rating = float(df["Review_Rating"].mean()) if "Review_Rating" in df.columns else 0.0
    return_rate = float((df["Returned"].str.upper() == "YES").mean() * 100) if "Returned" in df.columns else 0.0

    return {
        "total_sales": total_sales,
        "total_profit": total_profit,
        "total_orders": total_orders,
        "total_items": total_items,
        "avg_discount": avg_discount,
        "profit_margin": profit_margin,
        "total_loss": total_loss,
        "loss_orders_pct": loss_orders_pct,
        "avg_order_value": avg_order_value,
        "avg_rating": avg_rating,
        "return_rate": return_rate
    }


def get_category_analysis(df=None):
    """Calculates sales, profit, and margins grouped by Product_Category."""
    if df is None:
        df = get_engine().get_cleaned_data()

    agg = df.groupby("Category").agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Quantity=("Quantity", "sum"),
        Order_Count=("Order ID", "nunique"),
        Avg_Discount=("Discount_Percent", "mean")
    ).reset_index()

    total_sales = agg["Sales"].sum()
    total_profit = agg["Profit"].sum()
    agg["Profit_Margin"] = np.where(agg["Sales"] > 0, (agg["Profit"] / agg["Sales"]) * 100, 0.0)
    agg["Sales_Share"] = (agg["Sales"] / total_sales) * 100 if total_sales > 0 else 0.0
    agg["Profit_Share"] = np.where(total_profit != 0, (agg["Profit"] / total_profit) * 100, 0.0)
    return agg.sort_values(by="Sales", ascending=False)


def get_subcategory_analysis(df=None):
    """Calculates detailed metrics for each Product_Subcategory."""
    if df is None:
        df = get_engine().get_cleaned_data()

    agg = df.groupby(["Category", "Sub-Category"]).agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Quantity=("Quantity", "sum"),
        Order_Count=("Order ID", "nunique"),
        Avg_Discount=("Discount_Percent", "mean"),
        Loss_Records=("Profit", lambda x: (x < 0).sum())
    ).reset_index()

    agg["Profit_Margin"] = np.where(agg["Sales"] > 0, (agg["Profit"] / agg["Sales"]) * 100, 0.0)
    agg["Is_Profitable"] = agg["Profit"] >= 0
    return agg.sort_values(by="Profit", ascending=False)


def get_regional_analysis(df=None):
    """Aggregates sales and profitability across Warehouse_Regions."""
    if df is None:
        df = get_engine().get_cleaned_data()

    reg_agg = df.groupby("Region").agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Quantity=("Quantity", "sum"),
        Orders=("Order ID", "nunique"),
        Avg_Discount=("Discount_Percent", "mean")
    ).reset_index()

    reg_agg["Profit_Margin"] = np.where(reg_agg["Sales"] > 0, (reg_agg["Profit"] / reg_agg["Sales"]) * 100, 0.0)
    return reg_agg.sort_values(by="Sales", ascending=False)


def get_state_analysis(df=None, top_n=10):
    """Country-level (aliased as State) sales and profitability rankings."""
    if df is None:
        df = get_engine().get_cleaned_data()

    state_agg = df.groupby(["State", "Region"]).agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Orders=("Order ID", "nunique")
    ).reset_index()

    state_agg["Profit_Margin"] = np.where(state_agg["Sales"] > 0, (state_agg["Profit"] / state_agg["Sales"]) * 100, 0.0)
    top_states = state_agg.sort_values(by="Profit", ascending=False).head(top_n)
    bottom_states = state_agg.sort_values(by="Profit", ascending=True).head(top_n)
    return state_agg, top_states, bottom_states


def get_segment_analysis(df=None):
    """Customer segment analysis (Loyal, Premium, Returning, New)."""
    if df is None:
        df = get_engine().get_cleaned_data()

    seg_agg = df.groupby("Segment").agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Quantity=("Quantity", "sum"),
        Orders=("Order ID", "nunique"),
        Avg_Discount=("Discount_Percent", "mean")
    ).reset_index()

    seg_agg["Profit_Margin"] = np.where(seg_agg["Sales"] > 0, (seg_agg["Profit"] / seg_agg["Sales"]) * 100, 0.0)
    seg_agg["Avg_Sales_Per_Order"] = np.where(seg_agg["Orders"] > 0, seg_agg["Sales"] / seg_agg["Orders"], 0.0)
    return seg_agg.sort_values(by="Sales", ascending=False)


def get_discount_brackets(df=None):
    """Binned discount analysis to evaluate profit erosion at discount tiers.
    Discount_Percent is an integer 0-40 in this dataset."""
    if df is None:
        df = get_engine().get_cleaned_data()

    # Use Discount (fractional) which was derived from Discount_Percent/100
    bins = [-0.01, 0.0, 0.10, 0.20, 0.30, 0.40, 0.50, 1.0]
    labels = ["0% (No Discount)", "1% - 10%", "11% - 20%", "21% - 30%", "31% - 40%", "41% - 50%", "> 50% High Discount"]

    temp = df.copy()
    temp["Discount_Bracket"] = pd.cut(temp["Discount"], bins=bins, labels=labels)

    agg = temp.groupby("Discount_Bracket", observed=False).agg(
        Order_Lines=("Order ID", "count"),
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Avg_Profit_Per_Order=("Profit", "mean"),
        Loss_Count=("Profit", lambda x: (x < 0).sum())
    ).reset_index()

    agg["Profit_Margin"] = np.where(agg["Sales"] > 0, (agg["Profit"] / agg["Sales"]) * 100, 0.0)
    agg["Loss_Rate_Pct"] = np.where(agg["Order_Lines"] > 0, (agg["Loss_Count"] / agg["Order_Lines"]) * 100, 0.0)
    return agg


def get_time_series_analysis(df=None):
    """Computes monthly and yearly trends, plus YoY metrics."""
    if df is None:
        df = get_engine().get_cleaned_data()

    # Monthly aggregation
    monthly = df.groupby("Order Year-Month").agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Orders=("Order ID", "nunique"),
        Quantity=("Quantity", "sum")
    ).reset_index()
    monthly["Profit_Margin"] = np.where(monthly["Sales"] > 0, (monthly["Profit"] / monthly["Sales"]) * 100, 0.0)
    monthly["Order Date"] = pd.to_datetime(monthly["Order Year-Month"])
    monthly = monthly.sort_values(by="Order Date")

    # Yearly aggregation
    yearly = df.groupby("Order Year").agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Orders=("Order ID", "nunique"),
        Quantity=("Quantity", "sum")
    ).reset_index()
    yearly["Profit_Margin"] = np.where(yearly["Sales"] > 0, (yearly["Profit"] / yearly["Sales"]) * 100, 0.0)
    yearly["Sales_YoY_Growth"] = yearly["Sales"].pct_change() * 100
    yearly["Profit_YoY_Growth"] = yearly["Profit"].pct_change() * 100

    # Seasonality heatmap (Year x Month Name)
    month_order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    season_sales = df.pivot_table(
        index="Order Year", columns="Order Month Name",
        values="Sales", aggfunc="sum"
    ).reindex(columns=month_order)
    season_profit = df.pivot_table(
        index="Order Year", columns="Order Month Name",
        values="Profit", aggfunc="sum"
    ).reindex(columns=month_order)

    return monthly, yearly, season_sales, season_profit


def get_dataset_schema_summary():
    """Generates schema metadata for Data Overview page."""
    engine = get_engine()
    raw = engine.get_raw_data()
    clean = engine.get_cleaned_data()

    # Columns to show (original dataset columns only, not derived aliases)
    original_cols = [c for c in raw.columns]

    # Spark type mapping for e-commerce dataset
    type_map = {
        "Order_ID": "LongType",
        "Customer_ID": "StringType",
        "Order_Date": "DateType / TimestampType",
        "Year": "IntegerType",
        "Month": "IntegerType",
        "Day": "IntegerType",
        "Day_Of_Week": "StringType",
        "Quarter": "IntegerType",
        "Customer_Age": "IntegerType",
        "Customer_Gender": "StringType",
        "Country": "StringType",
        "City": "StringType",
        "Customer_Segment": "StringType",
        "Product_ID": "StringType",
        "Product_Category": "StringType",
        "Product_Subcategory": "StringType",
        "Brand": "StringType",
        "Unit_Price": "DoubleType",
        "Quantity": "IntegerType",
        "Discount_Percent": "IntegerType",
        "Discount_Amount": "DoubleType",
        "Coupon_Used": "StringType",
        "Shipping_Cost": "DoubleType",
        "Tax_Amount": "DoubleType",
        "Order_Amount": "DoubleType",
        "Payment_Method": "StringType",
        "Device_Type": "StringType",
        "Traffic_Source": "StringType",
        "Membership_Status": "StringType",
        "Shipping_Method": "StringType",
        "Warehouse_Region": "StringType",
        "Delivery_Days": "IntegerType",
        "Order_Status": "StringType",
        "Returned": "StringType",
        "Review_Rating": "DoubleType",
        "Customer_Lifetime_Value": "DoubleType",
        "Profit_Margin_Percent": "DoubleType",
        "Profit_Amount": "DoubleType",
        "Season": "StringType",
        "Holiday_Season": "StringType",
        "High_Value_Order": "StringType"
    }

    schema_rows = []
    for col in original_cols:
        null_count = int(raw[col].isnull().sum())
        unique_count = int(raw[col].nunique())
        sample_val = str(raw[col].dropna().iloc[0]) if len(raw[col].dropna()) > 0 else "None"
        spark_type = type_map.get(col, "StringType")
        pandas_dtype = str(raw[col].dtype)

        schema_rows.append({
            "Column Name": col,
            "Spark Schema Type": spark_type,
            "Pandas Dtype": pandas_dtype,
            "Null Count": null_count,
            "Unique Values": unique_count,
            "Sample Value": sample_val
        })

    return pd.DataFrame(schema_rows)

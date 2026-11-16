"""
Analytics and Aggregation Backend Module.
Provides high-performance analytical functions for Retail Sales and Profitability Analysis.
All results are computed directly from the dataset processed by the backend engine.
"""

import pandas as pd
import numpy as np
from backend.spark_engine import get_engine

def get_kpi_summary(df=None):
    """Computes headline KPIs from the dataset."""
    if df is None:
        df = get_engine().get_cleaned_data()

    total_sales = float(df["Sales"].sum())
    total_profit = float(df["Profit"].sum())
    total_orders = int(df["Order ID"].nunique())
    total_items = int(df["Quantity"].sum())
    avg_discount = float(df["Discount"].mean() * 100)
    profit_margin = float((total_profit / total_sales) * 100) if total_sales > 0 else 0.0

    loss_records = df[df["Profit"] < 0]
    total_loss = float(loss_records["Profit"].sum())
    loss_orders_pct = float((len(loss_records) / len(df)) * 100) if len(df) > 0 else 0.0
    avg_order_value = float(total_sales / total_orders) if total_orders > 0 else 0.0

    return {
        "total_sales": total_sales,
        "total_profit": total_profit,
        "total_orders": total_orders,
        "total_items": total_items,
        "avg_discount": avg_discount,
        "profit_margin": profit_margin,
        "total_loss": total_loss,
        "loss_orders_pct": loss_orders_pct,
        "avg_order_value": avg_order_value
    }

def get_category_analysis(df=None):
    """Calculates sales, profit, and margins grouped by Category."""
    if df is None:
        df = get_engine().get_cleaned_data()

    agg = df.groupby("Category").agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Quantity=("Quantity", "sum"),
        Order_Count=("Order ID", "nunique"),
        Avg_Discount=("Discount", lambda x: x.mean() * 100)
    ).reset_index()

    agg["Profit_Margin"] = (agg["Profit"] / agg["Sales"]) * 100
    agg["Sales_Share"] = (agg["Sales"] / agg["Sales"].sum()) * 100
    agg["Profit_Share"] = (agg["Profit"] / agg["Profit"].sum()) * 100
    return agg.sort_values(by="Sales", ascending=False)

def get_subcategory_analysis(df=None):
    """Calculates detailed metrics for each of the 17 Sub-Categories."""
    if df is None:
        df = get_engine().get_cleaned_data()

    agg = df.groupby(["Category", "Sub-Category"]).agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Quantity=("Quantity", "sum"),
        Order_Count=("Order ID", "nunique"),
        Avg_Discount=("Discount", lambda x: x.mean() * 100),
        Loss_Records=("Profit", lambda x: (x < 0).sum())
    ).reset_index()

    agg["Profit_Margin"] = (agg["Profit"] / agg["Sales"]) * 100
    agg["Is_Profitable"] = agg["Profit"] >= 0
    return agg.sort_values(by="Profit", ascending=False)

def get_regional_analysis(df=None):
    """Aggregates sales and profitability across geographical regions."""
    if df is None:
        df = get_engine().get_cleaned_data()

    reg_agg = df.groupby("Region").agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Quantity=("Quantity", "sum"),
        Orders=("Order ID", "nunique"),
        Avg_Discount=("Discount", lambda x: x.mean() * 100)
    ).reset_index()

    reg_agg["Profit_Margin"] = (reg_agg["Profit"] / reg_agg["Sales"]) * 100
    return reg_agg.sort_values(by="Sales", ascending=False)

def get_state_analysis(df=None, top_n=10):
    """State-level sales and profitability rankings."""
    if df is None:
        df = get_engine().get_cleaned_data()

    state_agg = df.groupby(["State", "Region"]).agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Orders=("Order ID", "nunique")
    ).reset_index()

    state_agg["Profit_Margin"] = (state_agg["Profit"] / state_agg["Sales"]) * 100
    top_states = state_agg.sort_values(by="Profit", ascending=False).head(top_n)
    bottom_states = state_agg.sort_values(by="Profit", ascending=True).head(top_n)
    return state_agg, top_states, bottom_states

def get_segment_analysis(df=None):
    """Customer segment analysis (Consumer, Corporate, Home Office)."""
    if df is None:
        df = get_engine().get_cleaned_data()

    seg_agg = df.groupby("Segment").agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Quantity=("Quantity", "sum"),
        Orders=("Order ID", "nunique"),
        Avg_Discount=("Discount", lambda x: x.mean() * 100)
    ).reset_index()

    seg_agg["Profit_Margin"] = (seg_agg["Profit"] / seg_agg["Sales"]) * 100
    seg_agg["Avg_Sales_Per_Order"] = seg_agg["Sales"] / seg_agg["Orders"]
    return seg_agg.sort_values(by="Sales", ascending=False)

def get_discount_brackets(df=None):
    """Binned discount analysis to evaluate profit erosion at discount tiers."""
    if df is None:
        df = get_engine().get_cleaned_data()

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

    agg["Profit_Margin"] = (agg["Profit"] / agg["Sales"]) * 100
    agg["Loss_Rate_Pct"] = (agg["Loss_Count"] / agg["Order_Lines"]) * 100
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
    monthly["Profit_Margin"] = (monthly["Profit"] / monthly["Sales"]) * 100
    monthly["Order Date"] = pd.to_datetime(monthly["Order Year-Month"])
    monthly = monthly.sort_values(by="Order Date")

    # Yearly aggregation
    yearly = df.groupby("Order Year").agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Orders=("Order ID", "nunique"),
        Quantity=("Quantity", "sum")
    ).reset_index()
    yearly["Profit_Margin"] = (yearly["Profit"] / yearly["Sales"]) * 100
    yearly["Sales_YoY_Growth"] = yearly["Sales"].pct_change() * 100
    yearly["Profit_YoY_Growth"] = yearly["Profit"].pct_change() * 100

    # Seasonality heatmap table (Year x Month Name)
    month_order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    season_sales = df.pivot_table(index="Order Year", columns="Order Month Name", values="Sales", aggfunc="sum").reindex(columns=month_order)
    season_profit = df.pivot_table(index="Order Year", columns="Order Month Name", values="Profit", aggfunc="sum").reindex(columns=month_order)

    return monthly, yearly, season_sales, season_profit

def get_dataset_schema_summary():
    """Generates schema metadata for Data Overview."""
    engine = get_engine()
    raw = engine.get_raw_data()
    clean = engine.get_cleaned_data()

    schema_rows = []
    for col in raw.columns:
        clean_dtype = str(clean[col].dtype) if col in clean.columns else "N/A"
        null_count = int(raw[col].isnull().sum())
        unique_count = int(raw[col].nunique())
        sample_val = str(raw[col].dropna().iloc[0]) if len(raw[col].dropna()) > 0 else "None"
        
        # Categorize column type for Spark
        if "Date" in col:
            spark_type = "DateType / TimestampType"
        elif col in ["Sales", "Profit", "Discount"]:
            spark_type = "DoubleType"
        elif col in ["Quantity", "Row ID"]:
            spark_type = "IntegerType"
        else:
            spark_type = "StringType"

        schema_rows.append({
            "Column Name": col,
            "Spark Schema Type": spark_type,
            "Pandas Dtype": clean_dtype,
            "Null Count": null_count,
            "Unique Values": unique_count,
            "Sample Value": sample_val
        })

    return pd.DataFrame(schema_rows)

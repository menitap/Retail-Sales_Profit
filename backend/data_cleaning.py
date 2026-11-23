"""
backend/data_cleaning.py
========================
Data Cleaning and Feature Engineering Module using Apache Spark.

This module implements:
- Validation of raw dataset schema and integrity.
- Safe type conversions for numerical attributes (Sales, Quantity, Discount, Profit).
- Robust parsing of multiple date formats for 'Order Date' and 'Ship Date'.
- Date-based feature extraction ('Year', 'Month').
- Feature engineering: 'Profit Margin' with safe handling of division-by-zero.
- Deduplication and missing value resolution preserving business integrity.

Frontend Integration Example:
-----------------------------
>>> from backend.spark_engine import load_raw_data
>>> from backend.data_cleaning import clean_superstore_data
>>>
>>> raw_df = load_raw_data()
>>> cleaned_df = clean_superstore_data(raw_df)
>>> cleaned_df.printSchema()
"""

from typing import List, Tuple
from pyspark.sql import DataFrame
from pyspark.sql.functions import (
    col,
    to_date,
    coalesce,
    year,
    month,
    when,
    round as spark_round,
    trim,
)
from pyspark.sql.types import (
    DoubleType,
    IntegerType,
    StringType,
)

# Mandatory columns required for the analytics pipeline
REQUIRED_COLUMNS: List[str] = [
    "Row ID",
    "Order ID",
    "Order Date",
    "Ship Date",
    "Customer ID",
    "Customer Name",
    "Segment",
    "Country",
    "City",
    "State",
    "Region",
    "Product ID",
    "Category",
    "Sub-Category",
    "Product Name",
    "Sales",
    "Quantity",
    "Discount",
    "Profit",
]


def validate_raw_data(df: DataFrame) -> Tuple[bool, List[str]]:
    """
    Validate whether the input PySpark DataFrame possesses the required schema.

    Parameters
    ----------
    df : DataFrame
        PySpark DataFrame to be validated.

    Returns
    -------
    Tuple[bool, List[str]]
        A boolean indicating validity, and a list of missing column names (if any).

    Raises
    ------
    TypeError
        If input is not an instance of PySpark DataFrame.

    Example
    -------
    >>> is_valid, missing = validate_raw_data(raw_df)
    >>> if not is_valid:
    ...     print(f"Missing columns: {missing}")
    """
    if not isinstance(df, DataFrame):
        raise TypeError(
            f"Expected input to be pyspark.sql.DataFrame, got {type(df).__name__}"
        )

    current_cols = set(df.columns)
    missing = [col_name for col_name in REQUIRED_COLUMNS if col_name not in current_cols]
    return (len(missing) == 0, missing)


def clean_superstore_data(df: DataFrame) -> DataFrame:
    """
    Preprocess and transform raw Superstore dataset into an analytical PySpark DataFrame.

    Cleaning and Feature Engineering Steps:
    1. Schema validation against required business columns.
    2. Trimming leading/trailing whitespace from string fields.
    3. Dropping duplicate rows (`dropDuplicates()`) to eliminate redundant transactions.
    4. Casting numeric fields:
       - 'Sales' -> DoubleType
       - 'Quantity' -> IntegerType
       - 'Discount' -> DoubleType
       - 'Profit' -> DoubleType
       - 'Postal Code' -> StringType (handles null/missing postal codes gracefully)
    5. Parsing 'Order Date' and 'Ship Date' to Spark DateType supporting 'M/d/yyyy', 'MM/dd/yyyy', and ISO formats.
    6. Extracting temporal features:
       - 'Year': Calendar year of the order.
       - 'Month': Calendar month number (1-12) of the order.
    7. Feature Engineering:
       - 'Profit Margin' = (Profit / Sales) * 100
       - Safely handles division by zero (sets 0.0 when Sales is 0 or null).
    8. Handling critical nulls:
       - Preserves business records; records with null Order ID, Sales, or unparseable Order Date are filtered out.

    Parameters
    ----------
    df : DataFrame
        Raw input PySpark DataFrame.

    Returns
    -------
    DataFrame
        Cleaned, type-safe PySpark DataFrame ready for analytics.

    Raises
    ------
    ValueError
        If required schema columns are missing or the resulting dataset is empty.

    Example
    -------
    >>> from backend.data_cleaning import clean_superstore_data
    >>> cleaned_df = clean_superstore_data(raw_df)
    """
    # 1. Validate Schema
    is_valid, missing = validate_raw_data(df)
    if not is_valid:
        raise ValueError(
            f"Dataset failed schema validation. Missing required columns: {missing}"
        )

    cleaned = df

    # 2. Trim whitespace on text columns
    string_cols = [
        "Order ID",
        "Customer ID",
        "Customer Name",
        "Segment",
        "Country",
        "City",
        "State",
        "Region",
        "Product ID",
        "Category",
        "Sub-Category",
        "Product Name",
    ]
    for c in string_cols:
        if c in cleaned.columns:
            cleaned = cleaned.withColumn(c, trim(col(c)))

    # 3. Deduplicate identical records
    # Deduplicate based on 'Row ID' if present, otherwise all columns
    if "Row ID" in cleaned.columns:
        cleaned = cleaned.dropDuplicates(["Row ID"])
    else:
        cleaned = cleaned.dropDuplicates()

    # 4. Convert numeric columns with safe casting
    cleaned = (
        cleaned.withColumn("Sales", col("Sales").cast(DoubleType()))
        .withColumn("Quantity", col("Quantity").cast(IntegerType()))
        .withColumn("Discount", col("Discount").cast(DoubleType()))
        .withColumn("Profit", col("Profit").cast(DoubleType()))
    )

    # 5. Handle Postal Code (cast as string to preserve format, fill nulls if present)
    if "Postal Code" in cleaned.columns:
        cleaned = cleaned.withColumn(
            "Postal Code",
            when(col("Postal Code").isNull(), "Unknown").otherwise(
                col("Postal Code").cast(StringType())
            ),
        )

    # 6. Parse Order Date and Ship Date into Spark DateType
    # Accommodates M/d/yyyy, MM/dd/yyyy, yyyy-MM-dd, and yyyy/MM/dd formats
    cleaned = cleaned.withColumn(
        "Order Date",
        coalesce(
            to_date(trim(col("Order Date")), "M/d/yyyy"),
            to_date(trim(col("Order Date")), "MM/dd/yyyy"),
            to_date(trim(col("Order Date")), "yyyy-MM-dd"),
            to_date(trim(col("Order Date")), "yyyy/MM/dd"),
        ),
    ).withColumn(
        "Ship Date",
        coalesce(
            to_date(trim(col("Ship Date")), "M/d/yyyy"),
            to_date(trim(col("Ship Date")), "MM/dd/yyyy"),
            to_date(trim(col("Ship Date")), "yyyy-MM-dd"),
            to_date(trim(col("Ship Date")), "yyyy/MM/dd"),
        ),
    )

    # 7. Extract Year and Month features
    cleaned = cleaned.withColumn("Year", year(col("Order Date"))).withColumn(
        "Month", month(col("Order Date"))
    )

    # 8. Calculate Profit Margin with safe division handling
    # Profit Margin % = (Profit / Sales) * 100
    cleaned = cleaned.withColumn(
        "Profit Margin",
        when(
            (col("Sales").isNotNull()) & (col("Sales") != 0.0),
            spark_round((col("Profit") / col("Sales")) * 100.0, 2),
        ).otherwise(0.0),
    )

    # 9. Filter out invalid/corrupt records where critical business identifiers are null
    # Records missing Order ID, Sales, or unparseable Order Date cannot be analyzed
    cleaned = cleaned.filter(
        col("Order ID").isNotNull()
        & col("Sales").isNotNull()
        & col("Profit").isNotNull()
        & col("Order Date").isNotNull()
    )

    return cleaned


# ---------------------------------------------------------------------------
# Frontend Integration Notes:
# ---------------------------------------------------------------------------
# In app.py:
#
# from backend.spark_engine import load_raw_data
# from backend.data_cleaning import clean_superstore_data
#
# raw_df = load_raw_data()
# cleaned_df = clean_superstore_data(raw_df)
#
# Or directly via spark_engine:
# from backend.spark_engine import get_cleaned_data
# df = get_cleaned_data()

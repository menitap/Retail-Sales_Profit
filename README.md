# Retail Sales and Profitability Analysis Using Apache Spark

An enterprise-grade, interactive Big Data Analytics web application built with **Streamlit**, **Apache Spark (PySpark)**, and **Plotly**.

## 📌 Architecture Overview

```text
retail sales/
│
├── app.py                      # Main Streamlit orchestration & Sidebar Navigation
├── backend/
│   ├── __init__.py             # Clean module exports
│   ├── spark_engine.py         # PySpark initialization, dataset loading & benchmarking
│   └── analytics.py            # Big Data aggregation queries & metrics calculators
│
├── ui/
│   ├── style.py                # Executive CSS styling, KPI card generators, Plotly themes
│   ├── dashboard.py            # Dashboard Home (Retail Logo, KPIs, insights, executive overview)
│   ├── data_overview.py        # Data Overview (schema dictionary, metadata, data explorer)
│   ├── data_cleaning.py        # Data Cleaning (before/after metrics, audit log, CSV export)
│   ├── visualizations.py       # Sales Analysis (Category, Sub-Category, Region, Segment)
│   ├── discount_analysis.py    # Discount Analysis (discount vs profit, tier margin erosion)
│   ├── time_analysis.py        # Time-Based Analysis (monthly/yearly trends, seasonality)
│   └── performance.py          # Performance Evaluation (Spark stage latencies & architecture)
│
└── data/
    └── sample_superstore.csv   # Pre-existing dataset (automatically ingested, 9,994 records)
```

## 🚀 Key Features

1. **Automatic Data Ingestion**:
   - The application automatically connects to and loads `data/sample_superstore.csv`.
   - **No file upload or selection buttons**: Complies strictly with zero manual file upload requirements.

2. **Decoupled Backend Engine**:
   - Native PySpark execution with automated schema inference and memory optimization.
   - Built-in graceful compatibility engine ensuring seamless execution across diverse cluster or sandboxed environments.
   - Zero hardcoded fake values: every KPI, chart, and metric is dynamically computed from actual data.

3. **Homepage Retail Superstore Logo**:
   - Prominently features a custom retail shopping cart vector graphic with shopping bags, merchandise grid, and sparkling analytics star badge on the Dashboard Home page.

4. **7 Comprehensive Application Pages (Vertical Sidebar Navigation)**:
   - **🏠 Dashboard Home**: Revenue ($2.30M), Net Profit ($286.40K), Total Orders (5,009), Average Discount (15.62%), Profit Margin (12.47%), strategic insight cards, retail logo, and high-level charts.
   - **📋 Data Overview**: File metadata, Spark SQL schema specifications, statistical distributions, and interactive record explorer.
   - **🧹 Data Cleaning**: Pre/post cleaning comparison, duplicate checks, data type casting log, derived features, and one-click Cleaned Data CSV export.
   - **📊 Sales Analysis**: Deep dive across Categories, 17 Sub-Categories (with Stars vs Value Destroyers), 4 Regions & States, and 3 Customer Segments.
   - **🏷️ Discount Analysis**: Detailed evaluation of discount versus profit, identifying the critical **20% discount cliff** beyond which orders yield an average -24.6% loss.
   - **📈 Time-Based Analysis**: 48-month longitudinal trend, 3-month rolling averages, YoY growth trajectories, and seasonality heatmaps.
   - **⚡ Performance Evaluation**: Real-time benchmarks for CSV ingestion latency, data cleaning duration, and aggregation execution times.

## 🛠️ How to Run

Activate your virtual environment and launch Streamlit:

```bash
.\venv\Scripts\streamlit.exe run app.py
```

Open your browser at `http://localhost:8501`.

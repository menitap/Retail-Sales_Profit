"""
Backend package exports for Retail Sales and Profitability Analysis.
"""

from backend.spark_engine import get_engine, SparkBackendEngine
from backend.analytics import (
    get_kpi_summary,
    get_category_analysis,
    get_subcategory_analysis,
    get_regional_analysis,
    get_state_analysis,
    get_segment_analysis,
    get_discount_brackets,
    get_time_series_analysis,
    get_dataset_schema_summary
)

__all__ = [
    "get_engine",
    "SparkBackendEngine",
    "get_kpi_summary",
    "get_category_analysis",
    "get_subcategory_analysis",
    "get_regional_analysis",
    "get_state_analysis",
    "get_segment_analysis",
    "get_discount_brackets",
    "get_time_series_analysis",
    "get_dataset_schema_summary"
]

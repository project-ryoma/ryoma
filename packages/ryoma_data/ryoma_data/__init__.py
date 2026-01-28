"""Ryoma Data - Data source connectors and profiling for Ryoma AI Platform."""

__version__ = "0.1.0"

# Base classes
from ryoma_data.base import BaseDataSource

# Factory
from ryoma_data.factory import DataSourceFactory
from ryoma_data.metadata import Catalog, Column, Schema, Table
from ryoma_data.profiler import DatabaseProfiler

# SQL data sources
from ryoma_data.sql import DataSource

__all__ = [
    # Base
    "BaseDataSource",
    "DataSource",
    "Catalog",
    "Column",
    "Schema",
    "Table",
    "DatabaseProfiler",
    # Factory
    "DataSourceFactory",
]

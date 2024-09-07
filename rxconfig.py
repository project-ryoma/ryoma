import logging

import reflex as rx
from reflex.constants import LogLevel

from alembic.ddl.impl import DefaultImpl

# class AlembicDuckDBImpl(DefaultImpl):
#     """Alembic implementation for DuckDB."""
#
#     __dialect__ = "duckdb"
#

config = rx.Config(
    app_name="ryoma_lab",
    loglevel=LogLevel.INFO,
    # db_url="duckdb:///:memory:",
)

# Setup basic configuration for logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

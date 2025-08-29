"""Test that lazy imports work correctly for datasources."""

import sys
from unittest.mock import MagicMock, patch

import pytest


def test_datasource_factory_lazy_import():
    """Test that DataSourceFactory doesn't import datasource modules at import time."""
    # This import should succeed regardless of which datasources are installed
    from ryoma_ai.datasource.factory import DataSourceFactory, get_supported_datasources

    # Getting supported datasources should work
    datasources = get_supported_datasources()
    assert len(datasources) > 0

    # Test that we can create datasources when dependencies are available
    try:
        # Try to create sqlite datasource (usually available)
        sqlite_ds = DataSourceFactory.create_datasource("sqlite", ":memory:")
        assert sqlite_ds is not None
    except ImportError:
        # If sqlite isn't available, that's fine for this test
        pass

    # Mock import_module to simulate missing dependencies for a specific datasource
    with patch("ryoma_ai.datasource.factory.import_module") as mock_import:
        mock_import.side_effect = ImportError("No module named 'duckdb'")

        # Creating a duckdb datasource should fail with helpful error
        with pytest.raises(ImportError) as exc_info:
            DataSourceFactory.create_datasource("duckdb", ":memory:")

        assert "Failed to import duckdb datasource" in str(exc_info.value)
        assert "Please install required dependencies" in str(exc_info.value)


def test_cli_import_without_all_dependencies():
    """Test that CLI modules can be imported without all datasource dependencies."""
    # Remove optional dependencies from sys.modules
    optional_deps = ["duckdb", "psycopg", "snowflake", "google.cloud.bigquery"]
    original_modules = {}

    for dep in optional_deps:
        if dep in sys.modules:
            original_modules[dep] = sys.modules[dep]
            del sys.modules[dep]

    try:
        with patch.dict("sys.modules", {dep: None for dep in optional_deps}):
            # These imports should succeed even without optional dependencies
            from ryoma_ai.cli import main
            from ryoma_ai.cli.app import RyomaAI
            from ryoma_ai.cli.command_handler import CommandHandler

            # Verify imports succeeded
            assert main is not None
            assert RyomaAI is not None
            assert CommandHandler is not None
    finally:
        # Restore original modules
        for dep, module in original_modules.items():
            sys.modules[dep] = module

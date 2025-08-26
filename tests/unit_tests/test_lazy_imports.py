"""Test that lazy imports work correctly for datasources."""

import pytest
from unittest.mock import patch, MagicMock
import sys


def test_datasource_factory_lazy_import():
    """Test that DataSourceFactory doesn't import datasource modules at import time."""
    # Remove duckdb from sys.modules if it exists
    if 'duckdb' in sys.modules:
        del sys.modules['duckdb']
    
    # Mock the duckdb module to simulate it not being installed
    with patch.dict('sys.modules', {'duckdb': None}):
        # This import should succeed even without duckdb installed
        from ryoma_ai.datasource.factory import DataSourceFactory, get_supported_datasources
        
        # Getting supported datasources should work
        datasources = get_supported_datasources()
        assert len(datasources) > 0
        
        # Creating a datasource that doesn't require duckdb should work
        # (This would require sqlite to be available, but it's part of Python stdlib)
        try:
            # Try to create sqlite datasource (doesn't require external deps)
            sqlite_ds = DataSourceFactory.create_datasource('sqlite', ':memory:')
            assert sqlite_ds is not None
        except ImportError as e:
            # If sqlite module itself has issues, that's okay for this test
            if 'sqlite' not in str(e):
                raise
        
        # Creating a duckdb datasource should fail with helpful error
        with pytest.raises(ImportError) as exc_info:
            DataSourceFactory.create_datasource('duckdb', ':memory:')
        
        assert 'Failed to import duckdb datasource' in str(exc_info.value)
        assert 'Please install required dependencies' in str(exc_info.value)


def test_cli_import_without_all_dependencies():
    """Test that CLI modules can be imported without all datasource dependencies."""
    # Remove optional dependencies from sys.modules
    optional_deps = ['duckdb', 'psycopg', 'snowflake', 'google.cloud.bigquery']
    original_modules = {}
    
    for dep in optional_deps:
        if dep in sys.modules:
            original_modules[dep] = sys.modules[dep]
            del sys.modules[dep]
    
    try:
        with patch.dict('sys.modules', {dep: None for dep in optional_deps}):
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
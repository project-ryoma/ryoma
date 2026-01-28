"""Tests for CatalogService"""

from unittest.mock import Mock

import pytest
from ryoma_ai.services.catalog_service import CatalogService


class TestCatalogService:
    """Test suite for CatalogService"""

    @pytest.fixture
    def mock_indexer(self):
        """Mock catalog indexer"""
        return Mock()

    @pytest.fixture
    def mock_searcher(self):
        """Mock catalog searcher"""
        return Mock()

    @pytest.fixture
    def service(self, mock_indexer, mock_searcher):
        """CatalogService instance"""
        return CatalogService(mock_indexer, mock_searcher)

    @pytest.fixture
    def sample_datasource(self):
        """Sample datasource for testing"""
        datasource = Mock()
        datasource.id = "test_ds"
        datasource.backend = "postgres"
        return datasource

    # === Indexing Tests ===

    def test_index_datasource(self, service, mock_indexer, sample_datasource):
        """Test indexing a datasource"""
        mock_indexer.index_datasource.return_value = "catalog-123"

        result = service.index_datasource(sample_datasource, level="column")

        assert result == "catalog-123"
        mock_indexer.index_datasource.assert_called_once_with(
            datasource=sample_datasource, data_source_id="test_ds", level="column"
        )

    def test_index_datasource_with_table_level(
        self, service, mock_indexer, sample_datasource
    ):
        """Test indexing at table level"""
        mock_indexer.index_datasource.return_value = "catalog-456"

        result = service.index_datasource(sample_datasource, level="table")

        assert result == "catalog-456"
        mock_indexer.index_datasource.assert_called_once_with(
            datasource=sample_datasource, data_source_id="test_ds", level="table"
        )

    def test_index_multiple_datasources(self, service, mock_indexer):
        """Test indexing multiple datasources"""
        ds1 = Mock()
        ds1.id = "ds1"
        ds2 = Mock()
        ds2.id = "ds2"

        mock_indexer.index_datasource.side_effect = ["catalog-1", "catalog-2"]

        result = service.index_multiple_datasources([ds1, ds2], level="table")

        assert len(result) == 2
        assert result == ["catalog-1", "catalog-2"]
        assert mock_indexer.index_datasource.call_count == 2

    def test_index_multiple_datasources_with_failures(self, service, mock_indexer):
        """Test indexing multiple datasources when some fail"""
        ds1 = Mock()
        ds1.id = "ds1"
        ds2 = Mock()
        ds2.id = "ds2"
        ds3 = Mock()
        ds3.id = "ds3"

        # ds2 fails, others succeed
        mock_indexer.index_datasource.side_effect = [
            "catalog-1",
            Exception("Indexing failed"),
            "catalog-3",
        ]

        result = service.index_multiple_datasources([ds1, ds2, ds3])

        # Should return only successful catalog IDs
        assert len(result) == 2
        assert result == ["catalog-1", "catalog-3"]

    def test_validate_indexing(self, service, mock_indexer):
        """Test validating catalog indexing"""
        mock_indexer.validate_indexing.return_value = True

        result = service.validate_indexing("catalog-123")

        assert result is True
        mock_indexer.validate_indexing.assert_called_once_with("catalog-123")

    # === Search Tests ===

    def test_search_tables(self, service, mock_searcher):
        """Test searching for tables"""
        mock_results = [
            {"table_name": "customers", "description": "Customer data"},
            {"table_name": "orders", "description": "Order data"},
        ]
        mock_searcher.search_catalogs.return_value = mock_results

        result = service.search_tables("customer data", top_k=5)

        assert len(result) == 2
        assert result == mock_results
        mock_searcher.search_catalogs.assert_called_once_with(
            query="customer data", top_k=5, level="table", datasource_id=None
        )

    def test_search_tables_with_datasource_filter(self, service, mock_searcher):
        """Test searching tables with datasource filter"""
        mock_searcher.search_catalogs.return_value = []

        service.search_tables("test", datasource_id="ds-1")

        mock_searcher.search_catalogs.assert_called_once_with(
            query="test", top_k=5, level="table", datasource_id="ds-1"
        )

    def test_search_columns_without_table(self, service, mock_searcher):
        """Test searching columns across all tables"""
        mock_results = [
            {"column_name": "email", "table_name": "customers"},
            {"column_name": "email_verified", "table_name": "customers"},
        ]
        mock_searcher.search_catalogs.return_value = mock_results

        result = service.search_columns("email")

        assert len(result) == 2
        mock_searcher.search_catalogs.assert_called_once_with(
            query="email", top_k=5, level="column"
        )

    def test_search_columns_with_table(self, service, mock_searcher):
        """Test searching columns in specific table"""
        mock_searcher.get_column_suggestions.return_value = ["email", "email_verified"]

        result = service.search_columns("email", table_name="customers")

        assert len(result) == 2
        # Results are converted to dict format
        assert result[0]["column_name"] == "email"
        mock_searcher.get_column_suggestions.assert_called_once_with(
            table_name="customers", query="email", top_k=5
        )

    def test_get_table_suggestions(self, service, mock_searcher):
        """Test getting table suggestions"""
        mock_searcher.get_table_suggestions.return_value = [
            "customers",
            "customer_orders",
            "customer_reviews",
        ]

        result = service.get_table_suggestions("customer")

        assert len(result) == 3
        assert result[0] == "customers"
        mock_searcher.get_table_suggestions.assert_called_once_with("customer", 5)

    def test_get_column_suggestions(self, service, mock_searcher):
        """Test getting column suggestions"""
        mock_searcher.get_column_suggestions.return_value = [
            "email",
            "email_verified",
            "secondary_email",
        ]

        result = service.get_column_suggestions("customers", "email")

        assert len(result) == 3
        assert result[0] == "email"
        mock_searcher.get_column_suggestions.assert_called_once_with(
            table_name="customers", query="email", top_k=5
        )

    def test_search_with_custom_top_k(self, service, mock_searcher):
        """Test that custom top_k is respected"""
        mock_searcher.search_catalogs.return_value = []

        service.search_tables("test", top_k=10)

        mock_searcher.search_catalogs.assert_called_once()
        call_args = mock_searcher.search_catalogs.call_args
        assert call_args.kwargs["top_k"] == 10

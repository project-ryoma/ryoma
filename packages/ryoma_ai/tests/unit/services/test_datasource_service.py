"""Tests for DataSourceService"""

from unittest.mock import Mock

import pytest
from ryoma_ai.services.datasource_service import DataSourceService


class TestDataSourceService:
    """Test suite for DataSourceService"""

    @pytest.fixture
    def mock_repository(self):
        """Mock datasource repository"""
        return Mock()

    @pytest.fixture
    def service(self, mock_repository):
        """DataSourceService instance"""
        return DataSourceService(mock_repository)

    @pytest.fixture
    def sample_datasource(self):
        """Sample datasource for testing"""
        datasource = Mock()
        datasource.id = "test_ds"
        datasource.backend = "duckdb"
        return datasource

    def test_add_datasource(self, service, mock_repository, sample_datasource):
        """Test adding a datasource"""
        service.add_datasource(sample_datasource)

        # Should save datasource
        mock_repository.save.assert_called_once_with(sample_datasource)
        # Should set as active
        mock_repository.set_active.assert_called_once_with("test_ds")

    def test_get_active_datasource(self, service, mock_repository, sample_datasource):
        """Test getting active datasource"""
        mock_repository.get_active.return_value = sample_datasource

        result = service.get_active_datasource()

        assert result == sample_datasource
        mock_repository.get_active.assert_called_once()

    def test_get_active_datasource_raises_when_none(self, service, mock_repository):
        """Test that ValueError is raised when no active datasource"""
        mock_repository.get_active.side_effect = ValueError("No active datasource")

        with pytest.raises(ValueError):
            service.get_active_datasource()

    def test_set_active_datasource(self, service, mock_repository):
        """Test setting active datasource"""
        service.set_active_datasource("test_ds")

        mock_repository.set_active.assert_called_once_with("test_ds")

    def test_get_datasource(self, service, mock_repository, sample_datasource):
        """Test getting datasource by ID"""
        mock_repository.get_by_id.return_value = sample_datasource

        result = service.get_datasource("test_ds")

        assert result == sample_datasource
        mock_repository.get_by_id.assert_called_once_with("test_ds")

    def test_list_datasources(self, service, mock_repository, sample_datasource):
        """Test listing datasources"""
        mock_repository.list_all.return_value = [sample_datasource]

        result = service.list_datasources()

        assert len(result) == 1
        assert result[0] == sample_datasource
        mock_repository.list_all.assert_called_once()

    def test_list_datasources_empty(self, service, mock_repository):
        """Test listing when no datasources exist"""
        mock_repository.list_all.return_value = []

        result = service.list_datasources()

        assert len(result) == 0

    def test_remove_datasource(self, service, mock_repository):
        """Test removing a datasource"""
        service.remove_datasource("test_ds")

        mock_repository.delete.assert_called_once_with("test_ds")

    def test_has_active_datasource_returns_true(
        self, service, mock_repository, sample_datasource
    ):
        """Test has_active_datasource when datasource exists"""
        mock_repository.get_active.return_value = sample_datasource

        result = service.has_active_datasource()

        assert result is True

    def test_has_active_datasource_returns_false(self, service, mock_repository):
        """Test has_active_datasource when no datasource exists"""
        mock_repository.get_active.side_effect = ValueError("No active datasource")

        result = service.has_active_datasource()

        assert result is False

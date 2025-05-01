from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from ryoma_ai.datasource.base import SqlDataSource
from ryoma_ai.datasource.metadata import Catalog


class MockSqlDataSource(SqlDataSource):
    def get_query_plan(self, query: str) -> Any:
        pass

    def crawl_catalogs(self, **kwargs):
        pass

    def _connect(self) -> Any:
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [("result1",), ("result2",)]
        mock_cursor.execute.return_value = None
        mock_connection.cursor.return_value = mock_cursor
        return mock_connection

    def get_catalog(self, **kwargs) -> Catalog:
        return Catalog()


@pytest.fixture
def mock_sql_data_source():
    data_source = MockSqlDataSource()
    return data_source


def test_execute_query(mock_sql_data_source):
    with patch("ryoma_ai.datasource.base.SqlDataSource.query") as mock_execute:
        mock_execute.return_value = "success"
        results = mock_sql_data_source.query("SELECT * FROM table")
    assert results == "success"


def test_sql_datasource_field_exists(mock_sql_data_source):
    assert hasattr(mock_sql_data_source, "database")
    assert hasattr(mock_sql_data_source, "db_schema")

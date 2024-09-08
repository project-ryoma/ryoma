from typing import Any
from unittest.mock import MagicMock

import pytest
from mock import patch

from ryoma_ai.datasource.base import SqlDataSource
from ryoma_ai.datasource.metadata import Catalog


class MockSqlDataSource(SqlDataSource):
    def connect(self) -> Any:
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [("result1",), ("result2",)]
        mock_cursor.execute.return_value = None
        mock_connection.cursor.return_value = mock_cursor
        return mock_connection

    def get_metadata(self, **kwargs) -> Catalog:
        return Catalog()


@pytest.fixture
def mock_sql_data_source():
    data_source = MockSqlDataSource()
    return data_source


def test_execute_query(mock_sql_data_source):
    with patch("ryoma_ai.type.base.SqlDataSource.query") as mock_execute:
        mock_execute.return_value = "success"
        results = mock_sql_data_source.query("SELECT * FROM table")
    assert results == "success"


def test_datasource_field_exists():
    assert hasattr(SqlDataSource, "__fields__")

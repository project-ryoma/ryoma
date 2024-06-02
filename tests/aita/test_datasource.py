import pytest

from aita.datasource.postgresql import PostgreSqlDataSource


@pytest.fixture
def postgresql_datasource():
    return PostgreSqlDataSource("postgresql://localhost:5432/postgres")


def test_postgresql_datasource(postgresql_datasource):
    assert postgresql_datasource.connect() is not None

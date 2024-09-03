import pytest

from ryoma.datasource.postgresql import PostgreSqlDataSource
from sqlalchemy import create_engine


@pytest.fixture
def postgres():
    return PostgreSqlDataSource(
        user="", password="", host="localhost", port=5432, database="postgres", db_schema="public"
    )


def test_postgres_connection(postgres):
    conn = postgres.connect()
    assert conn is not None


def test_postgres_get_metadata(postgres):
    metadata = postgres.get_metadata()
    assert metadata is not None
    assert len(metadata.tables) > 0


def test_postgres_connection_string(postgres):
    conn_str = postgres.connection_string()
    engine = create_engine(conn_str)
    conn = engine.connect()
    assert conn is not None
    conn.close()

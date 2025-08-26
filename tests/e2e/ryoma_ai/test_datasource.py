import pytest
from ryoma_ai.datasource.postgres import PostgresDataSource
from sqlalchemy import create_engine


@pytest.fixture
def postgres():
    # Use environment variables for PostgreSQL connection, with defaults for local testing
    import os
    return PostgresDataSource(
        user=os.environ.get("POSTGRES_USER", "postgres"),
        password=os.environ.get("POSTGRES_PASSWORD", "postgres"),
        host=os.environ.get("POSTGRES_HOST", "localhost"),
        port=int(os.environ.get("POSTGRES_PORT", 5432)),
        database=os.environ.get("POSTGRES_DB", "postgres"),
        db_schema="public",
    )


def test_postgres_connection(postgres):
    conn = postgres.connect()
    assert conn is not None


def test_postgres_get_metadata(postgres):
    metadata = postgres.get_catalog()
    assert metadata is not None
    assert len(metadata.tables) > 0


def test_postgres_connection_string(postgres):
    conn_str = postgres.connection_string()
    engine = create_engine(conn_str)
    conn = engine.connect()
    assert conn is not None
    conn.close()

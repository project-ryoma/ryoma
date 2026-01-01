import pytest
from ryoma_data import DataSource
from sqlalchemy import create_engine


@pytest.fixture
def postgres():
    # Use environment variables for PostgreSQL connection, with defaults for local testing
    import os

    return DataSource(
        "postgres",
        user=os.environ.get("POSTGRES_USER", "postgres"),
        password=os.environ.get("POSTGRES_PASSWORD", "postgres"),
        host=os.environ.get("POSTGRES_HOST", "localhost"),
        port=int(os.environ.get("POSTGRES_PORT", 5432)),
        database=os.environ.get("POSTGRES_DB", "postgres"),
        schema="public",
    )


def test_postgres_connection(postgres):
    conn = postgres.connect()
    assert conn is not None


def test_postgres_get_metadata(postgres):
    metadata = postgres.get_catalog()
    assert metadata is not None
    assert len(metadata.tables) > 0

import pandas as pd
import pytest
from ryoma_ai.datasource.duckdb import DuckDBDataSource


@pytest.fixture
def test_pandas_df():
    return pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})


def test_query_with_register(test_pandas_df):
    data_source = DuckDBDataSource()
    data_source.register("pdf", test_pandas_df)
    query = "SELECT * FROM pdf"
    result = data_source.query(query)
    assert result.shape == test_pandas_df.shape


def test_query(test_pandas_df):
    data_source = DuckDBDataSource()
    pdf = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
    result = data_source.query("SELECT * FROM pdf", pdf=pdf)
    assert result.shape == test_pandas_df.shape

from unittest.mock import patch

import pandas as pd
import pytest
from pyspark.sql import SparkSession
from ryoma_ai.tool.pandas_tool import PandasTool
from ryoma_ai.tool.spark_tool import SparkTool
from ryoma_ai.tool.sql_tool import SqlQueryTool

from tests.unit_tests.test_datasource import MockSqlDataSource


@pytest.fixture
def pandas_dataframe():
    df = pd.DataFrame(
        {
            "year": [2020, 2022, 2019, 2021],
            "n_legs": [2, 4, 5, 100],
            "animals": ["Flamingo", "Horse", "Brittle stars", "Centipede"],
        }
    )
    return df


@pytest.fixture
def mock_sql_data_source():
    data_source = MockSqlDataSource()
    return data_source


@pytest.fixture
def pyspark_session():
    return SparkSession.builder.appName("pytest").getOrCreate()


def test_pyspark_tool(pyspark_session, pandas_dataframe):
    pyspark_tool = SparkTool()
    pyspark_tool.update_script_context(
        {"spark_session": pyspark_session, "df": pandas_dataframe}
    )
    script = """
    spark_session.createDataFrame(df).show()
    """
    result = pyspark_tool._run(script)
    assert result.success is True


def test_sql_tool(mock_sql_data_source):
    with patch("ryoma_ai.datasource.base.SqlDataSource.query") as mock_execute:
        mock_execute.return_value = "success"
        sql_tool = SqlQueryTool(datasource=mock_sql_data_source)
        query = "SELECT * FROM customers LIMIT 4"
        result, _ = sql_tool._run(query)
        assert result == "success"


def test_pandas_tool(pandas_dataframe):
    pandas_tool = PandasTool()
    pandas_tool.update_script_context({"df": pandas_dataframe})
    script = """
    df["year"] = df["year"] + 1
    df
    """
    result = pandas_tool._run(script)
    assert result.success is True
    assert result.result["year"].tolist() == [2021, 2023, 2020, 2022]

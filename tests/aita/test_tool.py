import pandas as pd
import pytest
from mock import patch
from pyspark.sql import SparkSession

from aita.tool.pyspark import PySparkTool
from aita.tool.sql import SqlQueryTool
from tests.aita.test_datasource import mock_sql_data_source


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
def pyspark_session():
    return SparkSession.builder.appName("pytest").getOrCreate()


def test_pyspark_tool(pyspark_session, pandas_dataframe):
    pyspark_tool = PySparkTool()
    pyspark_tool.update_script_context({"spark_session": pyspark_session, "df": pandas_dataframe})
    script = """
    spark_session.createDataFrame(df).show()
    """
    result = pyspark_tool._run(script)
    assert result.success is True


def test_sql_tool(mock_sql_data_source):
    with patch("aita.datasource.sql.SqlDataSource.execute") as mock_execute:
        mock_execute.return_value = "success"
        sql_tool = SqlQueryTool(datasource=mock_sql_data_source)
        query = "SELECT * FROM customers LIMIT 4"
        result = sql_tool._run(query)
        assert result == "success"

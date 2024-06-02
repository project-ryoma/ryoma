import pandas as pd
import pytest
from mock import patch
from pyspark.sql import SparkSession

from aita.datasource.sql import SqlDataSource
from aita.tool.pyspark import PySparkTool
from aita.tool.sql import SqlQueryTool


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
def sql_database() -> SqlDataSource:
    return SqlDataSource("sqlite:///data/aita.db")


@pytest.fixture
def pyspark_session():
    return SparkSession.builder.master("local").appName("aita").getOrCreate()


def test_pyspark_tool(pyspark_session, pandas_dataframe):
    pyspark_tool = PySparkTool(
        script_context={"spark_session": pyspark_session, "df": pandas_dataframe}
    )
    script = """
    spark_session.createDataFrame(df).show()
    """
    result = pyspark_tool._run(script)
    assert result.success is True


def test_sql_tool(sql_database: SqlDataSource):
    with patch("aita.datasource.base.SqlDataSource.execute") as mock_execute:
        mock_execute.return_value = "success"
        sql_tool = SqlQueryTool(datasource=sql_database)
        query = "SELECT * FROM customers LIMIT 4"
        result = sql_tool._run(query)
        assert result == "success"

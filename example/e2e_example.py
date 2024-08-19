import os

from ryoma.agent.pandas import PandasAgent
from ryoma.agent.python import PythonAgent
from ryoma.agent.sql import SqlAgent
from ryoma.datasource.postgresql import PostgreSqlDataSource
from ryoma.datasource.snowflake import SnowflakeDataSource

# Snowflake

# Snowflake connection parameters
user = os.getenv("SNOWFLAKE_USER")
password = os.getenv("SNOWFLAKE_PASSWORD")
account = os.getenv("SNOWFLAKE_ACCOUNT")
warehouse = os.getenv("SNOWFLAKE_WAREHOUSE")
role = os.getenv("SNOWFLAKE_ROLE")
database = os.getenv("SNOWFLAKE_DATABASE")
schema = os.getenv("SNOWFLAKE_SCHEMA")

# Create a SnowflakeDataSource object
snowflake_datasource = SnowflakeDataSource(
    user=user,
    password=password,
    account=account,
    warehouse=warehouse,
    role=role,
    database=database,
    schema=schema,
)

sql_agent = SqlAgent("gpt-3.5-turbo").add_datasource(snowflake_datasource)
sql_agent.stream("I want to get the top 5 customers which making the most purchases")

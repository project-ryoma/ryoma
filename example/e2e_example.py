
import os
from aita.datasource.snowflake import SnowflakeDataSource
from aita.datasource.postgresql import PostgreSqlDataSource
from aita.agent.sql import SqlAgent
from aita.agent.pandas import PandasAgent
from aita.agent.python import PythonAgent

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

sql_agent = SqlAgent("gpt-3.5-turbo") \
    .add_datasource(snowflake_datasource) \

sql_agent.chat("I want to get the top 5 customers which making the most purchases")
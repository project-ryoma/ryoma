
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
sample_sql_query = """
SELECT c_custkey, c_name, SUM(o_totalprice) AS total_purchase
FROM snowflake_sample_data.tpch_sf1.customer
JOIN snowflake_sample_data.tpch_sf1.orders
ON c_custkey = o_custkey
GROUP BY c_custkey, c_name
ORDER BY total_purchase
DESC LIMIT 10
"""

# res = snowflake_datasource.execute(sample_sql_query)
# print(res)

metadata = snowflake_datasource.get_metadata(database=database, schema=schema)
print(metadata)
from dataplatform.mysql_client import mysql_client
from dataplatform.snowflake_client import snowflake_client
from langchain.agents import Tool


def connect_mysql(url):
    return mysql_client


def connect_snowflake(url):
    return snowflake_client


def get_data_from_mysql(sql_query):
    return mysql_client.run_query(sql_query)


def get_data_from_snowflake(sql_query):
    return snowflake_client.run_query(sql_query)


tools = [
    Tool(
        name="connect_mysql",
        func=connect_mysql,
        description="Connect to mysql database"
    ),
    Tool(
        name="connect_snowflake",
        func=connect_snowflake,
        description="connect to snowflake database"
    ),
    Tool(
        name="get_data_from_mysql",
        func=get_data_from_mysql,
        description="get data from mysql database"
    ),
    Tool(
        name="get_data_from_snowflake",
        func=get_data_from_snowflake,
        description="get data from snowflake database"
    )
]

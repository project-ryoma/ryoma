import pandas as pd
import mysql.connector
import os
import sys
from sqlalchemy import create_engine, MetaData, Table, Column
import snowflake.connector


# Map NumPy data types to SQLAlchemy types for Snowflake
PANDAS_SNOWFLAKE_TYPE_MAPPING = {
    'int64': "Int",
    'float64': "FLOAT",
    'object': "VARCHAR",
}

# MySQL configuration
MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
MYSQL_USER = os.environ.get("MYSQL_USER", "root")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "") 
MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE", "chatgpt")


# Snowflake configuration
SNOWFLAKE_ACCOUNT = os.environ.get('SNOWFLAKE_ACCOUNT', "") # e.g. abc12345.us-east-1
SNOWFLAKE_USER = os.environ.get('SNOWFLAKE_USER', "")
SNOWFLAKE_PASSWORD = os.environ.get('SNOWFLAKE_PASSWORD', "")
SNOWFLAKE_WAREHOUSE = os.environ.get('SNOWFLAKE_WAREHOUSE', "")
SNOWFLAKE_DATABASE = os.environ.get('SNOWFLAKE_DATABASE', "")
SNOWFLAKE_SCHEMA = os.environ.get('SNOWFLAKE_SCHEMA', "")


def load_data_from_mysql(mysql_conn, table_name):

    # Load data from MySQL table into pandas DataFrame
    query = f"SELECT * FROM {table_name};"
    df = pd.read_sql(query, mysql_conn)

    return df


def create_snowflake_table_from_mysql_table(sf_conn, df, table_name):
    # Create the CREATE TABLE SQL statement
    create_table_sql = f"CREATE OR REPLACE TABLE {table_name} ("
    create_table_sql += ", ".join([f"{col} {PANDAS_SNOWFLAKE_TYPE_MAPPING[str(df[col].dtype)]}" for col in df.columns])
    create_table_sql += ")"

    # Execute the CREATE TABLE statement in Snowflake
    cursor = sf_conn.cursor()
    cursor.execute(f"USE DATABASE {SNOWFLAKE_DATABASE}")
    cursor.execute(f"USE SCHEMA {SNOWFLAKE_SCHEMA}")
    cursor.execute(create_table_sql)


def write_data_to_snowflake(sf_conn, df, table_name):

    # Write data from pandas DataFrame to Snowflake table
    cursor = sf_conn.cursor()
    cursor.execute(f"USE DATABASE {SNOWFLAKE_DATABASE}")
    cursor.execute(f"USE SCHEMA {SNOWFLAKE_SCHEMA}")
    cursor.executemany(f"INSERT INTO {table_name} VALUES ({', '.join(['%s'] * len(df.columns))})", df.values.tolist())


def transform_data(df):
    df['id'] = df['id'].astype(str)
    return df


def main(table_name):

    # Connect to MySQL database
    mysql_connection = mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE
    )

    # Load data from MySQL
    data_df = load_data_from_mysql(mysql_connection, table_name)

    # Close MySQL connection
    mysql_connection.close()
    
    # transform data
    transformed_df = transform_data(data_df)

    # Connect to Snowflake
    snowflake_connection = snowflake.connector.connect(
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        account=SNOWFLAKE_ACCOUNT,
        warehouse=SNOWFLAKE_WAREHOUSE,
        database=SNOWFLAKE_DATABASE,
        schema=SNOWFLAKE_SCHEMA
    )

    # Create Snowflake table from MySQL table
    create_snowflake_table_from_mysql_table(snowflake_connection, transformed_df, table_name)

    # Write data to Snowflake
    write_data_to_snowflake(snowflake_connection, transformed_df, table_name)

    # Commit and close Snowflake connection
    snowflake_connection.commit()
    snowflake_connection.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script_name.py <table_name>")
        sys.exit(1)

    table_name = sys.argv[1]
    main(table_name)

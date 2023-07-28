from pyspark.sql import SparkSession
from pyspark.sql.types import IntegerType, FloatType, StringType

# MySQL configuration
MYSQL_HOST = "your_mysql_host"
MYSQL_USER = "your_mysql_user"
MYSQL_PASSWORD = "your_mysql_password"
MYSQL_DATABASE = "your_mysql_database"
MYSQL_TABLE = "your_mysql_table"

# Snowflake configuration
SNOWFLAKE_ACCOUNT = "your_snowflake_account"
SNOWFLAKE_USER = "your_snowflake_user"
SNOWFLAKE_PASSWORD = "your_snowflake_password"
SNOWFLAKE_WAREHOUSE = "your_snowflake_warehouse"
SNOWFLAKE_DATABASE = "your_snowflake_database"
SNOWFLAKE_SCHEMA = "your_snowflake_schema"
SNOWFLAKE_TABLE = "your_snowflake_table"

# Data type mapping between MySQL and Snowflake
MYSQL_SNOWFLAKE_TYPE_MAPPING = {
    'int64': IntegerType(),
    'float64': FloatType(),
    'object': StringType(),
}

def load_data_from_mysql(spark):
    # Read data from MySQL table into a PySpark DataFrame
    jdbc_url = f"jdbc:mysql://{MYSQL_HOST}/{MYSQL_DATABASE}"
    properties = {
        "user": MYSQL_USER,
        "password": MYSQL_PASSWORD,
        "driver": "com.mysql.cj.jdbc.Driver"
    }
    df = spark.read.jdbc(jdbc_url, table=MYSQL_TABLE, properties=properties)
    return df

def write_data_to_snowflake(df):
    # Write data from PySpark DataFrame to Snowflake table
    df.write.format("snowflake") \
        .option("sfURL", f"{SNOWFLAKE_ACCOUNT}.snowflakecomputing.com") \
        .option("sfDatabase", SNOWFLAKE_DATABASE) \
        .option("sfSchema", SNOWFLAKE_SCHEMA) \
        .option("sfWarehouse", SNOWFLAKE_WAREHOUSE) \
        .option("dbtable", SNOWFLAKE_TABLE) \
        .option("sfUser", SNOWFLAKE_USER) \
        .option("sfPassword", SNOWFLAKE_PASSWORD) \
        .mode("overwrite") \
        .save()

def main():
    # Create a Spark session
    spark = SparkSession.builder \
        .appName("MySQL to Snowflake") \
        .getOrCreate()

    # Load data from MySQL into a PySpark DataFrame
    data_df = load_data_from_mysql(spark)

    # Write data to Snowflake
    write_data_to_snowflake(data_df)

    # Stop the Spark session
    spark.stop()

if __name__ == "__main__":
    main()

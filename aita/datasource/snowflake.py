from typing import Optional

import pandas as pd
import snowflake.connector

from aita.datasource.base import SqlDataSource


class SnowflakeDataSource(SqlDataSource):

    # SELECT statement from snowflake information_schema to extract table and column metadata
    # https://docs.snowflake.com/en/sql-reference/account-usage.html#label-account-usage-views
    # This can be modified to use account_usage for performance at the cost of latency if necessary.
    SQL_STATEMENT = """
SELECT
    LOWER(c.COLUMN_NAME) AS col_name,
    c.COMMENT AS col_description,
    LOWER(c.DATA_TYPE) AS col_type,
    c.ORDINAL_POSITION AS col_sort_order,
    LOWER(c.TABLE_CATALOG) AS database,
    LOWER(c.TABLE_SCHEMA) AS schema,
    LOWER(c.TABLE_NAME) AS name,
    t.COMMENT AS description,
    IFF(LOWER(t.TABLE_TYPE) = 'VIEW', 'true', 'false') AS is_view
FROM
    "{database}"."INFORMATION_SCHEMA"."COLUMNS" AS c
LEFT JOIN
    "{database}"."INFORMATION_SCHEMA"."TABLES" AS t
        ON c.TABLE_NAME = t.TABLE_NAME
        AND c.TABLE_SCHEMA = t.TABLE_SCHEMA
WHERE
    c.TABLE_SCHEMA = 'TPCH_SF1'
{where_clause_suffix};
    """

    def __init__(
        self,
        user: str,
        password: str,
        account: str,
        warehouse: Optional[str] = "COMPUTE_WH",
        role: Optional[str] = None,
        database: Optional[str] = None,
        schema: Optional[str] = None,
        **kwargs,
    ):
        self.user = user
        self.password = password
        self.account = account
        self.warehouse = warehouse
        self.role = role
        self.schema = schema
        self.database = database
        super().__init__()

    def create_engine(self, connection_url: Optional[str] = None):
        return snowflake.connector.connect(
            user=self.user,
            password=self.password,
            account=self.account,
            warehouse=self.warehouse,
            database=self.database,
            schema=self.schema,
        )

    def execute(self, query: str, params=None):
        cur = self.engine.cursor()
        cur.execute(query, params)
        return cur.fetchall()

    def to_pandas(self, query: str, params=None):
        return pd.read_sql(query, self.engine, params=params)

    def get_uri(self):
        return f"snowflake://{self.user}:{self.password}@{self.account}?warehouse={self.warehouse}&database={self.database}&schema={self.schema}&role={self.role}"

    def get_metadata(self, **kwargs):

        if "where_clause_suffix" in kwargs:
            where_clause_suffix = "AND " + kwargs["where_clause_suffix"]
        else:
            where_clause_suffix = ""

        sql_statement = self.SQL_STATEMENT.format(
            cluster_source="cluster",
            database=self.database,
            schema=self.schema,
            where_clause_suffix=where_clause_suffix,
        )
        return self.execute(sql_statement)

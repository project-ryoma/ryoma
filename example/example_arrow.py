# write an arrow ADBC connect to postgresql and ingest data into it

import pyarrow as pa

# create a table
table = pa.table({"a": [1, 2, 3], "b": [4, 5, 6]})

# adbc connection
from adbc_driver_postgres.dbapi import connect

connection = connect("postgresql://localhost:5432/postgres")

# ingest data
cursor = connection.cursor()
cursor.adbc_ingest("table_name", table)
connection.commit()

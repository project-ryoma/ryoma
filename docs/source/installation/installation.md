# Installation

To install Ryoma, run the following command:

```bash
pip install ryoma_ai
```

If you want to use additional data source dependency, you can install it by running the following command:

```bash
pip install ryoma_ai[snowflake]
```

Then you can use the data source in your agent like this:


```python
from ryoma_ai.datasource.snowflake import SnowflakeDataSource
from ryoma_ai.agent.sql import SqlAgent

snowflake_datasource = SnowflakeDataSource("snowflake://account.region.snowflakecomputing.com/db")
sql_agent = SqlAgent("gpt-3.5-turbo")
    .add_datasource(snowflake_datasource)
```
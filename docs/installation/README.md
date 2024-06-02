# Installation

To install Aita, run the following command:

{% code title="bash" %}
```bash
pip install aita
```
{% endcode%}

If you want to use additional data source dependency, you can install it by running the following command:

{% code title="bash" %}
```bash
pip install aita[snowflake]
```
{% endcode%}
Then you can use the data source in your agent like this:

{% code title="python" %}
```python
from aita.datasource.snowflake import SnowflakeDataSource
from aita.agent.sql import SqlAgent

snowflake_datasource = SnowflakeDataSource("snowflake://account.region.snowflakecomputing.com/db")
sql_agent = SqlAgent("gpt-3.5-turbo") \
    .add_datasource(snowflake_datasource)
```
# SqlAgent

The SqlAgent can be used to ask questions in natural language and interact with SQL databases.

## Example

Pass Data Source to SqlAgent and analyze the data.

{% code title="python" %}

```python
from aita.agent.sql import SqlAgent
from aita.datasource.sql import SqlDataSource

datasource = SqlDataSource("sqlite:///data.db")
sql_agent = SqlAgent(datasource, "gpt-3.5-turbo")
sql_agent.chat("Get the top 10 customers by purchase amount")
```

{% endcode}
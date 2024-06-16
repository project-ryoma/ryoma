# SqlAgent

The SqlAgent can be used to ask questions in natural language and interact with SQL databases.

## Example

Pass Data Source to SqlAgent and analyze the data.

{% code title="python" %}

```python
from aita.agent.sql import SqlAgent
from aita.datasource.postgresql import PostgreSqlDataSource
from aita.prompt.base import BasicDataSourcePromptTemplate

postgres_datasource = PostgreSqlDataSource("postgresql://localhost:5432/db")
sql_agent = SqlAgent("gpt-3.5-turbo") \
    .set_prompt_context(BasicDataSourcePromptTemplate) \
    .add_datasource(postgres_datasource)
sql_agent.stream("Get the top 10 customers by purchase amount")
```

{% endcode}

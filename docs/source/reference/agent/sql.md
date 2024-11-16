# SqlAgent

The SqlAgent can be used to ask questions in natural language and interact with SQL databases.

## Example

Pass Data Source to SqlAgent and analyze the data.


```python
from ryoma_ai.agent.sql import SqlAgent
from ryoma_ai.datasource.postgres import PostgresDataSource
from ryoma_ai.prompt.base import BasicContextPromptTemplate

postgres_datasource = PostgresDataSource("postgresql://localhost:5432/db")
sql_agent = SqlAgent("gpt-3.5-turbo")
.set_context_prompt(BasicContextPromptTemplate)
.add_datasource(postgres_datasource)
sql_agent.stream("Get the top 10 customers by purchase amount")
```


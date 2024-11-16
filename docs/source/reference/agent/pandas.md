# Pandas Agent

The Pandas agent is an Ryoma agent that runs on the Pandas library.
The Pandas agent can be used to ask questions in natural language and interact with Pandas DataFrames.

## Example

pass Data Source to Pandas Agent and return result as a dataframe.


```python
from ryoma_ai.agent.pandas_agent import PandasAgent
from ryoma_ai.datasource.sqlite import SqliteDataSource
from ryoma_ai.prompt.base import BasicContextPromptTemplate

datasource = SqliteDataSource("sqlite:///data.db")
pandas_agent = PandasAgent("gpt-3.5-turbo")
.set_context_prompt(BasicContextPromptTemplate)
.add_datasource(datasource)
pandas_agent.stream("Get the top 10 customers by purchase amount")
```

add a DataFrame to the Pandas Agent, ask the agent to analyze the data.


```python
from ryoma_ai.agent.pandas_agent import PandasAgent
import pandas as pd

df = pd.DataFrame({
    'customer_id': [1, 2, 3, 4, 5],
    'purchase_amount': [100, 200, 300, 400, 500]
})
pandas_agent = PandasAgent("gpt-3.5-turbo")
    .add_dataframe(df)

pandas_agent.stream("I want to get the top customers which making the most purchases")
```

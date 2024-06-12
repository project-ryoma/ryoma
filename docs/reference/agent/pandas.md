# Pandas Agent

The Pandas agent is an Aita agent that runs on the Pandas library.
The Pandas agent can be used to ask questions in natural language and interact with Pandas DataFrames.

## Example

pass Data Source to Pandas Agent and return result as a dataframe.

{% code title="python" %}

```python
from aita.agent.pandas import PandasAgent
from aita.datasource.sqlite import SqliteDataSource
from aita.prompt.base import BasicDataSourcePromptTemplate

datasource = SqliteDataSource("sqlite:///data.db")
pandas_agent = PandasAgent("gpt-3.5-turbo") \
    .set_prompt_template(BasicDataSourcePromptTemplate) \
    .add_datasource(datasource)
pandas_agent.stream("Get the top 10 customers by purchase amount")
```
{% endcode %}

add a DataFrame to the Pandas Agent, ask the agent to analyze the data.

{% code title="python" %}
```python
from aita.agent.pandas import PandasAgent
import pandas as pd

df = pd.DataFrame({
    'customer_id': [1, 2, 3, 4, 5],
    'purchase_amount': [100, 200, 300, 400, 500]
})
pandas_agent = PandasAgent("gpt-3.5-turbo") \
    .add_dataframe(df)

pandas_agent.stream("I want to get the top customers which making the most purchases")
```
{% endcode %}

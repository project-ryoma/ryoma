# Pandas Agent

The Pandas agent is an Aita agent that runs on the Pandas library.
The Pandas agent can be used to ask questions in natural language and interact with Pandas DataFrames.

## Example

pass Data Source to Pandas Agent and return result as a dataframe.

{% code title="python" %}
```python
from aita.agent.pandas import PandasAgent
from aita.datasource.sql import SqlDataSource

datasource = SqlDataSource("sqlite:///data.db")
pandas_agent = PandasAgent(datasource, "gpt-3.5-turbo")
df = pandas_agent.chat("Get the top 10 customers by purchase amount")
print(df)
```
{% endcode %}

Pass Pandas DataFrame to Pandas Agent and analyze the data.

{% code title="python" %}
```python
from aita.agent.pandas import PandasAgent
import pandas as pd

df = pd.DataFrame({
    'customer_id': [1, 2, 3, 4, 5],
    'purchase_amount': [100, 200, 300, 400, 500]
})
sql_agent = PandasAgent(df, "gpt-3.5-turbo")

print(sql_agent.chat("I want to get the top customers which making the most purchases"))
```
{% endcode %}

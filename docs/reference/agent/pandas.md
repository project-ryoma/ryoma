# Pandas Agent

The Pandas agent is an Aita agent that runs on the Pandas library.
The Pandas agent can be used to ask questions in natural language and interact with Pandas DataFrames.

## Example

{% code title="python" %}
```python
from aita.agent.pandas import PandasAgent
import pandas as pd

df = pd.DataFrame({
    'customer_id': [1, 2, 3, 4, 5],
    'purchase_amount': [100, 200, 300, 400, 500]
})
sql_agent = PandasAgent({"df": df}, "gpt-3.5-turbo")

print(sql_agent.chat("I want to get the top customers which making the most purchases"))
```
{% endcode %}

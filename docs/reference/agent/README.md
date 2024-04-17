
# Aita agent

Aita agent is an AI agent that runs on LLM (Large Language Model), and can be used to ask questions in natural language.
Aita agent can also use tools (refer to [Aita tool](tools.md)) to let agent to run on various data APIs such as Pandas, Pyarrow, Spark, Pytorch etc.


## Example

{% code title="python" %}
```python
from aita.agent import PandasAgent
import pandas as pd

df = pd.DataFrame({
    'customer_id': [1, 2, 3, 4, 5],
    'purchase_amount': [100, 200, 300, 400, 500]
})
sql_agent = PandasAgent({"df": df}, "gpt-3.5-turbo", 0.8)

print(sql_agent.chat("I want to get the top customers which making the most purchases"))
```
{% endcode %}

## Agents

Currently supported agents are:
- [PythonAgent](python.md)
- [SqlAgent](sql.md)
- [PandasAgent](pandas.md)
- [PyarrowAgent](pyarrow.md)
- [SparkAgent](spark.md)
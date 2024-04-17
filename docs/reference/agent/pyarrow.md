# Pyarrow Agent

The Pyarrow agent is an Aita agent that runs on the Pyarrow library.
The Pyarrow agent can be used to ask questions in natural language and interact with Pyarrow Tables.

## Example

{% code title="python" %}
```python
from aita.agent import PyarrowAgent
import pyarrow as pa

table = pa.table({
    'customer_id': pa.array([1, 2, 3, 4, 5]),
    'purchase_amount': pa.array([100, 200, 300, 400, 500])
})

pa_agent = PyarrowAgent({"table": table}, "gpt-3.5-turbo", 0.8)
```
{% endcode %}
# Pyarrow Agent

The Pyarrow agent is an Aita agent that runs on the Pyarrow library.
The Pyarrow agent can be used to ask questions in natural language and interact with Pyarrow Tables.

## Example

{% code title="python" %}
```python
from aita.agent.pyarrow import PyArrowAgent 
import pyarrow as pa

table = pa.table({
    'customer_id': pa.array([1, 2, 3, 4, 5]),
    'purchase_amount': pa.array([100, 200, 300, 400, 500])
})

pa_agent = PyArrowAgent(table, "gpt-3.5-turbo")
```
{% endcode %}
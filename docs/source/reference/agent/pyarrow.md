# Pyarrow Agent

The Pyarrow agent is an Ryoma agent that runs on the Pyarrow library.
The Pyarrow agent can be used to ask questions in natural language and interact with Pyarrow Tables.

## Example

```python
from ryoma_ai.agent.pyarrow import PyArrowAgent
import pyarrow as pa

table = pa.table({
    'customer_id': pa.array([1, 2, 3, 4, 5]),
    'purchase_amount': pa.array([100, 200, 300, 400, 500])
})

pa_agent = PyArrowAgent("gpt-3.5-turbo")
    .add_table(table)

pa_agent.stream("I want to get the top customers which making the most purchases")
```

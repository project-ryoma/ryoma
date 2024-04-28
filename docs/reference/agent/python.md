# Python Agent

The Python agent is an Aita agent that run python script in IPython Kernel ([IPython](https://ipython.org/)).

## Example

{% code title="python" %}
```python
from aita.agent.python import PythonAgent

python_agent = PythonAgent(None, "gpt-3.5-turbo")

print(python_agent.chat("print('Hello, World!')"))
```
{% endcode %}

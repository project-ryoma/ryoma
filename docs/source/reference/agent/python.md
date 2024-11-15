# Python Agent

The Python agent is an Ryoma agent that run python script in IPython Kernel ([IPython](https://ipython.org/)).

## Example


```python
from ryoma_ai.agent.python import PythonAgent

python_agent = PythonAgent("gpt-3.5-turbo")

python_agent.stream("print('Hello, World!')")
```

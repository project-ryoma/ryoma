# Spark Agent

Spark agent is an Aita agent specialize in writing spark code.

## Example

{% code title="python" %}
```python
from aita.agent import SparkAgent

spark_agent = SparkAgent(None, "gpt-3.5-turbo", 0.8)

print(spark_agent.chat("I want to get the top customers which making the most purchases"))
```
{% endcode %}

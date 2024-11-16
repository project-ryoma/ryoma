# Spark Agent

Spark agent is an Ryoma agent specialize in writing spark code.

## Example


```python
from ryoma_ai.agent.pyspark import PySparkAgent
from ryoma_ai.datasource.postgres import PostgresDataSource

datasource = PostgresDataSource("postgresql://localhost:5432/db")
spark_configs = {
    "master": "local",
    "appName": "Ryoma"
}
spark_agent = PySparkAgent(spark_configs, "gpt-3.5-turbo")

spark_agent.stream("I want to get the top customers which making the most purchases")
```

(ryoma-agent)=

# Ryoma agent Documentation

Ryoma agent is an AI agent that runs on LLM (Large Language Model), and can be used to ask questions in natural language.
Ryoma agent can also use tools (refer to [Ryoma tool](tools.md)) to let agent to run on various data APIs such as Pandas, Pyarrow, Spark, Pytorch etc.

## Models
Ryoma model providers are inspired by [jupyter-ai-magic](https://jupyter-ai.readthedocs.io/en/latest/users/index.html#model-providers),
and currently supported models are:

| Provider            | Provider ID          | Environment variable(s)    | Python package(s)               |
|---------------------|----------------------|----------------------------|---------------------------------|
| AI21                | `ai21`               | `AI21_API_KEY`             | `ai21`                          |
| Anthropic           | `anthropic`          | `ANTHROPIC_API_KEY`        | `langchain-anthropic`           |
| Anthropic (playground)    | `anthropic-playground`     | `ANTHROPIC_API_KEY`        | `langchain-anthropic`           |
| Bedrock             | `bedrock`            | N/A                        | `boto3`                         |
| Bedrock (playground)      | `bedrock-playground`       | N/A                        | `boto3`                         |
| Cohere              | `cohere`             | `COHERE_API_KEY`           | `cohere`                        |
| ERNIE-Bot           | `qianfan`            | `QIANFAN_AK`, `QIANFAN_SK` | `qianfan`                       |
| Gemini              | `gemini`             | `GOOGLE_API_KEY`           | `langchain-google-genai`        |
| GPT4All             | `gpt4all`            | N/A                        | `gpt4all`                       |
| Hugging Face Hub    | `huggingface_hub`    | `HUGGINGFACEHUB_API_TOKEN` | `huggingface_hub`, `ipywidgets`, `pillow` |
| NVIDIA              | `nvidia-playground`        | `NVIDIA_API_KEY`           | `langchain_nvidia_ai_endpoints` |
| OpenAI              | `openai`             | `OPENAI_API_KEY`           | `langchain-openai`              |
| OpenAI (playground)       | `openai-playground`        | `OPENAI_API_KEY`           | `langchain-openai`              |
| SageMaker           | `sagemaker-endpoint` | N/A                        | `boto3`                         |


## Example

```python
from ryoma_ai.agent.pandas import PandasAgent
import pandas as pd

df = pd.DataFrame({
    'customer_id': [1, 2, 3, 4, 5],
    'purchase_amount': [100, 200, 300, 400, 500]
})
sql_agent = PandasAgent(df, "gpt-3.5-turbo")

print(sql_agent.stream("I want to get the top customers which making the most purchases"))
```

## Agents

Currently supported agents are:
- [PythonAgent](python.md)
- [SqlAgent](sql.md)
- [PandasAgent](pandas.md)
- [PyarrowAgent](pyarrow.md)
- [SparkAgent](spark.md)


```{toctree}
:maxdepth: 2

pandas
pyarrow
python
spark
sql
```

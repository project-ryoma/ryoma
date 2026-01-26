# Ryoma
AI Powered Data Agent framework, a comprehensive solution for data analysis, engineering, and visualization.

> **📢 Note:** Ryoma AI is undergoing a major refactoring to v0.2.0 with cleaner architecture and better separation of concerns. See [Documentation Index](docs/INDEX.md) for full details and [Refactoring Progress](docs/plans/REFACTORING_PROGRESS.md) for status (63% complete).

[![Build status](https://github.com/project-ryoma/ryoma/workflows/build/badge.svg)](https://github.com/project-ryoma/ryoma/actions/workflows/build.yml?query=workflow%3Abuild)
[![Python Version](https://img.shields.io/pypi/pyversions/ryoma.svg)](https://pypi.org/project/ryoma/)
[![Dependencies Status](https://img.shields.io/badge/dependencies-up%20to%20date-brightgreen.svg)](https://github.com/project-ryoma/ryoma/pulls?utf8=%E2%9C%93&q=is%3Apr%20author%3Aapp%2Fdependabot)

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Security: bandit](https://img.shields.io/badge/security-bandit-green.svg)](https://github.com/PyCQA/bandit)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/project-ryoma/ryoma/blob/main/.pre-commit-config.yaml)
[![License](https://img.shields.io/github/license/project-ryoma/ryoma)](https://github.com/project-ryoma/ryoma/blob/main/LICENSE)
[![Coverage Report](assets/images/coverage.svg)](https://github.com/project-ryoma/ryoma/blob/main/assets/images/coverage.svg)


## 📚 Documentation

**[→ Full Documentation Index](docs/INDEX.md)** - Start here for all documentation

**Quick Links:**
- [Architecture Overview](docs/ARCHITECTURE_COMPARISON.md) - v0.1.x vs v0.2.0 comparison
- [Refactoring Progress](docs/plans/REFACTORING_PROGRESS.md) - Current status (63% complete)
- [Test Organization](docs/TEST_ORGANIZATION.md) - Test suite structure and plans
- [Contributing](docs/source/contribution/contribution.md) - How to contribute

## Tech Stack

Our platform leverages a combination of cutting-edge technologies and frameworks:

- **[Langchain](https://www.langchain.com/)**: Facilitates the seamless integration of language models into application workflows, significantly enhancing AI interaction capabilities.
- **[Reflex](https://reflex.dev/)**: An open-source framework for quickly building beautiful, interactive web applications in pure Python
- **[Apache Arrow](https://arrow.apache.org/)**: A cross-language development platform for in-memory data that specifies a standardized language-independent columnar memory format for flat and hierarchical data, organized for efficient analytic operations on modern hardware like CPUs and GPUs.
- **[Jupyter Ai Magics](https://github.com/jupyterlab/jupyter-ai)**: A JupyterLab extension that provides a set of magics for working with AI models.
- **[Amundsen](https://www.amundsen.io/)**: A data discovery and metadata platform that helps users discover, understand, and trust the data they use.
- **[Ibis](https://ibis-project.org/)**: A Python data analysis framework that provides a pandas-like API for analytics on large datasets.
- **[Feast](https://feast.dev/)**: An operational feature store for managing and serving machine learning features to models in production.

## Installation
Simply install the package using pip:

```shell
pip install ryoma_ai
```
Or with extra dependencies:

```shell
pip install ryoma_ai[snowflake]
```

## Basic Example
Below is an example of using SqlAgent to connect to a postgres database and ask a question.
You can read more details in the [documentation](https://project-ryoma.github.io/ryoma/).

```python
from ryoma_ai.agent.sql import SqlAgent
from ryoma_ai.datasource.postgres import PostgresDataSource

# Connect to a postgres catalog
datasource = PostgresDataSource("postgresql://user:password@localhost:5432/dbname")

# Create a SQL agent
sql_agent = SqlAgent("gpt-3.5-turbo").add_datasource(datasource)

# ask question to the agent
sql_agent.stream("I want to get the top 5 customers which making the most purchases", display=True)
```

The Sql agent will try to run the tool as shown below:
```text
================================ Human Message =================================

I want to get the top 5 customers which making the most purchases
================================== Ai Message ==================================
Tool Calls:
  sql_database_query (call_mWCPB3GQGOTLYsvp21DGlpOb)
 Call ID: call_mWCPB3GQGOTLYsvp21DGlpOb
  Args:
    query: SELECT C.C_NAME, SUM(L.L_EXTENDEDPRICE) AS TOTAL_PURCHASES FROM CUSTOMER C JOIN ORDERS O ON C.C_CUSTKEY = O.O_CUSTKEY JOIN LINEITEM L ON O.O_ORDERKEY = L.L_ORDERKEY GROUP BY C.C_NAME ORDER BY TOTAL_PURCHASES DESC LIMIT 5
    result_format: pandas
```
Continue to run the tool with the following code:
```python
sql_agent.stream(tool_mode=ToolMode.ONCE)
```
Output will look like after running the tool:
```text
================================== Ai Message ==================================

The top 5 customers who have made the most purchases are as follows:

1. Customer#000143500 - Total Purchases: $7,154,828.98
2. Customer#000095257 - Total Purchases: $6,645,071.02
3. Customer#000087115 - Total Purchases: $6,528,332.52
4. Customer#000134380 - Total Purchases: $6,405,556.97
5. Customer#000103834 - Total Purchases: $6,397,480.12
```

## Use Ryoma Lab
Ryoma lab is an application that allows you to interact with your data and AI models in UI.
The ryoma lab is built with [Reflex](https://reflex.dev/).

1. Create Ryoma lab configuration file `rxconfig.py` in your project:
```python
import logging

import reflex as rx
from reflex.constants import LogLevel

config = rx.Config(
    app_name="ryoma_lab",
    loglevel=LogLevel.INFO,
)

# Setup basic configuration for logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
```

2. You can start the ryoma lab by running the following command:
```shell
ryoma_lab run
```
the ryoma lab will be available at `http://localhost:3000`.
![ui.png](assets%2Fui.png)

## Supported Models
Model provider are supported by jupyter ai magics. Ensure the corresponding environment variables are set before using the Ryoma agent.

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

## Supported Data Sources
- [x] Snowflake
- [x] Sqlite
- [x] BigQuery
- [x] Postgres
- [x] MySQL
- [x] File (CSV, Excel, Parquet, etc.)
- [ ] Redshift
- [ ] DynamoDB

## Supported Engines
- [x] Apache Spark
- [x] Apache Flink
- [ ] Presto

## 🛡 License

[![License](https://img.shields.io/github/license/project-ryoma/ryoma)](https://github.com/project-ryoma/ryoma/blob/main/LICENSE)

This project is licensed under the terms of the `Apache Software License 2.0` license. See [LICENSE](https://github.com/ryoma/ryoma/blob/master/LICENSE) for more details.

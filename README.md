# aita
AI Powered Data Platform, a comprehensive solution for data analysis, visualization, and automation.

<div align="center">

[![Build status](https://github.com/project-aita/aita/workflows/build/badge.svg?branch=main&event=push)](https://github.com/project-aita/aita/actions?query=workflow%3Abuild)
[![Python Version](https://img.shields.io/pypi/pyversions/aita.svg)](https://pypi.org/project/aita/)
[![Dependencies Status](https://img.shields.io/badge/dependencies-up%20to%20date-brightgreen.svg)](https://github.com/project-aita/aita/pulls?utf8=%E2%9C%93&q=is%3Apr%20author%3Aapp%2Fdependabot)

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Security: bandit](https://img.shields.io/badge/security-bandit-green.svg)](https://github.com/PyCQA/bandit)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/projec-taita/aita/blob/main/.pre-commit-config.yaml)
[![Semantic Versions](https://img.shields.io/badge/%20%20%F0%9F%93%A6%F0%9F%9A%80-semantic--versions-e10079.svg)](https://github.com/project-aita/aita/releases)
[![License](https://img.shields.io/github/license/project-aita/aita)](https://github.com/project-aita/aita/blob/main/LICENSE)
![Coverage Report](aita/assets/images/coverage.svg)

</div>

## Tech Stack

Our platform leverages a combination of cutting-edge technologies and frameworks:

- **[Langchain](https://www.langchain.com/)**: Facilitates the seamless integration of language models into application workflows, significantly enhancing AI interaction capabilities.
- **[FastAPI](https://fastapi.tiangolo.com/)**: A modern, fast (high-performance) web framework for building APIs with Python 3.7+, emphasizing speed, reliability, and ease of use.
- **[Apache Arrow](https://arrow.apache.org/)**: A cross-language development platform for in-memory data that specifies a standardized language-independent columnar memory format for flat and hierarchical data, organized for efficient analytic operations on modern hardware like CPUs and GPUs.
- **[Jupyter Ai Magics](https://github.com/jupyterlab/jupyter-ai)**: A JupyterLab extension that provides a set of magics for working with AI models.

## Supported Models
Model provider are supported by jupyter ai magics.

| Provider            | Provider ID          | Environment variable(s)    | Python package(s)               |
|---------------------|----------------------|----------------------------|---------------------------------|
| AI21                | `ai21`               | `AI21_API_KEY`             | `ai21`                          |
| Anthropic           | `anthropic`          | `ANTHROPIC_API_KEY`        | `langchain-anthropic`           |
| Anthropic (chat)    | `anthropic-chat`     | `ANTHROPIC_API_KEY`        | `langchain-anthropic`           |
| Bedrock             | `bedrock`            | N/A                        | `boto3`                         |
| Bedrock (chat)      | `bedrock-chat`       | N/A                        | `boto3`                         |
| Cohere              | `cohere`             | `COHERE_API_KEY`           | `cohere`                        |
| ERNIE-Bot           | `qianfan`            | `QIANFAN_AK`, `QIANFAN_SK` | `qianfan`                       |
| Gemini              | `gemini`             | `GOOGLE_API_KEY`           | `langchain-google-genai`        |
| GPT4All             | `gpt4all`            | N/A                        | `gpt4all`                       |
| Hugging Face Hub    | `huggingface_hub`    | `HUGGINGFACEHUB_API_TOKEN` | `huggingface_hub`, `ipywidgets`, `pillow` |
| NVIDIA              | `nvidia-chat`        | `NVIDIA_API_KEY`           | `langchain_nvidia_ai_endpoints` |
| OpenAI              | `openai`             | `OPENAI_API_KEY`           | `langchain-openai`              |
| OpenAI (chat)       | `openai-chat`        | `OPENAI_API_KEY`           | `langchain-openai`              |
| SageMaker           | `sagemaker-endpoint` | N/A                        | `boto3`                         |

## Supported Data Sources
- Snowflake
- BigQuery
- Postgres
- MySQL
- Redshift
- DynamoDB

## Supported Engines
- Apache Spark
- Apache Flink
- Presto
- **[Ray.io](https://ray.io/)**: A distributed computing framework that efficiently scales AI tasks and data processing across clusters, improving performance and resource utilization.

## 🛡 License

[![License](https://img.shields.io/github/license/project-aita/aita)](https://github.com/project-aita/aita/blob/main/LICENSE)

This project is licensed under the terms of the `Apache Software License 2.0` license. See [LICENSE](https://github.com/aita/aita/blob/master/LICENSE) for more details.

## 📃 Citation

```bibtex
@misc{aita,
  author = {aita},
  title = {AI Powered Data Platform},
  year = {2024},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/project-aita/aita}}
}
```
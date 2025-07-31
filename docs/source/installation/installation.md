# 📦 Installation

Complete installation guide for Ryoma AI with all database connectors and optional features.

## 📋 Prerequisites

- **Python 3.9+** - Ryoma requires Python 3.9 or higher
- **API Key** - OpenAI, Anthropic, or other supported LLM provider
- **Database Drivers** - For your specific database (optional)

## 🚀 Quick Installation

### Basic Installation
```bash
pip install ryoma_ai
```

This installs the core Ryoma package with basic functionality.

### With Database Support
```bash
# PostgreSQL support
pip install ryoma_ai[postgres]

# MySQL support
pip install ryoma_ai[mysql]

# Snowflake support
pip install ryoma_ai[snowflake]

# BigQuery support
pip install ryoma_ai[bigquery]

# All database connectors
pip install ryoma_ai[all]
```

## 🗄️ Database-Specific Setup

### PostgreSQL
```bash
pip install ryoma_ai[postgres]
```

```python
from ryoma_ai.datasource.postgres import PostgresDataSource

datasource = PostgresDataSource(
    connection_string="postgresql://user:password@localhost:5432/database",
    enable_profiling=True  # Enable metadata extraction
)
```

### Snowflake
```bash
pip install ryoma_ai[snowflake]
```

```python
from ryoma_ai.datasource.snowflake import SnowflakeDataSource

datasource = SnowflakeDataSource(
    account="your-account",
    user="your-user",
    password="your-password",
    database="your-database",
    warehouse="your-warehouse",
    enable_profiling=True
)
```

### BigQuery
```bash
pip install ryoma_ai[bigquery]
```

```python
from ryoma_ai.datasource.bigquery import BigQueryDataSource

datasource = BigQueryDataSource(
    project_id="your-project-id",
    credentials_path="/path/to/service-account.json",
    enable_profiling=True
)
```

## 🧠 LLM Provider Setup

### OpenAI
```bash
export OPENAI_API_KEY="your-openai-api-key"
```

```python
from ryoma_ai.agent.sql import SqlAgent

agent = SqlAgent(model="gpt-4", mode="enhanced")
```

### Anthropic Claude
```bash
pip install anthropic
export ANTHROPIC_API_KEY="your-anthropic-api-key"
```

```python
agent = SqlAgent(model="claude-3-sonnet-20240229", mode="enhanced")
```

### Local Models (Ollama)
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull codellama:13b

pip install ollama
```

```python
from ryoma_ai.models.ollama import OllamaModel

model = OllamaModel("codellama:13b")
agent = SqlAgent(model=model, mode="enhanced")
```

## ✅ Verify Installation

```python
import ryoma_ai
print(f"Ryoma AI version: {ryoma_ai.__version__}")

# Test basic functionality
from ryoma_ai.agent.sql import SqlAgent
from ryoma_ai.datasource.sqlite import SqliteDataSource

datasource = SqliteDataSource(":memory:", enable_profiling=True)
agent = SqlAgent("gpt-3.5-turbo", mode="enhanced")
agent.add_datasource(datasource)

print("✅ Ryoma AI installation successful!")
```

## 🎯 Next Steps

- **[Quick Start Guide](../getting-started/quickstart.md)** - Get up and running in 5 minutes
- **[Advanced Setup](../getting-started/advanced-setup.md)** - Production configuration
- **[Examples](../getting-started/examples.md)** - Real-world use cases
- **[API Reference](../reference/index.md)** - Complete documentation
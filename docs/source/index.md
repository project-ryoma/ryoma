<!--
Copyright (c) Ryoma Project Contributors

SPDX-License-Identifier: Apache-2.0
-->

(l-main-doc-page)=

# 🚀 Ryoma AI Documentation

> **AI-Powered Data Analysis Platform**
> Connect to databases, ask questions in natural language, and get intelligent insights

## 🎯 What is Ryoma?

Ryoma is a cutting-edge AI-powered data platform that revolutionizes how data users interact with their data. Built on state-of-the-art research, Ryoma enables:

### 🤖 **Intelligent SQL Generation**
- **Enhanced SQL Agent** - Multi-step reasoning with safety validation
- **ReFoRCE Agent** - Research-based self-refinement for maximum accuracy
- **Natural Language Queries** - Ask questions in plain English, get SQL results

### 📊 **Advanced Database Profiling**
- **Comprehensive Metadata Extraction** - Automatic schema understanding
- **Data Quality Assessment** - Multi-dimensional quality scoring
- **Semantic Type Detection** - Automatic identification of emails, phones, IDs
- **Column Similarity Analysis** - LSH-based relationship discovery

### 🗄️ **Universal Database Support**
- **PostgreSQL, MySQL, Snowflake, BigQuery** - Production-ready connectors
- **SQLite, DuckDB** - Perfect for development and analytics
- **Ibis Integration** - Native database optimizations for better performance

### 🛡️ **Enterprise-Ready Security**
- **Query Validation** - Configurable safety policies
- **Access Control** - Fine-grained permissions
- **Audit Logging** - Complete query tracking

![Ryoma Architecture](assets/ryoma_marchitecture.png)

## 👥 Who is Ryoma for?

### 📈 **Data Analysts**
Transform natural language questions into complex SQL queries without deep SQL knowledge.

### 🔬 **Data Scientists**
Rapidly explore datasets and generate insights with AI-powered analysis.

### 💼 **Business Users**
Get answers from your data without waiting for technical teams.

### 🏢 **Enterprise Teams**
Deploy secure, scalable data analysis with comprehensive governance.

## 🚀 Quick Start

Get up and running in under 5 minutes:

```python
from ryoma_ai.agent.sql import SqlAgent
from ryoma_ai.datasource.postgres import PostgresDataSource

# Connect to your database with profiling
datasource = PostgresDataSource(
    connection_string="postgresql://user:pass@localhost:5432/db",
    enable_profiling=True  # Automatic metadata extraction
)

# Create enhanced SQL agent
agent = SqlAgent(model="gpt-4", mode="enhanced")
agent.add_datasource(datasource)

# Ask questions in natural language
response = agent.stream("Show me the top 10 customers by revenue this quarter")
print(response)
```

## 🎯 Key Features

| 🚀 Feature | 📝 Description | 🔗 Learn More |
|------------|----------------|---------------|
| **Enhanced SQL Agent** | Multi-step reasoning with safety validation | [Agent Guide →](reference/agent/sql.md) |
| **Database Profiling** | Comprehensive metadata extraction | [Profiling Guide →](architecture/database-profiling.md) |
| **Universal Connectors** | Support for all major databases | [Data Sources →](reference/data-sources/index.md) |
| **Safety Framework** | Configurable validation and security | [Advanced Setup →](getting-started/advanced-setup.md) |
| **Model Flexibility** | OpenAI, Anthropic, local models | [Models →](reference/models/index.md) |

## 📚 Documentation Sections


```{toctree}
:maxdepth: 2

aita-lab/index
architecture/index
contribution/index
getting-started/index
installation/index
reference/index
roadmap/index
tech-specs/index
```
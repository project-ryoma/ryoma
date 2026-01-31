
# 🚀 Quick Start

Get up and running with Ryoma in under 5 minutes! This guide covers the essentials to start analyzing data with AI.

## 📋 Prerequisites

- **Python 3.9+** - Ryoma requires Python 3.9 or higher
- **API Key** - OpenAI API key or other supported LLM provider
- **Database** (optional) - PostgreSQL, MySQL, SQLite, or other supported databases

## 📦 Installation

### Basic Installation
```bash
pip install ryoma_ai
```

### With Database Support
```bash
# PostgreSQL support
pip install ryoma_ai[postgres]

# Snowflake support
pip install ryoma_ai[snowflake]

# All database connectors
pip install ryoma_ai[all]
```

## 🎯 Quick Start Options

### Option 1: CLI Interface

The fastest way to get started:

```bash
# Set your API key
export OPENAI_API_KEY="your-api-key-here"

# Start the CLI
ryoma_ai --setup

# Or start with defaults
ryoma_ai
```

Then use natural language:
```bash
ryoma_ai> show me all tables in my database
ryoma_ai> what customers made purchases last month?
ryoma_ai> create a chart of sales by region
```

### Option 2: Programmatic Usage (Recommended)

For integration into your applications:

```python
from ryoma_ai import Ryoma
from ryoma_data import DataSource

# Set up data source
datasource = DataSource(
    "postgres",
    host="localhost",
    port=5432,
    database="mydb",
    user="user",
    password="password"
)

# Create Ryoma instance and agent
ryoma = Ryoma(datasource=datasource)
agent = ryoma.sql_agent(model="gpt-4", mode="enhanced")

# Ask questions in natural language
response = agent.stream("Show me the top 10 customers by revenue this month")
print(response)
```

### Option 3: Pandas Agent

For DataFrame analysis:

```python
from ryoma_ai import Ryoma
import pandas as pd

# Create sample data
df = pd.DataFrame({
    'customer_id': [1, 2, 3, 4, 5],
    'revenue': [1000, 2500, 1800, 3200, 900],
    'region': ['North', 'South', 'East', 'West', 'North']
})

# Create Ryoma and pandas agent
ryoma = Ryoma()
agent = ryoma.pandas_agent(model="gpt-4")
agent.add_dataframe(df, df_id="sales_data")

# Analyze with natural language
result = agent.stream("What's the average revenue by region?")
print(result)
```

## 🚀 Advanced Features

### Multiple Datasources

```python
from ryoma_ai import Ryoma
from ryoma_data import DataSource

# Create Ryoma instance
ryoma = Ryoma()

# Add multiple datasources
ryoma.add_datasource(
    DataSource("postgres", host="localhost", database="sales", user="user", password="pass"),
    name="sales"
)
ryoma.add_datasource(
    DataSource("postgres", host="localhost", database="marketing", user="user", password="pass"),
    name="marketing"
)

# Create agent (uses first datasource by default)
agent = ryoma.sql_agent(model="gpt-4", mode="enhanced")

# Query sales database
agent.stream("Show top products by revenue")

# Switch to marketing database
ryoma.set_active("marketing")
agent.stream("Show campaign performance")
```

### Agent Modes

```python
# Basic mode - simple SQL generation
agent = ryoma.sql_agent(model="gpt-4", mode="basic")

# Enhanced mode - multi-step reasoning with safety validation
agent = ryoma.sql_agent(model="gpt-4", mode="enhanced")

# ReFoRCE mode - state-of-the-art with self-refinement
agent = ryoma.sql_agent(model="gpt-4", mode="reforce")
```

## 🔧 Configuration

### Environment Variables
```bash
# Set your API key
export OPENAI_API_KEY="your-api-key-here"

# Optional: Configure other providers
export ANTHROPIC_API_KEY="your-anthropic-key"
```

## ✅ Verify Installation

Run this quick test to ensure everything is working:

```python
from ryoma_ai import Ryoma
from ryoma_data import DataSource

# Create in-memory SQLite database
datasource = DataSource("sqlite", database=":memory:")

# Create Ryoma and agent
ryoma = Ryoma(datasource=datasource)
agent = ryoma.sql_agent(model="gpt-3.5-turbo", mode="basic")

print("✅ Ryoma is ready to use!")
```

## 🎯 Next Steps

Now that you have Ryoma running, explore these advanced features:

- **[Database Profiling](../architecture/database-profiling.md)** - Automatic metadata extraction
- **[Enhanced SQL Agent](../architecture/enhanced-sql-agent.md)** - Advanced query generation
- **[API Reference](../reference/index.md)** - Complete method documentation
- **[Examples](examples.md)** - Real-world use cases

## 🆘 Need Help?

- **Documentation**: [docs.ryoma.dev](https://docs.ryoma.dev)
- **GitHub Issues**: [Report bugs or request features](https://github.com/project-ryoma/ryoma/issues)
- **Community**: Join our discussions for support and tips

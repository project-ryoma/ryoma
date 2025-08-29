
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

### Option 1: CLI Interface (Recommended)

The fastest way to get started:

```bash
# Set your API key
export OPENAI_API_KEY="your-api-key-here"

# Start the CLI
ryoma-ai --setup

# Or start with defaults
ryoma-ai
```

Then use natural language:
```bash
ryoma-ai> show me all tables in my database
ryoma-ai> what customers made purchases last month?  
ryoma-ai> create a chart of sales by region
```

### Option 2: Programmatic Usage

For integration into your applications:

```python
from ryoma_ai.agent.sql import SqlAgent
from ryoma_ai.datasource.postgres import PostgresDataSource

# Set up data source
datasource = PostgresDataSource(
    connection_string="postgresql://user:pass@localhost:5432/db"
)

# Create SQL agent (uses default InMemoryStore)
agent = SqlAgent(
    model="gpt-4o",
    mode="enhanced",
    datasource=datasource
)

# Ask questions in natural language
response = agent.stream("Show me the top 10 customers by revenue this month")
print(response)
```

### Option 3: Pandas Agent

For DataFrame analysis:

```python
from ryoma_ai.agent.pandas import PandasAgent
import pandas as pd

# Create sample data
df = pd.DataFrame({
    'customer_id': [1, 2, 3, 4, 5],
    'revenue': [1000, 2500, 1800, 3200, 900],
    'region': ['North', 'South', 'East', 'West', 'North']
})

# Create pandas agent (uses default InMemoryStore)
agent = PandasAgent("gpt-4o")
agent.add_dataframe(df)

# Analyze with natural language
result = agent.stream("What's the average revenue by region?")
print(result)
```

## 🚀 Advanced Features

### Enhanced SQL Agent with Profiling
```python
from ryoma_ai.agent.sql import SqlAgent
from ryoma_ai.datasource.postgres import PostgresDataSource

# Connect to database with automatic profiling
datasource = PostgresDataSource(
    connection_string="postgresql://user:pass@localhost:5432/db"
)

# Use ReFoRCE mode for state-of-the-art performance
agent = SqlAgent(
    model="gpt-4",
    mode="reforce",  # Advanced self-refinement
    safety_config={
        "enable_validation": True,
        "max_retries": 3
    }
)
agent.add_datasource(datasource)

# Complex queries with automatic optimization
response = agent.stream("""
Find customers who made purchases in the last 30 days,
group by region, and show the top 3 products by revenue
""")
```

## 🔧 Configuration

### Environment Variables
```bash
# Set your API key
export OPENAI_API_KEY="your-api-key-here"

# Optional: Configure other providers
export ANTHROPIC_API_KEY="your-anthropic-key"
```

### Agent Configuration
```python
# Custom configuration
agent = SqlAgent(
    model="gpt-4",
    mode="enhanced",
    model_parameters={
        "temperature": 0.1,
        "max_tokens": 2000
    },
    safety_config={
        "enable_validation": True,
        "allowed_operations": ["SELECT", "WITH"],
        "max_rows": 10000
    }
)
```

## ✅ Verify Installation

Run this quick test to ensure everything is working:

```python
from ryoma_ai.agent.sql import SqlAgent
from ryoma_ai.datasource.sqlite import SqliteDataSource

# Create in-memory SQLite database
datasource = SqliteDataSource(":memory:")

# Test agent creation
agent = SqlAgent("gpt-3.5-turbo", mode="enhanced")
agent.add_datasource(datasource)

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

# Ryoma AI

AI-powered data analysis and SQL generation for the Ryoma platform.

Ryoma AI provides:
- **AI Agents** for intelligent data analysis and SQL generation
- **LLM-Enhanced Profiling** for automatic metadata generation
- **Advanced SQL Tools** with safety validation and error recovery
- **Integration with Ryoma Data** for multi-datasource support

## Installation

### Basic Installation
```bash
pip install ryoma_ai
```

Note: Ryoma AI requires `ryoma_data` for datasource connectivity. Install datasource-specific dependencies through `ryoma_data`:

```bash
# Install ryoma_data with database support
pip install ryoma_data[postgres]
pip install ryoma_data[mysql]
pip install ryoma_data[snowflake]
pip install ryoma_data[bigquery]
pip install ryoma_data[duckdb]

# Multiple datasources
pip install ryoma_data[postgres,mysql,duckdb]
```

## Usage

```python
from ryoma_data.postgres import PostgresDataSource
from ryoma_ai.agent.sql import SqlAgent

# Connect to data source
datasource = PostgresDataSource("postgresql://user:password@localhost/db")

# Create AI agent
sql_agent = SqlAgent("gpt-3.5-turbo").add_datasource(datasource)

# Generate and execute SQL
sql_agent.stream("Get the top 10 rows from the data source")
```

## Features

### LLM-Enhanced Profiling
```python
from ryoma_data.postgres import PostgresDataSource
from ryoma_ai.profiling import LLMProfileEnhancer
from ryoma_data.profiler import DatabaseProfiler
from ryoma_ai.llm.provider import load_model_provider

# Statistical profiling
profiler = DatabaseProfiler()
profile = profiler.profile_column(datasource, "customers", "email")

# Add LLM enhancement
model = load_model_provider("openai", model="gpt-4")
enhancer = LLMProfileEnhancer(model=model)
enhanced = enhancer.generate_field_description(profile, "customers")
print(enhanced["description"])
print(enhanced["sql_hints"])
```

### Advanced SQL Agents
- **EnhancedSqlAgent**: Multi-step reasoning with error handling
- **ReFoRCESqlAgent**: State-of-the-art with self-refinement and column exploration
- **Schema Linking**: Intelligent table relationship analysis
- **Safety Validation**: SQL query safety checks and sanitization

## Architecture

Ryoma AI is designed to work seamlessly with Ryoma Data:

- **ryoma_data**: Pure data connectors and statistical profiling (no AI dependencies)
- **ryoma_ai**: AI/LLM logic, agents, and enhanced metadata generation

This separation allows:
- Using ryoma_data standalone without AI dependencies
- Clean testing of data layer without mocking LLMs
- Flexible integration with different AI frameworks

## Documentation
Visit the [documentation](https://project-ryoma.github.io/ryoma/) for more information.

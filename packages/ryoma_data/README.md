# Ryoma Data

Pure data source connectors and statistical profiling for the Ryoma AI Platform.

## Overview

Ryoma Data provides a unified interface for connecting to various data sources and performing statistical profiling operations. It has **zero AI dependencies** and focuses purely on data access and analysis.

## Design Philosophy

- ✅ **Pure Data Layer**: No AI/LLM dependencies
- ✅ **Statistical Focus**: Row counts, distributions, quality metrics
- ✅ **Standalone Usage**: Can be used without ryoma_ai
- ✅ **Framework Agnostic**: Works with any AI framework
- ✅ **Fast & Testable**: No LLM mocking required for tests

## Supported Data Sources

### SQL Databases
- PostgreSQL
- MySQL
- SQLite
- DuckDB
- Snowflake
- BigQuery

### Other Sources
- Apache Iceberg (data lakes)
- DynamoDB (NoSQL)
- CSV, Parquet, JSON files

## Features

### Data Connectivity
- Unified datasource interface
- Automatic schema detection
- Connection pooling and optimization
- Query execution and result handling

### Statistical Profiling
- Row and column counts
- NULL percentage analysis
- Distinct value ratio calculation
- Top-k frequent values
- Min/max/mean for numeric columns
- String length and character type analysis
- Data quality scoring
- LSH-based column similarity analysis
- Basic semantic type inference (rule-based)

### What Ryoma Data Does NOT Include
- ❌ LLM-based metadata generation (use ryoma_ai for this)
- ❌ AI-powered semantic analysis (use ryoma_ai for this)
- ❌ Natural language descriptions (use ryoma_ai for this)
- ❌ SQL generation from natural language (use ryoma_ai for this)

## Installation

```bash
# Base installation
pip install ryoma_data

# With specific database support
pip install ryoma_data[postgres]
pip install ryoma_data[mysql]
pip install ryoma_data[snowflake]
pip install ryoma_data[bigquery]
pip install ryoma_data[duckdb]
pip install ryoma_data[iceberg]

# All databases
pip install ryoma_data[snowflake,postgres,mysql,bigquery,duckdb]
```

## Quick Start

### Basic Usage

```python
from ryoma_data import DataSource

# Connect to PostgreSQL
datasource = DataSource(
    "postgres",
    host="localhost",
    port=5432,
    database="mydb",
    user="user",
    password="pass"
)

# Or use connection URL
datasource = DataSource(
    "postgres",
    connection_url="postgresql://user:pass@localhost:5432/mydb"
)

# Get catalog information
catalog = datasource.get_catalog()
for schema in catalog.schemas:
    print(f"Schema: {schema.schema_name}")
    for table in schema.tables:
        print(f"  Table: {table.table_name}")
        for column in table.columns:
            print(f"    Column: {column.name} ({column.type})")
```

### Statistical Profiling

```python
from ryoma_data import DataSource, DatabaseProfiler

# Create datasource
datasource = DataSource("postgres", host="localhost", database="mydb")

# Create profiler
profiler = DatabaseProfiler(
    sample_size=10000,
    enable_lsh=True
)

# Profile a table
table_profile = profiler.profile_table(datasource, "customers")
print(f"Rows: {table_profile.row_count}")
print(f"Columns: {table_profile.column_count}")
print(f"Completeness: {table_profile.completeness_score:.2%}")

# Profile individual columns
column_profile = profiler.profile_column(
    datasource,
    table_name="customers",
    column_name="email"
)
print(f"Distinct count: {column_profile.distinct_count}")
print(f"NULL percentage: {column_profile.null_percentage:.1f}%")
print(f"Semantic type: {column_profile.semantic_type}")
print(f"Top values: {column_profile.top_k_values}")
```

### Query Execution

```python
# Execute SQL queries
result = datasource.query("SELECT * FROM customers LIMIT 10")
print(result)  # Returns pandas DataFrame or similar

# Get query plans
plan = datasource.get_query_plan("SELECT * FROM customers")
print(plan)
```

## Integration with Ryoma AI

For AI-enhanced features like natural language descriptions and SQL generation, use with `ryoma_ai`:

```python
from ryoma_data import DataSource, DatabaseProfiler
from ryoma_ai.profiling import LLMProfileEnhancer
from ryoma_ai.llm.provider import load_model_provider

# Data layer: Statistical profiling
datasource = DataSource("postgres", host="localhost", database="mydb")
profiler = DatabaseProfiler()
profile = profiler.profile_column(datasource, "customers", "email")

# AI layer: LLM enhancement
model = load_model_provider("openai", model="gpt-4")
enhancer = LLMProfileEnhancer(model=model)
enhanced = enhancer.generate_field_description(profile, "customers")

print(f"Statistics: {profile.distinct_count} distinct values")
print(f"AI Description: {enhanced['description']}")
print(f"SQL Hints: {enhanced['sql_hints']}")
```

## Architecture

Ryoma Data is a pure data layer with no AI dependencies:

```
ryoma_data → Statistical Analysis
     ↓
ryoma_ai (optional) → LLM Enhancement
```

Use ryoma_data standalone for data access and statistical profiling, or combine with ryoma_ai for AI-powered features.

## API Reference

### Core Classes

- **`DataSource`**: Connect to SQL databases (PostgreSQL, MySQL, Snowflake, BigQuery, DuckDB, SQLite)
- **`DatabaseProfiler`**: Analyze tables and columns statistically
- **`Catalog`**: Database catalog structure
- **`Schema`**: Database schema with tables
- **`Table`**: Table with columns and metadata
- **`Column`**: Column with type and constraints

### Connecting to Databases

```python
from ryoma_data import DataSource

# PostgreSQL
ds = DataSource("postgres", host="localhost", port=5432, database="mydb")

# MySQL
ds = DataSource("mysql", host="localhost", user="root", database="mydb")

# Snowflake
ds = DataSource("snowflake", account="myaccount", user="myuser",
                database="mydb", warehouse="compute_wh")

# BigQuery
ds = DataSource("bigquery", project_id="my-project", dataset_id="my_dataset")

# DuckDB (in-memory)
ds = DataSource("duckdb", database=":memory:")

# SQLite
ds = DataSource("sqlite", database="example.db")

# Connection URL
ds = DataSource("postgres", connection_url="postgresql://localhost/mydb")
```

### Using the Factory

```python
from ryoma_data.factory import DataSourceFactory

datasource = DataSourceFactory.create_datasource(
    "postgres",
    host="localhost",
    database="mydb"
)
```

## Testing

Since ryoma_data has no AI dependencies, tests are fast and deterministic:

```python
def test_profiling():
    profiler = DatabaseProfiler()
    profile = profiler.profile_column(datasource, "table", "col")

    assert profile.row_count > 0
    assert profile.distinct_count > 0
    assert 0 <= profile.null_percentage <= 100
    assert profile.semantic_type in ["identifier", "email", "numeric", ...]
```

No LLM mocking required!

## Contributing

When contributing to ryoma_data:

1. ✅ Keep it AI-free (no LLM dependencies)
2. ✅ Focus on data access and statistical analysis
3. ✅ Ensure backward compatibility
4. ✅ Add tests without AI mocking
5. ✅ Document statistical methods clearly

## License

Apache License 2.0

## Links

- **GitHub**: https://github.com/project-ryoma/ryoma
- **Documentation**: https://project-ryoma.github.io/ryoma/
- **Ryoma AI**: For AI-enhanced features
- **Ryoma Lab**: For interactive UI


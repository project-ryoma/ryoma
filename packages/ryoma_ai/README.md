# Ryoma

Ryoma lib is the core component of the project which includes:
- **Data Sources** that can be used to fetch data from different sources
- **Agents** that can be used to process data with AI models
- **Tools** that can be used by agent to process data

## Installation

### Basic Installation
```bash
pip install ryoma_ai
```

### Installing with Optional Dependencies

Ryoma AI uses lazy imports for datasource dependencies, so you only need to install the dependencies for the datasources you plan to use:

```bash
# For PostgreSQL support
pip install ryoma_ai[postgres]

# For MySQL support  
pip install ryoma_ai[mysql]

# For Snowflake support
pip install ryoma_ai[snowflake]

# For BigQuery support
pip install ryoma_ai[bigquery]

# For DuckDB support
pip install ryoma_ai[duckdb]

# For DynamoDB support
pip install ryoma_ai[dynamodb]

# For Apache Iceberg support
pip install ryoma_ai[iceberg]

# For PySpark support
pip install ryoma_ai[pyspark]

# Multiple datasources
pip install ryoma_ai[postgres,mysql,duckdb]
```

## Usage

```python
from ryoma_ai.datasource.postgres import PostgresDataSource
from ryoma_ai.agent.sql import SqlAgent

datasource = PostgresDataSource("postgresql://user:password@localhost/db")
sql_agent = SqlAgent("gpt-3.5-turbo").add_datasource(datasource)
sql_agent.stream("Get the top 10 rows from the data source")
```

## Documentation
Visit the [documentation](https://project-ryoma.github.io/ryoma/) for more information.

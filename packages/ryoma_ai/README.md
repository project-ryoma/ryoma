# Ryoma

Ryoma lib is the core component of the project which includes:
- **Data Sources** that can be used to fetch data from different sources
- **Agents** that can be used to process data with AI models
- **Tools** that can be used by agent to process data

## Installation

```bash
pip install ryoma_ai
```

## Usage

```python
from ryoma_ai.datasource.postgres import PostgresDataSource
from ryoma_ai.agent.sql import SqlAgent

datasource = PostgresDataSource("postgresql://user:password@localhost/db")
sql_agent = SqlAgent("gpt-3.5-turbo")
.add_datasource(datasource)
sql_agent.stream("Get the top 10 rows from the data source")
```

## Documentation
Visit the [documentation](https://project-ryoma.github.io/ryoma/) for more information.

# Aita

Aita lib is the core component of the project which includes:
- **Data Sources** that can be used to fetch data from different sources
- **Agents** that can be used to process data with AI models
- **Tools** that can be used by agent to process data

## Installation

```bash
pip install aita
```

## Usage

```python
from aita.datasource.postgresql import PostgreSqlDataSource
from aita.agent.sql import SqlAgent

datasource = PostgreSqlDataSource("postgresql://user:password@localhost/db")
sql_agent = SqlAgent("gpt-3.5-turbo")
    .add_datasource(datasource)
sql_agent.playground("Get the top 10 rows from the data source")
```

## Documentation
Visit the [documentation](https://aita-1.gitbook.io/aita) for more information.

# Enhanced SQL Agent - Quick Reference

## Quick Start

### Using AgentBuilder (Recommended)

```python
from ryoma_ai.services import AgentBuilder, DataSourceService
from ryoma_ai.infrastructure.datasource_repository import StoreBasedDataSourceRepository
from langchain_core.stores import InMemoryStore
from ryoma_data.sql import DataSource

# Initialize datasource
datasource = DataSource(
    "postgres",
    host="localhost",
    port=5432,
    database="mydb",
    user="user",
    password="password"
)

# Set up services
store = InMemoryStore()
repo = StoreBasedDataSourceRepository(store)
datasource_service = DataSourceService(repo)
datasource_service.add_datasource(datasource)

# Create SQL agent using builder
builder = AgentBuilder(datasource_service)
agent = builder.build_sql_agent(model="gpt-4", mode="enhanced")

# Ask a question
result = agent.stream("Show top 10 customers by revenue")
```

### Direct SqlAgent Factory (Alternative)

```python
from ryoma_ai.agent.sql import SqlAgent
from ryoma_ai.domain.constants import StoreKeys
from langchain_core.stores import InMemoryStore
from ryoma_data.sql import DataSource

# Initialize datasource
datasource = DataSource(
    "postgres",
    host="localhost",
    database="mydb",
    user="user",
    password="password"
)

# Create store and inject datasource
store = InMemoryStore()
store.mset([(StoreKeys.ACTIVE_DATASOURCE, datasource)])

# Create SQL agent with store
agent = SqlAgent(
    model="gpt-4",
    mode="enhanced",  # or "basic" or "reforce"
    store=store
)

# Ask a question
result = agent.stream("Show top 10 customers by revenue")
```

### ReFoRCE Mode (Advanced)

```python
# State-of-the-art SQL agent with ReFoRCE optimizations
agent = builder.build_sql_agent(
    model="gpt-4",
    mode="reforce"
)
```

## Constructor Parameters

### SqlAgent Factory

```python
SqlAgent(
    model: str | BaseChatModel,      # Model ID or LLM instance
    model_parameters: dict = None,    # Optional LLM parameters
    mode: str = "basic",              # "basic", "enhanced", or "reforce"
    safety_config: dict = None,       # Safety configuration (enhanced/reforce only)
    store = None,                     # BaseStore with datasource injected
)
```

### AgentBuilder.build_sql_agent

```python
builder.build_sql_agent(
    model: str = "gpt-3.5-turbo",    # Model ID or LLM instance
    mode: str = "basic",              # "basic", "enhanced", or "reforce"
    model_params: dict = None,        # Optional model parameters
)
```

## Agent Modes Comparison

| Feature | Basic Mode | Enhanced Mode | ReFoRCE Mode |
|---------|------------|---------------|--------------|
| Multi-step reasoning | ❌ | ✅ | ✅ |
| Schema linking | ❌ | ✅ | ✅ |
| Safety validation | ❌ | ✅ | ✅ |
| Error handling | ❌ | ✅ | ✅ |
| Query planning | ❌ | ✅ | ✅ |
| Database compression | ❌ | ❌ | ✅ |
| Format restriction | ❌ | ❌ | ✅ |
| Column exploration | ❌ | ❌ | ✅ |
| Self-refinement | ❌ | ❌ | ✅ |
| Parallel generation | ❌ | ❌ | ✅ |
| Consensus voting | ❌ | ❌ | ✅ |

## Available Tools by Mode

### Basic Mode (3 tools)
- **SqlQueryTool** - Execute SQL queries
- **CreateTableTool** - Create new tables
- **QueryProfileTool** - Profile query execution

### Enhanced Mode (5 tools)
All basic tools plus:
- **QueryExplanationTool** - Explain query execution plans
- **QueryOptimizationTool** - Optimize query performance

### ReFoRCE Mode (5 tools)
Same as enhanced mode (ReFoRCE is a prompting strategy, not different tools)

## Workflow Steps

### Enhanced SQL Agent (8 Steps)

1. **analyze_question** - Understand intent and complexity
2. **schema_linking** - Find relevant tables
3. **query_planning** - Create execution plan
4. **generate_sql** - Generate SQL query
5. **validate_safety** - Security validation
6. **execute_query** - Execute validated query
7. **handle_error** - Error recovery (if needed)
8. **format_response** - Format final answer

### ReFoRCE SQL Agent (7 Steps)

1. **compress_database_info** - Schema compression
2. **generate_format_restriction** - Answer format specification
3. **explore_columns** - Column discovery with feedback
4. **parallel_generation** - Multiple SQL candidates
5. **self_refinement** - Query improvement iterations
6. **consensus_voting** - Majority-vote consensus
7. **final_validation** - Result validation and formatting

## Key Methods

### Agent Methods

```python
# Stream responses (recommended)
result = agent.stream(question, display=True)

# Invoke synchronously
result = agent.invoke(question)

# Async invocation
result = await agent.ainvoke(question)

# Tool execution control
from ryoma_ai.agent.workflow import ToolMode
result = agent.stream(question, tool_mode=ToolMode.ONCE)
result = agent.stream(question, tool_mode=ToolMode.CONTINUOUS)
```

### Enhanced/ReFoRCE Methods

```python
# Safety configuration (enhanced/reforce only)
agent.enable_safety_rule("BLOCK_DELETE")
agent.disable_safety_rule("LIMIT_JOINS")
agent.set_safety_config(new_config)

# Schema analysis (enhanced/reforce only)
analysis = agent.analyze_schema(question)

# Query planning (enhanced/reforce only)
plan = agent.create_query_plan(question, context)
```

## Common Use Cases

### Business Intelligence

```python
# Revenue analysis
result = agent.stream(
    "Show monthly revenue trends for the last 12 months by product category"
)
```

### Customer Analytics

```python
# Customer segmentation
result = agent.stream(
    "Identify top 20% of customers by lifetime value and their characteristics"
)
```

### Operational Reporting

```python
# Performance metrics
result = agent.stream(
    "Calculate average order processing time by region for last quarter"
)
```

## DataSource Configuration

### Supported Backends

```python
from ryoma_data.sql import DataSource

# PostgreSQL
ds = DataSource("postgres", host="localhost", database="mydb", user="user", password="pass")

# MySQL
ds = DataSource("mysql", host="localhost", database="mydb", user="user", password="pass")

# SQLite
ds = DataSource("sqlite", database="path/to/db.sqlite")

# DuckDB
ds = DataSource("duckdb", database=":memory:")

# Snowflake
ds = DataSource("snowflake", account="xxx", database="DB", user="user", password="pass")

# BigQuery
ds = DataSource("bigquery", project_id="project", dataset_id="dataset")
```

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| No active datasource | Datasource not added to service | Call `datasource_service.add_datasource(ds)` |
| Schema loading error | DB connection/permissions | Check datasource configuration |
| Query timeout | Complex query/large dataset | Increase timeout or optimize query |
| Safety violation | Dangerous SQL operation | Review safety configuration |

## Best Practices

### Production Deployment

1. **Use AgentBuilder** - Cleaner separation of concerns
2. **Configure Safety Rules** - Set appropriate safety policies
3. **Set Resource Limits** - Prevent resource exhaustion
4. **Monitor Performance** - Track query execution metrics
5. **Access Control** - Implement proper database permissions

### Performance Optimization

1. **Use ReFoRCE Mode** - For best performance and accuracy on complex queries
2. **Use Enhanced Mode** - For production with safety validation
3. **Use Basic Mode** - For simple queries and development

## Version History

- **v0.2.0** - Service-based architecture with AgentBuilder
- **v0.1.x** - Direct datasource parameter (deprecated)

## Support and Resources

- **Documentation**: [Enhanced SQL Agent Architecture](enhanced-sql-agent.md)
- **Examples**: See `examples/` directory
- **Issues**: Report bugs and feature requests
- **Contributing**: See contribution guidelines

# 🤖 SqlAgent

The SqlAgent is Ryoma's flagship AI agent for natural language database interactions. It supports multiple modes from basic querying to state-of-the-art self-refinement capabilities.

## 🎯 Agent Modes

### Enhanced Mode (Recommended)
Advanced multi-step reasoning with safety validation and error handling.

```python
from ryoma_ai.agent.sql import SqlAgent
from ryoma_data import DataSource

# Create enhanced SQL agent
agent = SqlAgent(
    model="gpt-4",
    mode="enhanced",  # Multi-step reasoning
    safety_config={
        "enable_validation": True,
        "max_retries": 3,
        "allowed_operations": ["SELECT", "WITH", "CTE"]
    }
)

# Connect to database
datasource = DataSource(
    "postgres",
    connection_string="postgresql://user:pass@localhost:5432/db"
)
agent.add_datasource(datasource)

# Ask complex questions
response = agent.stream("""
Show me the top 10 customers by revenue this quarter,
including their growth rate compared to last quarter
""")
```

### ReFoRCE Mode (State-of-the-Art)
Research-based implementation with self-refinement and consensus voting.

```python
# ReFoRCE agent with advanced features
agent = SqlAgent(
    model="gpt-4",
    mode="reforce",  # Self-refinement workflow
    reforce_config={
        "enable_self_refinement": True,
        "parallel_generation": True,
        "consensus_voting": True,
        "exploration_depth": 3
    }
)

# Complex analytical queries
response = agent.stream("""
Analyze customer churn patterns:
1. Identify at-risk customers based on behavior
2. Calculate churn probability by segment
3. Recommend retention strategies
4. Estimate revenue impact of interventions
""")
```

### Basic Mode
Simple query generation for straightforward use cases.

```python
# Basic mode for simple queries
agent = SqlAgent(model="gpt-3.5-turbo", mode="basic")
agent.add_datasource(datasource)

response = agent.stream("Count total orders by month")
```

## 🔧 Configuration Options

### Model Parameters
```python
agent = SqlAgent(
    model="gpt-4",
    model_parameters={
        "temperature": 0.1,        # Low for consistency
        "max_tokens": 2000,        # Sufficient for complex queries
        "top_p": 0.9,
        "frequency_penalty": 0.1
    }
)
```

### Safety Configuration
```python
safety_config = {
    "enable_validation": True,
    "allowed_operations": ["SELECT", "WITH", "CTE", "UNION"],
    "blocked_operations": ["DROP", "DELETE", "UPDATE", "INSERT"],
    "max_rows": 50000,
    "max_execution_time": 300,  # 5 minutes
    "require_where_clause": True,
    "block_cross_database": False
}

agent = SqlAgent(
    model="gpt-4",
    mode="enhanced",
    safety_config=safety_config
)
```

### ReFoRCE Configuration
```python
reforce_config = {
    "enable_self_refinement": True,     # Self-consistency checking
    "parallel_generation": True,        # Generate multiple candidates
    "consensus_voting": True,           # Majority vote selection
    "exploration_depth": 3,             # Column exploration iterations
    "refinement_iterations": 2,         # Self-refinement rounds
    "candidate_count": 3                # Parallel candidates
}

agent = SqlAgent(
    model="gpt-4",
    mode="reforce",
    reforce_config=reforce_config
)
```

## 📊 Methods

### Core Methods

#### `add_datasource(datasource, name=None)`
Add a data source to the agent.

```python
from ryoma_data import DataSource

datasource = DataSource("postgres", connection_string="postgresql://localhost:5432/db")
agent.add_datasource(datasource, name="main_db")
```

#### `stream(question: str) -> str`
Process a natural language question and return SQL results.

```python
response = agent.stream("What are our top selling products this month?")
print(response)
```

#### `get_query_plan(question: str) -> Dict`
Get the query execution plan without running the query.

```python
plan = agent.get_query_plan("Show customer segments by revenue")
print(f"Complexity: {plan['complexity']}")
print(f"Tables: {plan['relevant_tables']}")
```

### Advanced Methods

#### `profile_database() -> Dict`
Get comprehensive database profiling information.

```python
profile = agent.profile_database()
print(f"Tables: {len(profile['tables'])}")
print(f"Total rows: {profile['total_rows']:,}")
```

#### `validate_query(sql: str) -> Dict`
Validate a SQL query against safety policies.

```python
validation = agent.validate_query("SELECT * FROM customers LIMIT 100")
print(f"Valid: {validation['is_valid']}")
print(f"Issues: {validation['issues']}")
```

#### `explain_query(sql: str) -> str`
Get a natural language explanation of a SQL query.

```python
explanation = agent.explain_query("""
SELECT c.name, SUM(o.amount) as revenue
FROM customers c
JOIN orders o ON c.id = o.customer_id
WHERE o.date >= '2024-01-01'
GROUP BY c.name
ORDER BY revenue DESC
LIMIT 10
""")
print(explanation)
```

#### `optimize_query(sql: str) -> Dict`
Get query optimization suggestions.

```python
optimization = agent.optimize_query("SELECT * FROM large_table WHERE status = 'active'")
print(f"Optimized SQL: {optimization['optimized_sql']}")
print(f"Improvements: {optimization['improvements']}")
```

## 🛡️ Safety Features

### Validation Rules
The agent automatically validates queries against configurable rules:

- **Operation filtering** - Allow/block specific SQL operations
- **Row limits** - Prevent queries returning too many rows
- **Execution time limits** - Timeout long-running queries
- **Cross-database restrictions** - Block queries across databases
- **WHERE clause requirements** - Ensure data filtering

### Error Handling
Automatic error recovery with intelligent retry logic:

```python
# Automatic error handling
try:
    response = agent.stream("Complex analytical query")
except Exception as e:
    # Agent automatically retries with refined query
    print(f"Query succeeded after retry: {response}")
```

## 📈 Performance Features

### Database Profiling
Use profiling for better query generation:

```python
from ryoma_data import DataSource, DatabaseProfiler

datasource = DataSource("postgres", connection_string="postgresql://localhost:5432/db")

# Profile tables
profiler = DatabaseProfiler(
    sample_size=10000,
    enable_lsh=True
)
profile = profiler.profile_table(datasource, "customers")
```

### Query Optimization
Automatic query optimization based on database statistics:

- **Index usage hints** from cardinality analysis
- **Join optimization** using similarity analysis
- **Predicate pushdown** based on data distribution
- **Resource estimation** from statistical data

## 🔍 Monitoring and Debugging

### Enable Logging
```python
import logging

# Enable detailed logging
logging.basicConfig(level=logging.INFO)
ryoma_logger = logging.getLogger('ryoma_ai')
ryoma_logger.setLevel(logging.DEBUG)
```

### Performance Monitoring
```python
from ryoma_ai.monitoring import PerformanceMonitor

monitor = PerformanceMonitor(
    track_query_time=True,
    track_model_calls=True,
    export_metrics=True
)

agent = SqlAgent(
    model="gpt-4",
    mode="enhanced",
    monitor=monitor
)
```

## 🎯 Best Practices

### 1. **Choose the Right Mode**
- **Basic**: Simple queries, development
- **Enhanced**: Production use, complex analysis
- **ReFoRCE**: Maximum accuracy, research applications

### 2. **Configure Safety Appropriately**
- Always enable validation in production
- Set reasonable row and time limits
- Block dangerous operations

### 3. **Use Database Profiling**
- Profile tables for better query generation
- Use appropriate sample sizes
- Enable LSH for column similarity

### 4. **Structure Questions Well**
- Be specific about desired output format
- Include relevant business context
- Break down complex multi-part questions

### 5. **Monitor Performance**
- Track query execution times
- Monitor model API usage
- Set up alerts for failures

## 🔗 Related Documentation

- **[Database Profiling](../profiling/index.md)** - Metadata extraction system
- **[Data Sources](../data-sources/index.md)** - Database connectors
- **[Tools](../tool/index.md)** - Specialized analysis tools
- **[Advanced Setup](../../getting-started/advanced-setup.md)** - Production configuration


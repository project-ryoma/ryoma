# Enhanced SQL Agent - Quick Reference

## Quick Start

### Basic Usage

```python
from ryoma_ai.agent.sql import SqlAgent
from ryoma_ai.datasource.sql import SqlDataSource

# Initialize datasource
datasource = SqlDataSource(connection_string="your_db_connection")

# Create enhanced SQL agent
sql_agent = SqlAgent(
    model="gpt-4",
    datasource=datasource,
    use_enhanced_mode=True
)

# Ask a question
result = sql_agent.invoke({
    "messages": [{"role": "user", "content": "Show top 10 customers by revenue"}]
})
```

### ReFoRCE Mode (Advanced)

```python
# State-of-the-art SQL agent with ReFoRCE optimizations
sql_agent = SqlAgent(
    model="gpt-4",
    datasource=datasource,
    use_reforce_mode=True,
    max_parallel_threads=3,
    max_refinement_iterations=5
)
```

## Configuration Options

### Safety Configuration

```python
safety_config = {
    "max_result_rows": 1000,           # Limit result rows
    "blocked_functions": [             # Dangerous SQL functions
        "DROP", "DELETE", "UPDATE", 
        "LOAD_FILE", "INTO OUTFILE"
    ],
    "allowed_schemas": [               # Restrict schema access
        "public", "analytics"
    ],
    "query_timeout": 30,               # Query timeout in seconds
    "max_joins": 5,                    # Maximum number of joins
    "safety_level": "STRICT"           # PERMISSIVE, MODERATE, STRICT
}

sql_agent = SqlAgent(
    model="gpt-4",
    datasource=datasource,
    use_enhanced_mode=True,
    safety_config=safety_config
)
```

### ReFoRCE Configuration

```python
reforce_config = {
    "max_parallel_threads": 3,         # Parallel SQL generation
    "max_refinement_iterations": 5,    # Self-refinement iterations
    "compression_threshold": 30000,    # Schema compression threshold (tokens)
}

sql_agent = SqlAgent(
    model="gpt-4",
    datasource=datasource,
    use_reforce_mode=True,
    **reforce_config
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

## Key Components

### Specialized Agents

- **SchemaLinkingAgent** - Intelligent table discovery
- **QueryPlannerAgent** - Query complexity analysis and planning
- **SqlErrorHandler** - Error recovery and correction
- **SqlSafetyValidator** - Security and safety validation

### Enhanced Tools

- **SqlQueryTool** - Query execution with safety
- **SchemaAnalysisTool** - Schema relationship analysis
- **QueryValidationTool** - SQL syntax/semantic validation
- **TableSelectionTool** - Relevant table suggestions
- **QueryOptimizationTool** - Performance optimization
- **QueryExplanationTool** - Natural language explanations

## Safety Features

### Security Validation

- SQL injection prevention
- Dangerous operation blocking
- Resource limit enforcement
- Access control validation

### Error Classification

- **Syntax Errors** - Invalid SQL syntax
- **Semantic Errors** - Logical errors
- **Permission Errors** - Access violations
- **Data Errors** - Data-related issues
- **Performance Errors** - Resource/timeout issues

## Performance Features

### ReFoRCE Optimizations

- **Database Compression** - Reduce schema size for large databases
- **Parallel Processing** - Generate multiple SQL candidates simultaneously
- **Self-Refinement** - Iteratively improve query quality
- **Consensus Mechanism** - Use majority vote for best results

### Query Optimization

- Index usage analysis
- Join optimization suggestions
- Performance estimation
- Resource usage monitoring

## Common Use Cases

### Business Intelligence

```python
# Revenue analysis
result = sql_agent.invoke({
    "messages": [{"role": "user", "content": 
        "Show monthly revenue trends for the last 12 months by product category"
    }]
})
```

### Customer Analytics

```python
# Customer segmentation
result = sql_agent.invoke({
    "messages": [{"role": "user", "content": 
        "Identify top 20% of customers by lifetime value and their characteristics"
    }]
})
```

### Operational Reporting

```python
# Performance metrics
result = sql_agent.invoke({
    "messages": [{"role": "user", "content": 
        "Calculate average order processing time by region for last quarter"
    }]
})
```

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Schema loading error | DB connection/permissions | Check datasource configuration |
| Query timeout | Complex query/large dataset | Increase timeout or optimize query |
| Safety violation | Dangerous SQL operation | Review safety configuration |
| Memory issues | Large schema | Enable schema compression |

### Debug Mode

```python
sql_agent = SqlAgent(
    model="gpt-4",
    datasource=datasource,
    use_enhanced_mode=True,
    debug=True,
    log_level="DEBUG"
)
```

## Best Practices

### Production Deployment

1. **Configure Safety Rules** - Set appropriate safety policies
2. **Set Resource Limits** - Prevent resource exhaustion
3. **Monitor Performance** - Track query execution metrics
4. **Regular Testing** - Test with your specific schema
5. **Access Control** - Implement proper database permissions

### Performance Optimization

1. **Use ReFoRCE Mode** - For best performance and accuracy
2. **Enable Compression** - For large database schemas
3. **Tune Parallel Threads** - Based on your system capacity
4. **Monitor Resource Usage** - Optimize based on metrics

### Security Considerations

1. **Principle of Least Privilege** - Minimal database permissions
2. **Input Validation** - Validate all user inputs
3. **Audit Logging** - Log all query executions
4. **Regular Updates** - Keep system updated

## API Reference

### SqlAgent Methods

```python
# Initialize agent
sql_agent = SqlAgent(model, datasource, **config)

# Process question
result = sql_agent.invoke(input_data, **kwargs)

# Stream responses
for chunk in sql_agent.stream(input_data, **kwargs):
    print(chunk)

# Safety configuration
sql_agent.enable_safety_rule("BLOCK_DELETE")
sql_agent.disable_safety_rule("LIMIT_JOINS")
sql_agent.set_safety_config(new_config)

# Schema analysis
analysis = sql_agent.analyze_schema(question)

# Query planning
plan = sql_agent.create_query_plan(question, context)
```

### State Management

```python
# Access workflow state
state = sql_agent.get_current_state()

# Check execution status
status = state.get("current_step")
errors = state.get("error_info")
results = state.get("execution_result")
```

## Support and Resources

- **Documentation**: [Enhanced SQL Agent Architecture](enhanced-sql-agent.md)
- **Examples**: See `examples/` directory
- **Issues**: Report bugs and feature requests
- **Contributing**: See contribution guidelines

## Version History

- **v1.0.0** - Initial Enhanced SQL Agent implementation
- **v1.1.0** - Added ReFoRCE optimizations
- **v1.2.0** - Improved safety validation and error handling

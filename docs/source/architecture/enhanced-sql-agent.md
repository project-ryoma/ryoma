# Enhanced SQL Agent Architecture

## Overview

The Enhanced SQL Agent is a state-of-the-art Text-to-SQL system that combines cutting-edge research insights with enterprise-grade reliability, safety, and performance. It implements a sophisticated multi-step reasoning workflow with intelligent schema analysis, advanced error handling, and comprehensive safety validation.

## Research Foundation

This implementation is based on two key research papers:

### 1. "Automatic Metadata Extraction for Text-to-SQL" (arXiv:2505.19988)
- **Database Profiling**: Systematic querying to gather statistics about tables and fields
- **Novel Schema Linking**: Using LLM SQL generation capability for high-recall schema element identification
- **Query Log Analysis**: Extracting metadata from historical SQL queries written by experts
- **SQL-to-Text Generation**: Creating natural language questions from SQL for training data

### 2. "ReFoRCE: A Text-to-SQL Agent with Self-Refinement, Format Restriction, and Column Exploration"
- **Database Information Compression**: Pattern-based table grouping to reduce schema size
- **Expected Answer Format Restriction**: LLM-generated format specifications
- **Iterative Column Exploration**: Execution-feedback driven column discovery
- **Self-Refinement Workflow**: Multi-iteration query improvement with self-consistency
- **Parallelization with Consensus**: Multiple candidates with majority-vote consensus

## Architecture Components

### Core Agents

#### EnhancedSqlAgent
The main orchestrator that implements the multi-step reasoning workflow.

**Key Features:**
- Multi-step reasoning with state management
- Intelligent schema linking and table selection
- Comprehensive safety validation
- Advanced error handling and recovery
- Query optimization and performance analysis

#### ReFoRCESqlAgent
Advanced implementation incorporating ReFoRCE methodology for state-of-the-art performance.

**Key Features:**
- Database information compression
- Expected answer format restriction
- Iterative column exploration with execution feedback
- Self-refinement workflow with self-consistency
- Parallelization with majority-vote consensus

### Specialized Sub-Agents

#### SchemaLinkingAgent
Analyzes database schema and identifies relevant tables using intelligent algorithms.

**Capabilities:**
- Schema relationship analysis
- Table relevance scoring
- Column significance assessment
- Join path discovery

#### QueryPlannerAgent
Creates structured execution plans and analyzes query complexity.

**Capabilities:**
- Query complexity analysis (Simple, Medium, Complex, Very Complex)
- Multi-step query planning
- Dependency identification
- Performance estimation

#### SqlErrorHandler
Handles errors with intelligent recovery strategies.

**Capabilities:**
- Error classification (Syntax, Semantic, Permission, Data, Performance)
- Automatic query correction
- Recovery strategy suggestions
- Context-aware error analysis

#### SqlSafetyValidator
Validates queries for security and safety compliance.

**Capabilities:**
- Multi-level security validation
- SQL injection prevention
- Resource limit enforcement
- Configurable safety policies

### Enhanced Tools

#### Core SQL Tools
- **SqlQueryTool**: Executes SQL queries with safety checks
- **CreateTableTool**: Creates database tables
- **QueryProfileTool**: Profiles query performance

#### Advanced Analysis Tools
- **SchemaAnalysisTool**: Analyzes database schema relationships
- **QueryValidationTool**: Validates SQL syntax and semantics
- **TableSelectionTool**: Suggests relevant tables for queries
- **QueryOptimizationTool**: Provides performance optimization suggestions
- **QueryExplanationTool**: Explains SQL queries in natural language

## Workflow Architecture

### Enhanced SQL Agent Workflow

![Enhanced SQL Agent Workflow](enhanced-sql-agent-workflow.mmd)

The Enhanced SQL Agent follows an 8-step workflow:

1. **Question Analysis** - Understands user intent and query complexity
2. **Schema Linking** - Identifies relevant tables using intelligent algorithms
3. **Query Planning** - Creates structured execution plans
4. **SQL Generation** - Generates optimized SQL queries
5. **Safety Validation** - Comprehensive security and safety checks
6. **Query Execution** - Executes validated queries
7. **Error Handling** - Intelligent error recovery and correction
8. **Response Formatting** - User-friendly result presentation

### ReFoRCE Workflow

![ReFoRCE SQL Agent Workflow](reforce-sql-agent-workflow.mmd)

The ReFoRCE agent implements an advanced workflow with additional optimizations:

1. **Database Information Compression** - Pattern-based schema compression
2. **Format Restriction Generation** - Expected answer format specification
3. **Column Exploration** - Iterative column discovery with feedback
4. **Parallel Generation** - Multiple SQL candidates in parallel
5. **Self-Refinement** - Multi-iteration query improvement
6. **Consensus Voting** - Majority-vote consensus mechanism
7. **Final Validation** - Comprehensive result validation

### Overall Architecture

![SQL Agent Architecture Overview](sql-agent-architecture.mmd)

## State Management

The agents maintain comprehensive state throughout the workflow:

```python
class SqlAgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    original_question: str
    current_step: str
    schema_analysis: Optional[Dict]
    relevant_tables: Optional[List[Dict]]
    query_plan: Optional[Dict]
    generated_sql: Optional[str]
    validation_result: Optional[Dict]
    execution_result: Optional[str]
    error_info: Optional[Dict]
    safety_check: Optional[Dict]
    final_answer: Optional[str]
    retry_count: int
    max_retries: int
```

### ReFoRCE Extended State

```python
class ReFoRCESqlAgentState(SqlAgentState):
    compressed_schema: Optional[str]
    format_restriction: Optional[FormatRestriction]
    column_exploration: Optional[ColumnExplorationResult]
    self_refinement_iterations: int
    parallel_candidates: List[Dict[str, Any]]
    consensus_result: Optional[str]
    confidence_score: float
```

## Safety and Security Features

### Multi-Level Safety Validation

1. **Syntax Validation**: Checks for valid SQL syntax
2. **Security Validation**: Prevents dangerous operations
3. **Access Control**: Enforces data access policies
4. **Resource Limits**: Prevents resource-intensive queries

### Configurable Safety Policies

```python
safety_config = {
    "max_result_rows": 1000,
    "blocked_functions": ["DROP", "DELETE", "UPDATE"],
    "allowed_schemas": ["public", "analytics"],
    "query_timeout": 30,
    "max_joins": 5
}
```

### Error Classification

- **Syntax Errors**: Invalid SQL syntax
- **Semantic Errors**: Valid syntax but logical errors
- **Permission Errors**: Access control violations
- **Data Errors**: Data-related issues
- **Performance Errors**: Resource or timeout issues

## Performance Optimizations

### Database Schema Compression

- Pattern-based table grouping
- Representative table selection
- Token limit management
- Intelligent schema reduction

### Parallel Processing

- Multiple SQL candidate generation
- Concurrent query execution
- Majority-vote consensus
- Confidence scoring

### Query Optimization

- Performance analysis
- Index usage suggestions
- Join optimization
- Query rewriting recommendations

## Usage Examples

### Basic Enhanced Mode

```python
from ryoma_ai.agent.sql import SqlAgent

# Initialize with enhanced capabilities
sql_agent = SqlAgent(
    model="gpt-4",
    datasource=datasource,
    use_enhanced_mode=True,
    safety_config={
        "max_result_rows": 1000,
        "blocked_functions": ["DROP", "DELETE"]
    }
)

# Process a question
result = sql_agent.invoke({
    "messages": [HumanMessage(content="Show top 10 customers by revenue")]
})
```

### ReFoRCE Mode (State-of-the-Art)

```python
# Initialize with ReFoRCE optimizations
sql_agent = SqlAgent(
    model="gpt-4",
    datasource=datasource,
    use_reforce_mode=True,
    max_parallel_threads=3,
    max_refinement_iterations=5,
    compression_threshold=30000
)

# Process complex queries with advanced reasoning
result = sql_agent.invoke({
    "messages": [HumanMessage(content="Calculate customer lifetime value by segment")]
})
```

### Advanced Configuration

```python
# Custom safety configuration
safety_config = {
    "max_result_rows": 5000,
    "blocked_functions": ["LOAD_FILE", "INTO OUTFILE"],
    "allowed_schemas": ["sales", "marketing"],
    "query_timeout": 60,
    "max_joins": 10,
    "safety_level": "STRICT"
}

# Initialize with custom settings
sql_agent = SqlAgent(
    model="gpt-4-turbo",
    datasource=datasource,
    use_reforce_mode=True,
    safety_config=safety_config,
    max_parallel_threads=5,
    max_refinement_iterations=3
)
```

## Integration Points

### Database Connections

The agents support multiple database types through the SqlDataSource interface:
- PostgreSQL
- MySQL
- SQLite
- SQL Server
- Oracle
- Snowflake

### Model Integration

Compatible with various language models:
- OpenAI GPT models (GPT-3.5, GPT-4)
- Anthropic Claude models
- Local models via Ollama
- Azure OpenAI Service

### Monitoring and Logging

Built-in monitoring capabilities:
- Query execution metrics
- Error tracking and analysis
- Performance monitoring
- Safety violation logging

## Best Practices

### Production Deployment

1. **Safety First**: Always configure appropriate safety rules
2. **Resource Limits**: Set reasonable query timeouts and result limits
3. **Access Control**: Implement proper database access controls
4. **Monitoring**: Set up comprehensive monitoring and alerting
5. **Testing**: Thoroughly test with your specific database schema

### Performance Optimization

1. **Schema Analysis**: Regularly analyze and optimize database schema
2. **Index Management**: Ensure proper indexing for common query patterns
3. **Query Caching**: Implement query result caching where appropriate
4. **Resource Monitoring**: Monitor database resource usage

### Security Considerations

1. **Principle of Least Privilege**: Grant minimal necessary database permissions
2. **Input Validation**: Validate all user inputs
3. **Audit Logging**: Log all query executions for audit purposes
4. **Regular Updates**: Keep the system updated with latest security patches

## Troubleshooting

### Common Issues

1. **Schema Loading Errors**: Check database connectivity and permissions
2. **Query Timeout**: Adjust timeout settings or optimize queries
3. **Safety Violations**: Review and adjust safety configuration
4. **Memory Issues**: Consider schema compression for large databases

### Debug Mode

Enable debug mode for detailed logging:

```python
sql_agent = SqlAgent(
    model="gpt-4",
    datasource=datasource,
    use_enhanced_mode=True,
    debug=True,
    log_level="DEBUG"
)
```

## Future Enhancements

### Planned Features

1. **Advanced Caching**: Intelligent query result caching
2. **Query Optimization**: ML-based query optimization
3. **Multi-Database Support**: Cross-database query capabilities
4. **Natural Language Explanations**: Enhanced result explanations
5. **Interactive Query Building**: Step-by-step query construction

### Research Integration

Continuous integration of latest research:
- New schema linking algorithms
- Advanced error correction techniques
- Improved safety validation methods
- Performance optimization strategies

## Contributing

For information on contributing to the Enhanced SQL Agent, please see the [Contribution Guidelines](../contribution/README.md).

## References

1. "Automatic Metadata Extraction for Text-to-SQL" (arXiv:2505.19988)
2. "ReFoRCE: A Text-to-SQL Agent with Self-Refinement, Format Restriction, and Column Exploration"
3. [Snowflake Labs ReFoRCE Implementation](https://github.com/Snowflake-Labs/ReFoRCE)

# Enhanced SQL Agent Architecture Documentation

This directory contains comprehensive documentation for the Enhanced SQL Agent system, including architectural diagrams, technical specifications, and usage guides.

## Documentation Files

### Core Documentation

- **[enhanced-sql-agent.md](enhanced-sql-agent.md)** - Complete technical architecture documentation
- **[sql-agent-quick-reference.md](sql-agent-quick-reference.md)** - Quick start guide and API reference
- **[index.md](index.md)** - Architecture documentation index

### Workflow Diagrams (Mermaid Format)

- **[enhanced-sql-agent-workflow.mmd](enhanced-sql-agent-workflow.mmd)** - Enhanced SQL Agent 8-step workflow
- **[reforce-sql-agent-workflow.mmd](reforce-sql-agent-workflow.mmd)** - ReFoRCE agent advanced workflow
- **[sql-agent-architecture.mmd](sql-agent-architecture.mmd)** - Overall system architecture overview

## Viewing Diagrams

### Online Mermaid Viewers

You can view the `.mmd` diagram files using online Mermaid viewers:

1. **Mermaid Live Editor**: https://mermaid.live/
2. **GitHub**: GitHub automatically renders Mermaid diagrams in markdown files
3. **VS Code**: Use the "Mermaid Preview" extension

### Local Rendering

To render diagrams locally:

```bash
# Install Mermaid CLI
npm install -g @mermaid-js/mermaid-cli

# Render to SVG
mmdc -i enhanced-sql-agent-workflow.mmd -o enhanced-sql-agent-workflow.svg

# Render to PNG
mmdc -i enhanced-sql-agent-workflow.mmd -o enhanced-sql-agent-workflow.png
```

### Integration with Documentation

The diagrams are referenced in the main documentation files and can be embedded in various formats:

```markdown
# In Markdown
![Enhanced SQL Agent Workflow](enhanced-sql-agent-workflow.mmd)

# In reStructuredText
.. mermaid:: enhanced-sql-agent-workflow.mmd
```

## Architecture Overview

### Enhanced SQL Agent

The Enhanced SQL Agent implements a sophisticated 8-step workflow:

1. **Question Analysis** - Intent understanding and complexity assessment
2. **Schema Linking** - Intelligent table and column discovery
3. **Query Planning** - Structured execution plan creation
4. **SQL Generation** - Context-aware query generation
5. **Safety Validation** - Comprehensive security checks
6. **Query Execution** - Safe query execution with monitoring
7. **Error Handling** - Intelligent error recovery and correction
8. **Response Formatting** - User-friendly result presentation

### ReFoRCE Optimizations

The ReFoRCE agent adds advanced optimizations:

1. **Database Compression** - Pattern-based schema size reduction
2. **Format Restriction** - Expected answer format specification
3. **Column Exploration** - Iterative discovery with execution feedback
4. **Parallel Generation** - Multiple SQL candidates simultaneously
5. **Self-Refinement** - Multi-iteration query improvement
6. **Consensus Voting** - Majority-vote result selection
7. **Final Validation** - Comprehensive result validation

## Research Foundation

This implementation is based on two key research papers:

### "Automatic Metadata Extraction for Text-to-SQL" (arXiv:2505.19988)

Key contributions integrated:
- Database profiling for metadata generation
- Novel schema linking using LLM capabilities
- Query log analysis for insight extraction
- SQL-to-text generation for training data

### "ReFoRCE: A Text-to-SQL Agent with Self-Refinement, Format Restriction, and Column Exploration"

Key innovations implemented:
- Database information compression techniques
- Expected answer format restriction
- Iterative column exploration with feedback
- Self-refinement workflow with consistency checks
- Parallelization with majority-vote consensus

## Key Components

### Specialized Agents

- **SchemaLinkingAgent** - Advanced schema analysis and table discovery
- **QueryPlannerAgent** - Query complexity analysis and execution planning
- **SqlErrorHandler** - Intelligent error classification and recovery
- **SqlSafetyValidator** - Multi-level security and safety validation

### Enhanced Tools

- **SqlQueryTool** - Safe query execution with monitoring
- **SchemaAnalysisTool** - Database schema relationship analysis
- **QueryValidationTool** - SQL syntax and semantic validation
- **TableSelectionTool** - Intelligent table relevance scoring
- **QueryOptimizationTool** - Performance optimization suggestions
- **QueryExplanationTool** - Natural language query explanations

## Safety and Security

### Multi-Level Validation

1. **Syntax Validation** - SQL syntax correctness
2. **Security Validation** - Dangerous operation prevention
3. **Access Control** - Permission and policy enforcement
4. **Resource Limits** - Query timeout and result size limits

### Configurable Policies

```python
safety_config = {
    "max_result_rows": 1000,
    "blocked_functions": ["DROP", "DELETE", "UPDATE"],
    "allowed_schemas": ["public", "analytics"],
    "query_timeout": 30,
    "safety_level": "STRICT"
}
```

## Performance Features

### ReFoRCE Optimizations

- **Schema Compression** - Reduces large schema sizes for better performance
- **Parallel Processing** - Generates multiple SQL candidates simultaneously
- **Self-Refinement** - Iteratively improves query quality and accuracy
- **Consensus Mechanism** - Uses majority voting for optimal results

### Query Optimization

- Index usage analysis and recommendations
- Join optimization and query rewriting suggestions
- Performance estimation and resource monitoring
- Caching strategies for frequently used queries

## Usage Modes

### Basic Mode
- Simple SQL query generation
- Basic error handling
- Standard safety checks

### Enhanced Mode
- Multi-step reasoning workflow
- Advanced schema linking
- Comprehensive error handling
- Intelligent query planning

### ReFoRCE Mode (State-of-the-Art)
- All enhanced mode features
- Database compression
- Format restriction
- Column exploration
- Self-refinement
- Parallel generation
- Consensus voting

## Integration

### Database Support

- PostgreSQL
- MySQL
- SQLite
- SQL Server
- Oracle
- Snowflake

### Model Support

- OpenAI GPT models (GPT-3.5, GPT-4)
- Anthropic Claude models
- Local models via Ollama
- Azure OpenAI Service

## Contributing

When contributing to the Enhanced SQL Agent documentation:

1. **Update Diagrams** - Modify `.mmd` files for architectural changes
2. **Maintain Consistency** - Keep documentation synchronized with code
3. **Test Examples** - Verify all code examples work correctly
4. **Review Process** - Follow the standard review process for documentation changes

## Support

For questions, issues, or contributions related to the Enhanced SQL Agent:

- **Documentation Issues** - Report in the main repository
- **Feature Requests** - Use the issue tracker
- **Technical Questions** - Check the quick reference guide first

## Version History

- **v1.0.0** - Initial Enhanced SQL Agent documentation
- **v1.1.0** - Added ReFoRCE optimizations and diagrams
- **v1.2.0** - Comprehensive architecture documentation and quick reference

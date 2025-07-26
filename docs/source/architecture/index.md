(ryoma-architecture)=

# Architecture

Ryoma architecture diagram documentation.

## Enhanced SQL Agent

The Enhanced SQL Agent is a state-of-the-art Text-to-SQL system that combines cutting-edge research insights with enterprise-grade reliability, safety, and performance.

### Key Features

- **Multi-step reasoning** with intelligent workflow management
- **Advanced schema linking** using research-based algorithms
- **Comprehensive safety validation** with configurable policies
- **Intelligent error handling** with automatic recovery
- **ReFoRCE optimizations** for state-of-the-art performance

### Documentation

- **[Enhanced SQL Agent Architecture](enhanced-sql-agent.md)** - Comprehensive technical documentation
- **[Database Profiling System](database-profiling.md)** - Comprehensive metadata extraction and profiling
- **[Quick Reference Guide](sql-agent-quick-reference.md)** - Quick start and API reference
- **[Workflow Diagrams](enhanced-sql-agent-workflow.mmd)** - Visual workflow representations

## Database Profiling System

The Database Profiling System implements comprehensive metadata extraction based on research from the "Automatic Metadata Extraction for Text-to-SQL" paper.

### Key Features

- **Statistical Analysis** - Row counts, NULL statistics, distinct-value ratios
- **Type-Specific Profiling** - Numeric, date, and string analysis
- **Semantic Type Inference** - Automatic detection of emails, phones, URLs, etc.
- **Data Quality Scoring** - Multi-dimensional quality assessment
- **LSH Similarity** - Locality-sensitive hashing for column similarity
- **Top-k Frequent Values** - Most common data patterns

```{toctree}
:maxdepth: 2

architecture
enhanced-sql-agent
database-profiling
sql-agent-quick-reference
```

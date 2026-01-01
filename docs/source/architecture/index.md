(ryoma-architecture)=

# Architecture

Comprehensive documentation for Ryoma's architecture and design patterns.

## Platform Architecture

The platform is organized into three distinct packages with clear separation of concerns:
- **ryoma_data** - Data layer with connectors and profiling
- **ryoma_ai** - AI layer with LLM agents and analysis
- **ryoma_lab** - UI layer with interactive interfaces

**[View Complete Architecture Guide →](architecture.md)**

## Enhanced SQL Agent

The Enhanced SQL Agent combines cutting-edge research with enterprise reliability for Text-to-SQL tasks.

### Key Features

- Multi-step reasoning with intelligent workflow
- Advanced schema linking algorithms
- Comprehensive safety validation
- Intelligent error handling with auto-recovery
- ReFoRCE optimizations for state-of-the-art performance

**[View Enhanced SQL Agent Documentation →](enhanced-sql-agent.md)**

## Database Profiling System

Comprehensive metadata extraction based on research from "Automatic Metadata Extraction for Text-to-SQL".

### Key Features

- Statistical analysis (row counts, NULL stats, distinct-value ratios)
- Type-specific profiling (numeric, date, string)
- Semantic type inference (emails, phones, URLs)
- Data quality scoring
- LSH-based column similarity
- Top-k frequent values

**[View Database Profiling Documentation →](database-profiling.md)**

## Store Architecture

Unified storage system separating metadata, vectors, and data sources.

### Three-Store Architecture

- **Metadata Store** - Structured metadata, configuration, and state
- **Vector Store** - Semantic search and embeddings
- **Data Sources** - Actual database connections

**[View Store Architecture Documentation →](store-architecture.md)**

```{toctree}
:maxdepth: 2

architecture
store-architecture
enhanced-sql-agent
database-profiling
sql-agent-quick-reference
```

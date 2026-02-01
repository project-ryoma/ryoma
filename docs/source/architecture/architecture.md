# Architecture

## User API

The `Ryoma` class is the main entry point for users:

```python
from ryoma_ai import Ryoma
from ryoma_data import DataSource

# Connect to a database
datasource = DataSource("postgres", host="localhost", database="mydb", user="user", password="pass")
ryoma = Ryoma(datasource=datasource)

# Create agents
sql_agent = ryoma.sql_agent(model="gpt-4", mode="enhanced")
pandas_agent = ryoma.pandas_agent(model="gpt-4")

# Multiple datasources
ryoma.add_datasource(another_datasource, name="analytics")
ryoma.set_active("analytics")
```

## Internal Architecture

Ryoma is organized into three distinct packages with clear separation of concerns:

```
ryoma/
├── packages/
│   ├── ryoma_data/      # Data layer: Connectors & profiling
│   ├── ryoma_ai/        # AI layer: LLM agents & analysis
│   └── ryoma_lab/       # UI layer: Interactive interfaces
```

## Package Architecture

### 1. ryoma_data (Data Layer)

**Core Components:**

```
ryoma_data/
├── base.py              # Abstract DataSource interface
├── sql.py               # Unified SQL datasource
├── metadata.py          # Catalog, Schema, Table, Column models
├── profiler.py          # Statistical profiling
└── factory.py           # Datasource factory
```

**Capabilities:**
- Database connections and query execution
- Schema introspection and catalog management
- Statistical profiling (row counts, null %, distinct ratios, etc.)
- Data quality scoring
- LSH-based column similarity
- Semantic type inference (rule-based)

### 2. ryoma_ai (AI Layer)

**Core Components:**

```
ryoma_ai/
├── agent/               # AI agents
│   ├── sql.py          # SQL generation agents
│   ├── workflow.py     # Base workflow agent
│   └── internals/      # Specialized agents
│       ├── enhanced_sql_agent.py
│       ├── reforce_sql_agent.py
│       ├── query_planner.py
│       ├── schema_linking_agent.py
│       ├── sql_error_handler.py
│       ├── sql_safety_validator.py
│       └── metadata_manager.py
├── profiling/          # LLM-enhanced profiling
│   └── llm_enhancer.py
├── tool/               # Agent tools
│   ├── sql_tool.py
│   ├── pandas_tool.py
│   └── preprocess_tools.py
├── llm/                # LLM provider abstractions
│   └── provider.py
└── utils/              # Utilities
    └── datasource_utils.py
```

**Capabilities:**
- LLM-based metadata enhancement
- SQL generation from natural language
- Multi-step query planning
- Schema linking and relationship analysis
- SQL error handling and recovery
- Query safety validation
- Agent orchestration

### 3. ryoma_lab (UI Layer)

Interactive user interfaces built with Reflex.

## Design Patterns

### Unified Datasource Pattern

```python
from ryoma_data import DataSource

# Single class for all SQL databases
datasource = DataSource(
    "postgres",
    host="localhost",
    database="mydb"
)
```

### Separation of Profiling

```python
from ryoma_data import DataSource, DatabaseProfiler

# Statistical profiling (data layer)
datasource = DataSource("postgres", connection_string="...")
profiler = DatabaseProfiler(sample_size=10000)
profile = profiler.profile_table(datasource, "customers")

# LLM enhancement (AI layer)
from ryoma_ai.profiling import LLMProfileEnhancer
enhancer = LLMProfileEnhancer(model=llm_model)
enhanced = enhancer.generate_field_description(profile, "customers")
```

### Type Guards

```python
from ryoma_ai.utils import is_sql_datasource, ensure_sql_datasource

# Type guard for static type checking
if is_sql_datasource(datasource):
    result = datasource.query(sql)

# Runtime validation
sql_ds = ensure_sql_datasource(datasource)
result = sql_ds.query(sql)
```

## Data Flow

### Basic Query Flow
```
User Question
     ↓
[ryoma_ai Agent]
     ↓
Schema Analysis (ryoma_ai)
     ↓
SQL Generation (ryoma_ai)
     ↓
Safety Validation (ryoma_ai)
     ↓
Query Execution (ryoma_data)
     ↓
Result Processing (ryoma_ai)
     ↓
User Response
```

### Enhanced Profiling Flow
```
Database
     ↓
[ryoma_data] Statistical Profiling
     ├─ Row counts
     ├─ NULL percentages
     ├─ Distinct ratios
     ├─ Top-k values
     └─ Basic semantic types
     ↓
[ryoma_ai] LLM Enhancement
     ├─ Natural language descriptions
     ├─ Business purpose analysis
     ├─ SQL generation hints
     └─ Join candidate scoring
     ↓
Enhanced Metadata
```

## Extension Points

### Adding New Datasources

1. Use the unified `DataSource` class:
```python
from ryoma_data import DataSource

# New database automatically supported through Ibis
datasource = DataSource(
    "clickhouse",
    host="localhost",
    port=9000
)
```

2. Register in factory if needed:
```python
from ryoma_data.factory import DataSourceFactory

datasource = DataSourceFactory.create(
    "new_backend",
    **connection_params
)
```

### Adding New AI Features

Create new modules in `ryoma_ai` that use the `DataSource` interface:

```python
from ryoma_data import DataSource

class MyAIFeature:
    def __init__(self, datasource: DataSource, model):
        self.datasource = datasource
        self.model = model

    def analyze(self):
        catalog = self.datasource.get_catalog()
        # Use LLM to analyze catalog
        pass
```

## Performance Considerations

### Lazy Loading
- Datasources lazy-load database drivers
- Only import what you need

### Caching
- LLM responses cached by default
- Statistical profiles can be cached
- Catalog information can be cached

### Batch Processing
- Batch profiling modes supported
- Parallel processing for large databases
- Configurable worker pools

## Security

### SQL Safety (AI Layer)
- Query validation before execution
- Configurable safety rules
- Result size limits

### Connection Security (Data Layer)
- Secure credential handling
- Connection pooling
- Timeout enforcement

## Related Documentation

- **[Store Architecture](store-architecture.md)** - Storage and state management
- **[Enhanced SQL Agent](enhanced-sql-agent.md)** - AI agent architecture
- **[Database Profiling](database-profiling.md)** - Profiling system details

## References

- **Paper**: "Automatic Metadata Extraction for Text-to-SQL"
- **Paper**: "ReFoRCE: A Text-to-SQL Agent with Self-Refinement"
- **LangChain**: Agent framework
- **Ibis**: Database abstraction layer

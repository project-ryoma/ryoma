# Store Architecture

Ryoma AI uses a unified store architecture that separates concerns while ensuring data consistency across all components.

## 🏗️ Three-Store Architecture

### Overview

Ryoma implements a three-tier storage system:

```mermaid
graph TD
    CLI[CLI Application] --> MS[Metadata Store]
    CLI --> VS[Vector Store] 
    CLI --> DS[Data Sources]
    
    MS --> AM[Agent Manager]
    VS --> AM
    DS --> AM
    
    AM --> SA[SQL Agent]
    AM --> PA[Python Agent]
    AM --> DA[Data Analysis Agent]
    AM --> CA[Chat Agent]
    
    SA --> CS[Catalog Store]
    PA --> CS
    DA --> CS
    CA --> CS
    
    CS --> MS
    CS --> VS
```

### 1. Metadata Store
**Purpose**: Stores structured metadata, configuration, and agent state

**Types**:
- `memory` - In-memory store (default, no persistence)
- `postgres` - PostgreSQL-based store with persistence
- `redis` - Redis-based store for distributed deployments

**What it stores**:
- Agent configurations and state
- Data source registrations
- Catalog metadata and indexes
- Session information

### 2. Vector Store  
**Purpose**: Handles semantic search and embeddings for catalog optimization

**Types**:
- `chroma` - File-based vector database (recommended for development)
- `faiss` - In-memory vector store for fast prototyping
- `qdrant` - Production vector database
- `pgvector` - PostgreSQL with vector extension

**What it stores**:
- Table and column embeddings for semantic search
- Indexed catalog elements for fast retrieval
- Query history embeddings for context

### 3. Data Sources
**Purpose**: Connects to actual databases and data sources

**Types**:
- `postgres` - PostgreSQL databases
- `mysql` - MySQL databases  
- `sqlite` - SQLite databases
- `snowflake` - Snowflake data warehouse
- `bigquery` - Google BigQuery
- `duckdb` - DuckDB analytics database

## 🔄 Store Unification

### The Problem
Previously, each component created independent store instances, leading to:
- Data duplication across stores
- Inconsistent state between agents
- Circular dependencies between modules
- Performance degradation

### The Solution
The unified architecture ensures:
- **Single source of truth**: All components share the same store instances
- **CLI coordination**: CLI creates and distributes stores to all managers
- **No duplication**: Agents receive stores from CLI, never create their own
- **Consistency**: All agents see the same data and state

### Implementation Pattern

```python
# CLI creates unified stores
class RyomaAI:
    def __init__(self):
        # Create unified stores from configuration
        self.meta_store = StoreFactory.create_store(**meta_config.to_factory_params())
        self.vector_store = create_vector_store(config=vector_config, embedding_function=embedding)
        
        # Pass unified stores to all managers
        self.agent_manager = AgentManager(...)
        self.command_handler = CommandHandler(
            meta_store=self.meta_store,
            vector_store=self.vector_store
        )

# Agents receive stores from CLI
class BaseAgent:
    def __init__(self, store=None, vector_store=None, **kwargs):
        if store is None:
            raise ValueError("store parameter is required - agents must receive stores from CLI")
        self.store = store
        self.vector_store = vector_store
```

## ⚙️ Configuration Structure

### New Configuration Format

The configuration is now split into three distinct sections:

```json
{
  "model": "gpt-4o",
  "mode": "enhanced",
  "embedding_model": "text-embedding-ada-002",
  
  "meta_store": {
    "type": "memory",
    "connection_string": null,
    "options": {}
  },
  
  "vector_store": {
    "type": "chroma", 
    "collection_name": "ryoma_vectors",
    "dimension": 768,
    "distance_metric": "cosine",
    "extra_configs": {
      "persist_directory": "./data/vectors"
    }
  },
  
  "datasources": [
    {
      "name": "default",
      "type": "postgres", 
      "host": "localhost",
      "port": 5432,
      "database": "mydb",
      "user": "postgres",
      "password": "password"
    }
  ]
}
```

### Configuration Examples

#### Development Setup
```json
{
  "meta_store": {"type": "memory"},
  "vector_store": {"type": "chroma"},
  "datasources": [{"type": "sqlite", "database": ":memory:"}]
}
```

#### Production Setup
```json
{
  "meta_store": {
    "type": "postgres",
    "connection_string": "postgresql://user:pass@prod-db:5432/metadata"
  },
  "vector_store": {
    "type": "qdrant",
    "extra_configs": {
      "url": "http://qdrant-server:6333",
      "api_key": "your-api-key"
    }
  },
  "datasources": [
    {
      "name": "warehouse",
      "type": "snowflake",
      "account": "your-account", 
      "warehouse": "COMPUTE_WH"
    }
  ]
}
```

## 🔧 Store Factory Pattern

### Metadata Store Factory
```python
from ryoma_ai.store.store_factory import StoreFactory

# Create store from configuration
store = StoreFactory.create_store(
    store_type="postgres",
    connection_string="postgresql://localhost:5432/metadata",
    options={}
)
```

### Supported Store Types

| Type | Description | Use Case |
|------|-------------|----------|
| `memory` | In-memory storage | Development, testing |
| `postgres` | PostgreSQL storage | Production, persistence |
| `redis` | Redis storage | Distributed, caching |

## 📊 Catalog Store Integration

### Unified Catalog Indexing

The catalog store now uses the unified architecture:

```python
# CatalogStore requires unified stores
catalog_store = CatalogStore(
    metadata_store=unified_meta_store,  # From CLI
    vector_store=unified_vector_store   # From CLI  
)

# Indexing uses UnifiedCatalogIndexService
indexer = UnifiedCatalogIndexService(
    metadata_store=unified_meta_store,
    vector_store=unified_vector_store
)
```

### Search Optimization

Catalog search is now optimized using indexed metadata:

```python
# Fast semantic search without loading full catalog
relevant_catalog = catalog_store.search_relevant_catalog(
    query="customer information",
    top_k=10,
    min_score=0.3
)

# Get table suggestions
suggestions = catalog_store.get_table_suggestions(
    query="sales data",
    max_tables=5
)
```

## 🛡️ Error Prevention

### Store Validation

The architecture prevents common errors:

```python
# Agents MUST receive stores from CLI
class BaseAgent:
    def __init__(self, store=None, **kwargs):
        if store is None:
            raise ValueError("store parameter is required - agents must receive stores from CLI to ensure unified storage")
```

### Circular Import Resolution

Moved exception classes to break circular dependencies:
- `CatalogIndexError` moved from `ryoma_ai.store.exceptions` to `ryoma_ai.catalog.exceptions`
- Clean separation between catalog and store modules

## 🔄 Migration Guide

### From Legacy Configuration

**Old format:**
```json
{
  "database": {
    "type": "postgres",
    "connection_string": "postgresql://..."
  },
  "default_datasource": {...},
  "additional_datasources": [...]
}
```

**New format:**
```json
{
  "meta_store": {"type": "memory"},
  "vector_store": {"type": "chroma"}, 
  "datasources": [{...}]
}
```

### Agent Initialization Updates

**Old way:**
```python
agent = SqlAgent("gpt-4", mode="enhanced")
agent.add_datasource(datasource)
```

**New way (CLI managed):**
```python
# CLI handles all initialization
ryoma-ai> show me the data
# Agents are created automatically with unified stores
```

**New way (Programmatic):**
```python
# Must provide unified stores
agent = SqlAgent(
    model="gpt-4",
    mode="enhanced",
    datasource=datasource,
    store=unified_meta_store,      # Required
    vector_store=unified_vector_store  # Optional but recommended
)
```

## 🏎️ Performance Benefits

### Before Unification
- Multiple store instances per agent
- Duplicate data storage
- Inconsistent state
- Higher memory usage

### After Unification  
- Single store instance shared by all agents
- Centralized data management
- Consistent state across system
- Optimized memory usage
- Faster catalog operations through indexing

## 🔍 Debugging Store Issues

### Check Store Status
```bash
ryoma-ai> /config
# Shows all store configurations

ryoma-ai> /agents  
# Shows which agents are using stores
```

### Common Issues

**"Store parameter is required" Error:**
- Agents must receive stores from CLI
- Never create agents directly in production
- Use CLI or pass unified stores explicitly

**Vector search fails:**
- Run `/index-catalog` first
- Ensure vector store is configured
- Check embedding model configuration

**Circular import errors:**
- Import from correct exception modules
- Use lazy imports if needed
- Check module dependency order
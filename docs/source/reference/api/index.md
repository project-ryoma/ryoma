# 🔧 API Reference

Complete API documentation for Ryoma's core components and interfaces.

## 🎯 Core APIs

| 🧩 Component | 📝 Description | 🔗 Link |
|--------------|----------------|---------|
| **Core API** | Base agents, stores, and configuration | [Core API →](core.md) |

## 🏗️ Architecture APIs

The API reference covers Ryoma's unified three-tier architecture:

### 1. **Agent Layer**
- Base agent functionality and common interfaces
- Agent factory and creation patterns
- Multi-agent routing and coordination

### 2. **Store Layer** 
- Metadata store management
- Vector store operations
- Unified store coordination

### 3. **Data Layer**
- Data source connections and management
- Catalog indexing and search
- Query execution and validation

## 🚀 Quick Examples

### Agent Creation
```python
from ryoma_ai.agent.factory import AgentFactory

# Create any agent type
agent = AgentFactory.create_agent(
    agent_type="sql",
    model="gpt-4o",
    datasource=datasource,
    store=meta_store,
    vector_store=vector_store
)
```

### Store Management
```python
from ryoma_ai.store.store_factory import StoreFactory

# Create unified stores
meta_store = StoreFactory.create_store(
    store_type="postgres",
    connection_string="postgresql://localhost:5432/metadata"
)
```

### Catalog Operations
```python
# Search and index operations
agent.index_datasource(datasource, level="table")
catalog = agent.search_catalogs("customer data", top_k=10)
```

```{toctree}
:maxdepth: 2

core
```
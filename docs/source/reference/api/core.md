# 🔧 Core API Reference

Complete reference for Ryoma's core APIs, including agent creation, store management, and configuration.

## 🏗️ Base Agent API

### Class: `BaseAgent`

Foundation class for all Ryoma agents providing unified store management and common functionality.

```python
from ryoma_ai.agent.base import BaseAgent

class BaseAgent:
    def __init__(
        self,
        datasource: Optional[DataSource] = None,
        embedding: Optional[Union[dict, Embeddings]] = None,
        vector_store: Optional[Union[dict, VectorStore]] = None,
        store = None,
        **kwargs
    )
```

#### Parameters
- **`datasource`** *(Optional[DataSource])*: Primary data source for the agent
- **`embedding`** *(Optional[Union[dict, Embeddings]])*: Embedding configuration or instance
- **`vector_store`** *(Optional[Union[dict, VectorStore]])*: Vector store configuration or instance  
- **`store`** *(Optional[Store])*: Unified metadata store (uses InMemoryStore as default)

#### Methods

##### `add_datasource(datasource: DataSource) -> BaseAgent`
Register a data source with the agent.

```python
from ryoma_ai.datasource.postgres import PostgresDataSource

datasource = PostgresDataSource("postgresql://localhost:5432/db")
agent.add_datasource(datasource)
```

##### `get_datasource() -> DataSource`
Retrieve the registered data source.

```python
datasource = agent.get_datasource()
print(f"Connected to: {datasource.type}")
```

##### `index_datasource(datasource, level="catalog", data_source_id=None)`
Index data source for optimized search.

```python
# Index at table level (recommended)
catalog_id = agent.index_datasource(datasource, level="table")

# Index with custom ID
agent.index_datasource(datasource, level="column", data_source_id="prod_db")
```

##### `search_catalogs(query: str, top_k: int = 5, **kwargs) -> Catalog`
Search indexed catalog metadata.

```python
# Search for relevant tables/columns
catalog = agent.search_catalogs(
    query="customer information",
    top_k=10,
    min_score=0.3,
    element_types=["table", "column"]
)
```

##### `get_table_suggestions(query: str, max_tables: int = 5, min_score: float = 0.4)`
Get table suggestions based on query.

```python
suggestions = agent.get_table_suggestions(
    query="sales revenue data",
    max_tables=5,
    min_score=0.4
)

for suggestion in suggestions:
    print(f"Table: {suggestion['table_name']}")
    print(f"Description: {suggestion['description']}")
    print(f"Score: {suggestion['score']:.2f}")
```

##### `validate_catalog_indexing() -> Dict[str, Any]`
Check catalog indexing status and recommendations.

```python
status = agent.validate_catalog_indexing()
print(f"Status: {status['status']}")
print(f"Recommendation: {status['recommendation']}")
```

## 🏭 Agent Factory API

### Class: `AgentFactory`

Factory for creating agents with consistent configuration.

```python
from ryoma_ai.agent.factory import AgentFactory

class AgentFactory:
    @staticmethod
    def create_agent(agent_type: str, *args, **kwargs) -> Union[BaseAgent, ...]
```

#### Supported Agent Types
```python
from ryoma_ai.agent.factory import get_builtin_agents

# Get all built-in agent types
agents = get_builtin_agents()
# Returns: [base, sql, pandas, pyarrow, pyspark, python, embedding]
```

#### Usage Examples
```python
# SQL Agent
sql_agent = AgentFactory.create_agent(
    agent_type="sql",
    model="gpt-4o",
    mode="enhanced",
    datasource=datasource,
    store=meta_store
)

# Python Agent  
python_agent = AgentFactory.create_agent(
    agent_type="python",
    model="gpt-4o",
    store=meta_store
)

# Data Analysis Agent
data_agent = AgentFactory.create_agent(
    agent_type="pandas", 
    model="gpt-4o",
    datasource=datasource,
    store=meta_store,
    vector_store=vector_store
)
```

## 🧠 Multi-Agent Router API

### Class: `MultiAgentRouter`

Intelligent routing system for automatic agent selection.

```python
from ryoma_ai.agent.multi_agent_router import MultiAgentRouter

class MultiAgentRouter:
    def __init__(
        self,
        model: str,
        datasource = None,
        meta_store = None, 
        vector_store = None,
        **kwargs
    )
```

#### Methods

##### `route_and_execute(user_input: str, **config_overrides) -> tuple`
Route question to appropriate agent and return results.

```python
agent, classification, context = router.route_and_execute(
    "Show me customer revenue trends",
    sql_mode="enhanced"  # Override configuration
)

print(f"Routed to: {classification.suggested_agent}")
print(f"Confidence: {classification.confidence:.2f}")
```

##### `get_agent(agent_type: str, **config_overrides) -> Any`
Get or create specific agent instance.

```python
# Get cached agent instance
sql_agent = router.get_agent("sql")

# Get agent with custom config
enhanced_agent = router.get_agent("sql", mode="reforce")
```

##### `get_capabilities() -> Dict[str, Dict[str, List[str]]]`
Get capabilities for all agent types.

```python
capabilities = router.get_capabilities()

for agent_name, info in capabilities.items():
    print(f"{agent_name}: {info['capabilities']}")
```

##### `get_current_stats() -> Dict[str, Any]`
Get router usage statistics.

```python
stats = router.get_current_stats()
print(f"Total queries: {stats['total_queries']}")
print(f"Most used agent: {max(stats['agent_usage'], key=stats['agent_usage'].get)}")
```

## 🗄️ Store Management API

### Store Factory
```python
from ryoma_ai.store.store_factory import StoreFactory

# Create metadata store
meta_store = StoreFactory.create_store(
    store_type="postgres",
    connection_string="postgresql://localhost:5432/metadata",
    options={"pool_size": 10}
)

# Supported store types: memory, postgres, redis
```

### Vector Store Factory
```python
from ryoma_ai.vector_store.factory import create_vector_store
from ryoma_ai.vector_store.config import VectorStoreConfig

config = VectorStoreConfig(
    type="chroma",
    collection_name="my_vectors",
    dimension=1536,
    extra_configs={"persist_directory": "./vectors"}
)

vector_store = create_vector_store(
    config=config,
    embedding_function=embedding
)
```

## 📊 Catalog Store API

### Class: `CatalogStore`

Manages catalog metadata with semantic search capabilities.

```python
from ryoma_ai.store.catalog_store import CatalogStore

store = CatalogStore(
    metadata_store=meta_store,
    vector_store=vector_store
)
```

#### Methods

##### `search_relevant_catalog(query, top_k=5, min_score=0.3, element_types=None)`
Search for relevant catalog elements.

```python
catalog = store.search_relevant_catalog(
    query="customer data",
    top_k=10,
    min_score=0.4,
    element_types=["table", "column"]
)

print(f"Found {len(catalog.tables)} relevant tables")
```

##### `get_table_suggestions(query, max_tables=5, min_score=0.4)`
Get table suggestions based on semantic similarity.

```python
suggestions = store.get_table_suggestions(
    query="sales and revenue analysis",
    max_tables=5,
    min_score=0.4
)

for suggestion in suggestions:
    print(f"{suggestion['table_name']}: {suggestion['score']:.2f}")
```

##### `get_column_suggestions(query, table_context=None, max_columns=10, min_score=0.3)`
Get column suggestions with optional table context.

```python
columns = store.get_column_suggestions(
    query="customer identifier",
    table_context="customers",
    max_columns=10,
    min_score=0.3
)
```

## 🎯 Configuration API

### Class: `ConfigManager`

Handles configuration loading and validation.

```python
from ryoma_ai.config.manager import ConfigManager

manager = ConfigManager()

# Load configuration
config = manager.load_config("/path/to/config.json")

# Validate configuration  
validation = manager.validate_config(config)
if not validation['valid']:
    print(f"Config errors: {validation['errors']}")

# Apply environment variables
config = manager.apply_env_vars(config)
```

### Environment Configuration
```python
# Get environment-specific config
env_config = manager.get_environment_config("production")

# Merge configurations
final_config = manager.merge_configs(base_config, env_config)
```

## 🔍 Data Source API

### Base DataSource Interface
```python
from ryoma_ai.datasource.base import DataSource

class DataSource:
    def get_catalog(self) -> Catalog
    def execute_query(self, query: str) -> Any
    def get_table_names(self) -> List[str]
    def get_table_info(self, table_name: str) -> Dict
    def test_connection(self) -> bool
```

### Database-Specific APIs
```python
from ryoma_ai.datasource.postgres import PostgresDataSource

# PostgreSQL-specific features
postgres_ds = PostgresDataSource("postgresql://localhost:5432/db")
postgres_ds.enable_explain_analyze()  # Query performance analysis
postgres_ds.set_search_path(["public", "analytics"])  # Schema search path
```

## 🎨 Embedding API

### Embedding Client Factory
```python
from ryoma_ai.embedding.client import get_embedding_client

# OpenAI embeddings
embedding = get_embedding_client(
    "text-embedding-ada-002",
    model_parameters={"batch_size": 100}
)

# Local embeddings
local_embedding = get_embedding_client(
    "sentence-transformers/all-MiniLM-L6-v2",
    model_parameters={"device": "cuda"}
)
```

## 🔐 Security API

### Query Validation
```python
from ryoma_ai.agent.validator import QueryValidator

validator = QueryValidator(
    allowed_operations=["SELECT", "WITH"],
    blocked_operations=["DROP", "DELETE"],
    max_rows=50000
)

# Validate query
result = validator.validate_query("SELECT * FROM customers")
if not result['is_valid']:
    print(f"Validation failed: {result['issues']}")
```

### Safety Configuration
```python
from ryoma_ai.config.safety import SafetyConfig

safety = SafetyConfig(
    enable_validation=True,
    allowed_operations=["SELECT", "WITH", "CTE"],
    max_rows=100000,
    max_execution_time=300,
    require_where_clause=False
)

agent = SqlAgent(
    model="gpt-4o",
    mode="enhanced",
    safety_config=safety
)
```

## 📈 Monitoring API

### Performance Monitoring
```python
from ryoma_ai.monitoring import PerformanceMonitor

monitor = PerformanceMonitor(
    track_query_time=True,
    track_model_calls=True,
    export_metrics=True
)

# Get metrics
metrics = monitor.get_metrics()
print(f"Average query time: {metrics['avg_query_time']:.2f}s")
print(f"Total model calls: {metrics['total_model_calls']}")
```

### Health Monitoring
```python
from ryoma_ai.monitoring import HealthMonitor

health = HealthMonitor()

# Check component health
status = health.check_all_components()
for component, health_info in status.items():
    print(f"{component}: {health_info['status']}")
```

## 🔗 Related Documentation

- **[Agent Reference](../agent/index.md)** - Specific agent APIs
- **[Data Sources](../data-sources/index.md)** - Database connectors
- **[Models](../models/index.md)** - Model configuration
- **[Store Architecture](../../architecture/store-architecture.md)** - Storage system
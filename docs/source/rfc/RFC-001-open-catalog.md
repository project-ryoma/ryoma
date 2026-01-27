# RFC-001: Open Catalog - Database-Agnostic Metadata Search

**Status:** Draft
**Authors:** Ryoma AI Team
**Created:** 2026-01-27
**Updated:** 2026-01-27

## Abstract

This RFC proposes **Open Catalog**, a database-agnostic, deterministic metadata search framework for Ryoma AI. Unlike embedding-based retrieval systems, Open Catalog treats metadata like source code—searchable, inspectable, and verifiable—enabling LLM agents to explore data systems systematically without vector indexing.

## Problem Statement

### Current Challenges

Ryoma AI currently relies on vector-based catalog indexing for metadata search:

1. **Fragmentation**: Metadata is scattered across different systems (RDBMS, data warehouses, lakehouses, streaming platforms)
2. **Opacity**: Vector embeddings are black boxes—hard to debug when retrieval fails
3. **Indexing Overhead**: Requires pre-indexing, vector stores, and embedding generation
4. **Hallucination Risk**: LLMs reason over incomplete or stale indexed metadata
5. **System-Specific Logic**: Each connector requires custom indexing code

### Example Scenario

```
User: "Show me customer revenue by region for Q4 2025"

Current Flow (Vector-Based):
1. Generate embedding for "customer revenue region Q4"
2. Search vector store for similar tables
3. Retrieve top-k results (may miss relevant tables)
4. LLM generates SQL from incomplete context
5. Query fails or returns wrong results

Problems:
- What if "revenue" table wasn't indexed?
- What if embedding doesn't capture "Q4" temporal semantics?
- How do we debug why "regional_sales" wasn't retrieved?
```

## Goals

### Primary Goals

1. **Zero-Indexing Search**: Enable metadata search without pre-indexing or vector stores
2. **Deterministic Discovery**: Search results should be reproducible and debuggable
3. **System-Agnostic**: Work uniformly across SQL, NoSQL, data warehouses, and streaming systems
4. **LLM-Native**: Designed for agent-driven exploration (Claude Code style)
5. **Incremental Refinement**: Support iterative narrowing from broad to specific metadata

### Non-Goals

1. **Replace All Vector Search**: Vector search remains valid for some use cases (e.g., semantic table matching)
2. **Optimize for Scale**: Initial focus is correctness, not sub-second search on million-table catalogs
3. **Full-Text Search Engine**: Not building a general-purpose search engine
4. **Schema Change Detection**: Out of scope (for now)

## Design Overview

### Core Principle

> **Treat metadata like source code.**
> Use structured search (glob, grep, filters) + LLM reasoning instead of embeddings.

### High-Level Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    LLM Agent (Claude)                         │
│  "Show me customer tables with email columns"                │
└────────────────┬─────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────┐
│               Open Catalog API (Unified)                      │
│  - search_tables(pattern, filters)                           │
│  - search_columns(pattern, table, type)                      │
│  - inspect_table(name)                                       │
│  - get_relationships(table)                                  │
└────────────────┬─────────────────────────────────────────────┘
                 │
        ┌────────┴────────┬──────────────┬──────────────┐
        ▼                 ▼              ▼              ▼
┌──────────────┐  ┌──────────────┐  ┌──────────┐  ┌──────────┐
│ PostgreSQL   │  │  Snowflake   │  │  Delta   │  │  Kafka   │
│  Adapter     │  │   Adapter    │  │  Adapter │  │  Adapter │
└──────────────┘  └──────────────┘  └──────────┘  └──────────┘
```

### Workflow Comparison

| Step | Vector-Based (Current) | Open Catalog (Proposed) |
|------|------------------------|-------------------------|
| **1. Discovery** | Embed query → Search vectors | Pattern-based search (e.g., `*customer*`) |
| **2. Narrowing** | Re-embed, re-search | Filter results (e.g., `has_column:email`) |
| **3. Inspection** | Retrieve pre-indexed metadata | Fetch fresh schema on-demand |
| **4. Verification** | Hope embedding captured it | Explicit column/type checks |
| **5. Query Generation** | LLM + stale metadata | LLM + fresh metadata |

## Core Abstractions

### 1. Metadata Elements

All data systems expose these primitives:

```python
@dataclass
class MetadataElement:
    """Base class for all metadata entities."""
    name: str
    type: ElementType  # TABLE, COLUMN, SCHEMA, etc.
    qualified_name: str  # Fully qualified identifier
    properties: Dict[str, Any]  # System-specific attributes

@dataclass
class TableMetadata(MetadataElement):
    schema_name: Optional[str]
    columns: List[ColumnMetadata]
    row_count: Optional[int]
    size_bytes: Optional[int]
    properties: Dict[str, Any]  # System-specific (partitions, clustering, etc.)

@dataclass
class ColumnMetadata(MetadataElement):
    table_name: str
    data_type: str
    nullable: bool
    primary_key: bool
    foreign_keys: List[ForeignKeyRef]
    properties: Dict[str, Any]  # System-specific (collation, default, etc.)
```

### 2. Search Operations

Core search primitives that every adapter must implement:

```python
class OpenCatalogAdapter(Protocol):
    """Protocol for database-agnostic metadata access."""

    def search_tables(
        self,
        pattern: Optional[str] = None,  # Glob pattern: "*customer*", "dim_*"
        schema: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,  # has_column:email, row_count>1000
        limit: int = 100
    ) -> List[TableMetadata]:
        """Search tables by name pattern and filters."""
        ...

    def search_columns(
        self,
        pattern: Optional[str] = None,  # Glob pattern: "*email*", "created_*"
        table: Optional[str] = None,  # Limit to specific table
        data_type: Optional[str] = None,  # Filter by type
        limit: int = 100
    ) -> List[ColumnMetadata]:
        """Search columns across tables."""
        ...

    def inspect_table(self, qualified_name: str) -> TableMetadata:
        """Get complete metadata for a specific table."""
        ...

    def get_relationships(
        self,
        table: str,
        direction: Literal["incoming", "outgoing", "both"] = "both"
    ) -> List[RelationshipMetadata]:
        """Get foreign key relationships for a table."""
        ...

    def get_sample_data(
        self,
        table: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get sample rows from a table (for value inspection)."""
        ...
```

### 3. Search Filters

Declarative filters that translate to system-specific queries:

```python
class SearchFilter:
    """Declarative metadata filters."""

    # Column-based filters
    has_column: Optional[str]  # "email", "created_at"
    has_columns: Optional[List[str]]  # Multiple columns

    # Type-based filters
    column_type: Optional[str]  # "VARCHAR", "TIMESTAMP"
    has_primary_key: Optional[bool]
    has_foreign_keys: Optional[bool]

    # Size-based filters
    row_count_min: Optional[int]
    row_count_max: Optional[int]
    size_bytes_min: Optional[int]

    # Temporal filters
    modified_after: Optional[datetime]
    created_after: Optional[datetime]

    # System-specific filters (extensible)
    properties: Dict[str, Any]
```

## Agent Workflow

### Claude Code–Style Search Flow

The agent follows an iterative refinement process:

```
┌─────────────────────────────────────────────────────────────┐
│ User Question: "Show customer emails from last month"       │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 1: BROAD SEARCH                                         │
│ Agent: "Let me search for customer-related tables"          │
│ Action: search_tables(pattern="*customer*")                 │
│ Result: [customers, customer_orders, customer_feedback,     │
│          dim_customer, customer_segments] (23 tables)       │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 2: NARROW BY COLUMN                                     │
│ Agent: "Which tables have email columns?"                   │
│ Action: search_tables(pattern="*customer*",                 │
│                       filters={has_column: "email"})        │
│ Result: [customers, customer_feedback] (2 tables)           │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 3: INSPECT SCHEMA                                       │
│ Agent: "Let me check the customers table structure"         │
│ Action: inspect_table("customers")                          │
│ Result: {                                                    │
│   columns: [id, name, email, created_at, region],          │
│   row_count: 45000,                                         │
│   primary_key: [id]                                         │
│ }                                                            │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 4: CHECK RELATIONSHIPS                                  │
│ Agent: "Are there related tables?"                          │
│ Action: get_relationships("customers")                      │
│ Result: [                                                    │
│   {from: "orders", to: "customers", on: "customer_id"},   │
│   {from: "customer_segments", to: "customers", on: "id"}  │
│ ]                                                            │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 5: VERIFY TEMPORAL COLUMN                               │
│ Agent: "Does it have a date column for filtering?"          │
│ Action: inspect_table("customers").columns                  │
│ Result: created_at (TIMESTAMP)                              │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 6: GENERATE QUERY                                       │
│ Agent: "I have all the information I need"                  │
│ SQL: SELECT email FROM customers                            │
│      WHERE created_at >= DATE_TRUNC('month', NOW() - ...   │
└─────────────────────────────────────────────────────────────┘
```

### Key Characteristics

1. **Iterative**: Each step refines the search space
2. **Explicit**: Every action is traceable and debuggable
3. **Fresh**: Metadata is fetched on-demand, not from stale cache
4. **Verifiable**: Agent can check assumptions before generating SQL

## Implementation Strategy

### Phase 1: Core Abstractions (This PR)

**Goal**: Establish interfaces and documentation (no production code changes)

**Deliverables**:
- [ ] `OpenCatalogAdapter` protocol definition
- [ ] `MetadataElement` dataclass hierarchy
- [ ] `SearchFilter` specification
- [ ] RFC documentation
- [ ] Example/reference implementation (SQLite)

**Files**:
```
packages/ryoma_ai/ryoma_ai/catalog/
├── open_catalog/
│   ├── __init__.py
│   ├── protocol.py          # OpenCatalogAdapter protocol
│   ├── models.py            # MetadataElement dataclasses
│   ├── filters.py           # SearchFilter specification
│   └── exceptions.py        # OpenCatalog-specific errors
├── adapters/
│   ├── __init__.py
│   └── reference/
│       └── sqlite_adapter.py  # Reference implementation
└── tests/
    └── open_catalog/
        └── test_sqlite_adapter.py
```

### Phase 2: Adapter Implementations

**Goal**: Implement adapters for existing connectors

**Strategy**: **Ibis-Based Universal Adapter** (Recommended)

Since Ryoma already uses [Ibis](https://ibis-project.org/) for database connectivity, we can leverage Ibis's unified metadata interface to create **a single adapter that works across ALL databases**:

```python
from ryoma_ai.catalog.adapters import IbisOpenCatalogAdapter

# Works with ANY Ibis backend
datasource = DataSource("postgres", host="localhost", database="mydb")
adapter = IbisOpenCatalogAdapter(datasource)

# Same adapter works with Snowflake
datasource = DataSource("snowflake", account="myaccount", ...)
adapter = IbisOpenCatalogAdapter(datasource)

# And DuckDB, BigQuery, MySQL, SQLite, ClickHouse, etc.
```

**Benefits**:
- ✅ Single implementation for ALL databases
- ✅ Leverages existing Ibis integration in Ryoma
- ✅ Automatic support for new Ibis backends
- ✅ Consistent behavior across systems
- ✅ Reduced maintenance burden

**Ibis Metadata API Used**:
- `conn.list_tables()` - List available tables
- `conn.list_databases()` - List schemas/databases
- `conn.get_schema(table)` - Get table schema (columns, types)
- `table.count()` - Get row count
- `table.limit(n).execute()` - Get sample data

**Supported Databases** (via Ibis):
1. PostgreSQL
2. MySQL / MariaDB
3. Snowflake
4. BigQuery
5. DuckDB
6. SQLite
7. ClickHouse
8. Trino / Presto
9. Oracle
10. MSSQL
11. And more...

**Alternative: Backend-Specific Adapters**

For databases requiring specialized optimizations or features not available in Ibis:

```python
class PostgresOpenCatalogAdapter:
    """Optimized adapter for PostgreSQL-specific features."""

    def search_tables(self, pattern, schema, filters, limit):
        # Use PostgreSQL-specific optimizations
        query = """
            SELECT
                schemaname, tablename,
                pg_total_relation_size(schemaname||'.'||tablename) as size_bytes,
                n_live_tup as row_count
            FROM pg_tables
            JOIN pg_stat_user_tables ON ...
            WHERE tablename LIKE :pattern
        """
        ...
```

**Implementation Priority**:
1. **IbisOpenCatalogAdapter** (universal, immediate support for all DBs)
2. PostgreSQL-specific adapter (optimizations for pg_stat, pg_catalog)
3. Snowflake-specific adapter (metadata caching, information schema)
4. BigQuery-specific adapter (INFORMATION_SCHEMA optimizations)

### Phase 3: Agent Integration

**Goal**: Create Open Catalog–aware tools and agent modes

**New Tools**:
- `OpenCatalogSearchTool`: Replaces vector-based catalog search
- `InspectTableTool`: Deep-dive into specific table
- `RelationshipDiscoveryTool`: Explore table relationships

**Agent Mode**:
```python
SqlAgent(
    model="claude-sonnet-4",
    mode="open_catalog",  # New mode
    catalog_strategy="open_catalog"  # vs "vector" or "hybrid"
)
```

### Phase 4: Hybrid Strategy

**Goal**: Allow mixing Open Catalog + vector search

**Use Cases**:
- Use Open Catalog for exact matches, vector for semantic similarity
- Use vector search for initial candidate generation, Open Catalog for verification

```python
class HybridCatalogSearcher:
    def search(self, query: str, strategy: Literal["vector", "open", "hybrid"]):
        if strategy == "hybrid":
            # 1. Get semantic candidates from vector search
            candidates = self.vector_searcher.search(query, top_k=20)
            # 2. Verify and refine using Open Catalog
            verified = self.open_catalog.inspect_tables(candidates)
            return verified
        ...
```

## Technical Details

### Pattern Matching

Support glob-style patterns that translate to SQL `LIKE`:

```python
Pattern              SQL Translation
------------------------------------
"*customer*"      →  table_name LIKE '%customer%'
"dim_*"           →  table_name LIKE 'dim_%'
"fact_*_daily"    →  table_name LIKE 'fact_%_daily'
"[!_]*"           →  table_name NOT LIKE '\_%'  (no prefix underscore)
```

### Filter Translation

SearchFilter → SQL WHERE clauses:

```python
filters = SearchFilter(
    has_column="email",
    row_count_min=1000,
    modified_after=datetime(2025, 1, 1)
)

# Translates to (PostgreSQL example):
"""
WHERE EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE columns.table_name = tables.table_name
    AND columns.column_name = 'email'
)
AND (
    SELECT n_live_tup FROM pg_stat_user_tables
    WHERE relname = tables.table_name
) >= 1000
AND pg_stat_user_tables.last_autovacuum > '2025-01-01'
"""
```

### Performance Considerations

**Concern**: "Won't querying information_schema be slow?"

**Response**:
1. **Caching**: Adapters can cache results with TTL (e.g., 5 minutes)
2. **Lazy Loading**: Only fetch full schema when inspecting specific tables
3. **Parallel Queries**: Search operations can run concurrently
4. **Index Hints**: Use system catalog indexes (information_schema is usually indexed)
5. **Progressive Refinement**: Narrow search space quickly (1000 tables → 10 → 1)

**Benchmarks** (target):
- Search 10K tables: < 500ms
- Inspect single table: < 100ms
- Get relationships: < 200ms

## Debugging and Observability

### Agent Trace Example

```
[Open Catalog Trace] Query: "customer revenue by region"

Step 1: search_tables(pattern="*customer*")
  ├─ SQL: SELECT ... FROM information_schema.tables WHERE ...
  ├─ Duration: 45ms
  └─ Results: 23 tables

Step 2: search_tables(pattern="*customer*", filters={has_column:"revenue"})
  ├─ SQL: SELECT ... WHERE EXISTS (... column_name = 'revenue')
  ├─ Duration: 120ms
  └─ Results: 2 tables [customers_revenue, customer_metrics]

Step 3: inspect_table("customers_revenue")
  ├─ SQL: SELECT ... FROM information_schema.columns WHERE ...
  ├─ Duration: 35ms
  └─ Result: {columns: [customer_id, region, revenue_q4, ...], ...}

Step 4: get_relationships("customers_revenue")
  ├─ SQL: SELECT ... FROM information_schema.key_column_usage WHERE ...
  ├─ Duration: 40ms
  └─ Result: [FK to customers(id), FK to regions(code)]

Total: 240ms, 4 operations
```

### Error Handling

```python
class OpenCatalogError(Exception):
    """Base exception for Open Catalog operations."""
    pass

class TableNotFoundException(OpenCatalogError):
    """Raised when table doesn't exist."""
    table_name: str
    suggested_tables: List[str]  # Fuzzy matches

class ColumnNotFoundException(OpenCatalogError):
    """Raised when column doesn't exist in table."""
    table_name: str
    column_name: str
    available_columns: List[str]

class SearchTimeoutError(OpenCatalogError):
    """Raised when search exceeds timeout."""
    query: str
    timeout_ms: int
```

## Alternatives Considered

### Alternative 1: Improve Vector Search

**Idea**: Keep vector embeddings but make them more transparent

**Pros**:
- No architecture change
- Fast for large catalogs

**Cons**:
- Still requires indexing
- Still opaque (can't explain why table wasn't retrieved)
- Doesn't solve freshness problem

**Decision**: Rejected. Doesn't address core issues.

### Alternative 2: Full-Text Search (Elasticsearch/Solr)

**Idea**: Index metadata in Elasticsearch

**Pros**:
- Fast full-text search
- Rich query language

**Cons**:
- Another infrastructure dependency
- Still requires indexing
- Overkill for structured metadata

**Decision**: Rejected. Too heavyweight.

### Alternative 3: GraphQL-Style Metadata API

**Idea**: Expose metadata as a GraphQL schema

**Pros**:
- Flexible queries
- Industry-standard

**Cons**:
- GraphQL is for apps, not LLM agents
- Doesn't solve search problem
- Query language is overly complex

**Decision**: Rejected. Mismatch with agent workflow.

## Open Questions

1. **Caching Strategy**: How long should metadata be cached? System-specific?
2. **Permissions**: How do we handle column-level permissions in search?
3. **Cross-Database Search**: Should search span multiple databases simultaneously?
4. **Fuzzy Matching**: Should we support fuzzy table name matching (`"custmer" → "customer"`)?
5. **Sampling Strategy**: How many sample rows to fetch by default?
6. **Telemetry**: What metrics should we track for Open Catalog usage?

## Success Metrics

How we'll measure success:

1. **Correctness**: % of queries where correct tables are identified
2. **Debuggability**: % of failures that can be explained from trace logs
3. **Latency**: P95 search latency < 500ms for 10K tables
4. **Adoption**: % of users who enable `open_catalog` mode
5. **Agent Iterations**: Avg. number of search steps before SQL generation

**Target** (3 months post-launch):
- 95% correctness
- 100% debuggable failures
- <300ms P95 latency
- 20% adoption
- <5 search iterations per query

## Migration Path

### For Existing Users

**No Breaking Changes**:
- Vector-based catalog search remains default
- Open Catalog is opt-in via agent mode

**Gradual Migration**:
```python
# Phase 1: Hybrid (both available)
agent = SqlAgent(
    catalog_strategy="hybrid",
    fallback_to_vector=True
)

# Phase 2: Open Catalog default
agent = SqlAgent(
    catalog_strategy="open_catalog",
    fallback_to_vector=True  # Safety net
)

# Phase 3: Vector deprecated
agent = SqlAgent(
    catalog_strategy="open_catalog"
)
```

### Deprecation Timeline

- **v0.3.0**: Introduce Open Catalog (opt-in)
- **v0.4.0**: Make Open Catalog default, deprecate vector-only mode
- **v0.5.0**: Remove vector-based catalog search entirely

## References

### Inspiration

- **Claude Code Search**: Glob → Grep → Read workflow for code exploration
- **SQL INFORMATION_SCHEMA**: Standard metadata interface
- **Trino Metadata API**: System-agnostic metadata abstraction
- **DBT Catalog**: Declarative metadata management

### Related RFCs

- *To be created*: RFC-002: Metadata Caching Strategy
- *To be created*: RFC-003: Multi-Catalog Search Orchestration

### External Links

- [PostgreSQL INFORMATION_SCHEMA](https://www.postgresql.org/docs/current/information-schema.html)
- [Snowflake INFORMATION_SCHEMA](https://docs.snowflake.com/en/sql-reference/info-schema)
- [Trino Metadata Protocol](https://trino.io/docs/current/develop/spi-overview.html)
- [Claude Code Agent SDK](https://docs.anthropic.com/claude/docs/claude-agent)

---

## Appendix A: Reference Implementation

Minimal SQLite adapter demonstrating the protocol:

```python
from typing import List, Optional, Dict, Any
from ryoma_ai.catalog.open_catalog import (
    OpenCatalogAdapter,
    TableMetadata,
    ColumnMetadata,
    SearchFilter
)

class SQLiteOpenCatalogAdapter(OpenCatalogAdapter):
    """Reference implementation for SQLite."""

    def __init__(self, datasource):
        self.datasource = datasource

    def search_tables(
        self,
        pattern: Optional[str] = None,
        schema: Optional[str] = None,
        filters: Optional[SearchFilter] = None,
        limit: int = 100
    ) -> List[TableMetadata]:
        """Search tables in SQLite using sqlite_master."""
        query = "SELECT name, sql FROM sqlite_master WHERE type='table'"

        if pattern:
            # Convert glob to SQL LIKE
            like_pattern = pattern.replace("*", "%").replace("?", "_")
            query += f" AND name LIKE '{like_pattern}'"

        if filters and filters.has_column:
            # Check column existence
            query += f"""
                AND name IN (
                    SELECT name FROM pragma_table_info(name)
                    WHERE name = '{filters.has_column}'
                )
            """

        query += f" LIMIT {limit}"

        results = self.datasource.query(query)
        return [self._parse_table_metadata(row) for row in results]

    def inspect_table(self, table_name: str) -> TableMetadata:
        """Get full table metadata."""
        columns = self.datasource.query(
            f"PRAGMA table_info({table_name})"
        )

        return TableMetadata(
            name=table_name,
            qualified_name=table_name,
            columns=[
                ColumnMetadata(
                    name=col["name"],
                    data_type=col["type"],
                    nullable=not col["notnull"],
                    primary_key=bool(col["pk"]),
                    table_name=table_name
                )
                for col in columns
            ]
        )

    # ... other methods
```

## Appendix B: Agent Tool Examples

```python
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

class SearchTablesInput(BaseModel):
    pattern: Optional[str] = Field(None, description="Glob pattern for table names")
    has_column: Optional[str] = Field(None, description="Filter by column name")

class OpenCatalogSearchTool(BaseTool):
    """Tool for searching database tables without indexing."""

    name: str = "search_tables"
    description: str = """
    Search for database tables by name pattern and filters.
    Use glob patterns like '*customer*' or 'dim_*'.
    Can filter by column existence, size, etc.
    Returns list of matching tables with basic metadata.
    """
    args_schema: Type[BaseModel] = SearchTablesInput

    def _run(
        self,
        pattern: Optional[str] = None,
        has_column: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        adapter = get_open_catalog_adapter()
        filters = SearchFilter(has_column=has_column) if has_column else None
        results = adapter.search_tables(pattern=pattern, filters=filters)
        return [table.to_dict() for table in results]
```

---

## Appendix C: Canonical Metadata Schema

### Logical Metadata Tables

The Open Catalog defines standard metadata tables independent of backend systems:

#### Core Tables

1. **`catalogs`**: Top-level metadata namespaces
   ```sql
   catalog_id, catalog_name, catalog_type, connection_info, created_at
   ```

2. **`namespaces`**: Logical groupings (schemas, databases, topics)
   ```sql
   namespace_id, catalog_id, namespace_name, namespace_type, properties
   ```

3. **`assets`**: Tables, views, topics, indexes, models, etc.
   ```sql
   asset_id, namespace_id, asset_name, asset_type, qualified_name,
   size_bytes, row_count, last_updated_at, properties
   ```

4. **`fields`**: Columns, attributes, keys, or fields
   ```sql
   field_id, asset_id, field_name, data_type, nullable, primary_key,
   foreign_keys, field_order, properties
   ```

5. **`versions`**: Snapshots, revisions, commits, or timestamps
   ```sql
   version_id, asset_id, version_number, created_at, change_summary
   ```

6. **`properties`**: Extensible key-value metadata
   ```sql
   entity_id, entity_type, property_key, property_value, source_system
   ```

7. **`tags`**: Labels and classifications
   ```sql
   entity_id, entity_type, tag_name, tag_category, applied_at
   ```

8. **`lineage`** (optional): Data flow relationships
   ```sql
   from_asset_id, to_asset_id, lineage_type, confidence_score
   ```

### LLM-Friendly Views

#### `v_catalog_search` - Flattened Search Surface

Provides `ripgrep`-equivalent search across all metadata:

```sql
CREATE VIEW v_catalog_search AS
SELECT
    object_id,
    object_type,  -- 'asset', 'field', 'namespace'
    qualified_name,
    content,  -- Concatenated searchable text
    match_score
FROM (
    -- Asset names and descriptions
    SELECT
        asset_id as object_id,
        'asset' as object_type,
        qualified_name,
        concat_ws(' ',
            asset_name,
            description,
            tags,
            properties
        ) as content
    FROM assets

    UNION ALL

    -- Field names and metadata
    SELECT
        field_id as object_id,
        'field' as object_type,
        concat(asset_qualified_name, '.', field_name),
        concat_ws(' ',
            field_name,
            data_type,
            description,
            tags
        ) as content
    FROM fields
    JOIN assets ON fields.asset_id = assets.asset_id
) searchable_entities;
```

**Usage**:
```sql
-- Find all assets containing "customer" or "email"
SELECT qualified_name, object_type
FROM v_catalog_search
WHERE content ILIKE '%customer%'
   OR content ILIKE '%email%'
ORDER BY match_score DESC
LIMIT 20;
```

#### `v_asset_overview` - One Row Per Asset

Quick asset summary for browsing:

```sql
CREATE VIEW v_asset_overview AS
SELECT
    asset_id,
    qualified_name,
    asset_type,
    COUNT(fields.field_id) as field_count,
    size_bytes,
    row_count,
    last_updated_at,
    array_agg(tags.tag_name) as tags
FROM assets
LEFT JOIN fields ON assets.asset_id = fields.asset_id
LEFT JOIN tags ON assets.asset_id = tags.entity_id
GROUP BY asset_id;
```

#### `v_asset_health` - System Health Metrics

Optional view for freshness and quality signals:

```sql
CREATE VIEW v_asset_health AS
SELECT
    asset_id,
    qualified_name,
    freshness_score,  -- Days since last update
    size_trend,  -- Growing, stable, shrinking
    change_frequency,  -- Daily, weekly, monthly
    risk_flags  -- stale, empty, unused
FROM asset_health_metrics;
```

## Appendix D: Supported Question Classes

### 1. Discovery Questions

**Q**: "Which assets contain customer_id?"

**Agent Flow**:
```python
# Tool: search_catalog
results = search_catalog(query="customer_id", limit=20)

# Returns:
[
    {"qualified_name": "prod.users.customer_id", "type": "field"},
    {"qualified_name": "prod.orders.customer_id", "type": "field"},
    {"qualified_name": "analytics.dim_customers", "type": "asset"}
]
```

### 2. Schema Inspection

**Q**: "What fields does the orders table have?"

**Agent Flow**:
```python
# Tool: describe_asset
schema = describe_asset(asset="prod.orders")

# Returns:
{
    "fields": [
        {"name": "order_id", "type": "INTEGER", "pk": true},
        {"name": "customer_id", "type": "INTEGER", "fk": "users.id"},
        {"name": "order_date", "type": "TIMESTAMP"},
        {"name": "total_amount", "type": "DECIMAL"}
    ]
}
```

### 3. Freshness Questions

**Q**: "What hasn't changed in 14 days?"

**Agent Flow**:
```python
# Tool: query_catalog
stale_assets = query_catalog(sql="""
    SELECT qualified_name, last_updated_at
    FROM v_asset_overview
    WHERE last_updated_at < NOW() - INTERVAL '14 days'
    ORDER BY last_updated_at ASC
    LIMIT 20
""")
```

### 4. Cross-System Search

**Q**: "Where does email appear across all databases?"

**Agent Flow**:
```python
# Search across all catalogs
results = search_catalog(
    query="email",
    scope="all_catalogs"
)

# Returns results from Postgres, Snowflake, MySQL, etc.
```

### 5. Change & Versioning

**Q**: "What changed yesterday?"

**Agent Flow**:
```python
changes = query_catalog(sql="""
    SELECT qualified_name, change_summary
    FROM versions
    WHERE created_at >= NOW() - INTERVAL '1 day'
    ORDER BY created_at DESC
""")
```

### 6. Governance & Risk

**Q**: "Which assets contain PII?"

**Agent Flow**:
```python
pii_assets = query_catalog(sql="""
    SELECT DISTINCT a.qualified_name
    FROM assets a
    JOIN tags t ON a.asset_id = t.entity_id
    WHERE t.tag_name IN ('PII', 'sensitive', 'gdpr')
""")
```

## Appendix E: Agent Tool Specifications

### Required Tools

All Open Catalog agents must implement these tools:

#### 1. `search_catalog`

```python
def search_catalog(
    query: str,
    object_type: Optional[Literal["asset", "field", "namespace"]] = None,
    catalog: Optional[str] = None,
    limit: int = 20
) -> List[Dict[str, Any]]:
    """
    Lexical search across all metadata.

    Equivalent to: rg "pattern" across all catalogs

    Returns:
        List of matching objects with qualified names and types
    """
```

#### 2. `describe_asset`

```python
def describe_asset(
    asset: str,
    include_sample_data: bool = False
) -> Dict[str, Any]:
    """
    Get complete metadata for a specific asset.

    Returns:
        {
            "qualified_name": "prod.orders",
            "asset_type": "table",
            "fields": [...],
            "size_bytes": 1024000,
            "row_count": 50000,
            "last_updated": "2026-01-27T10:00:00Z",
            "sample_data": [...]  # If requested
        }
    """
```

#### 3. `query_catalog`

```python
def query_catalog(
    sql: str,
    timeout_seconds: int = 30
) -> List[Dict[str, Any]]:
    """
    Execute SQL query against Open Catalog metadata.

    Restrictions:
        - Read-only (SELECT only)
        - Metadata tables only (no production data)
        - Row limit enforced (max 1000 rows)
        - Timeout enforced

    Returns:
        Query results as list of dictionaries
    """
```

#### 4. `asset_health`

```python
def asset_health(
    asset: str
) -> Dict[str, Any]:
    """
    Get health metrics for an asset (optional, system-dependent).

    Returns:
        {
            "freshness_score": 0.95,
            "size_trend": "growing",
            "change_frequency": "daily",
            "risk_flags": []
        }
    """
```

### Tool Characteristics

All tools must be:
- **Read-only**: No mutations to metadata or data
- **Auditable**: All calls logged with user, timestamp, query
- **Backend-agnostic**: Work across all connector types
- **Timeout-enforced**: Fail fast on slow operations
- **Row-limited**: Prevent unbounded result sets

## Appendix F: Agent Execution Loop

### Standard Flow

```
┌───────────────────────────────────────────────────────────┐
│ User Question                                              │
│ "Which tables have customer email addresses?"             │
└──────────────────┬────────────────────────────────────────┘
                   │
                   ▼
┌───────────────────────────────────────────────────────────┐
│ Planner: Parse Intent                                      │
│ {                                                          │
│   "intent": "discovery",                                  │
│   "entities": {"field": "email", "domain": "customer"},  │
│   "scope": "all_catalogs",                                │
│   "output": "list"                                        │
│ }                                                          │
└──────────────────┬────────────────────────────────────────┘
                   │
                   ▼
┌───────────────────────────────────────────────────────────┐
│ Tool: search_catalog(query="customer email", limit=20)    │
│ Returns: 15 potential matches                             │
└──────────────────┬────────────────────────────────────────┘
                   │
                   ▼
┌───────────────────────────────────────────────────────────┐
│ Agent: Filter candidates                                   │
│ - "customers" table (has email column) ✓                  │
│ - "customer_feedback" table (has email column) ✓          │
│ - "email_campaigns" table (no customer context) ✗         │
└──────────────────┬────────────────────────────────────────┘
                   │
                   ▼
┌───────────────────────────────────────────────────────────┐
│ Tool: describe_asset("customers")                         │
│ Verify: email column exists, type is VARCHAR              │
└──────────────────┬────────────────────────────────────────┘
                   │
                   ▼
┌───────────────────────────────────────────────────────────┐
│ Agent: Formulate Response                                  │
│ "Found 2 tables with customer email addresses:            │
│  1. customers (50,000 rows)                               │
│  2. customer_feedback (12,000 rows)"                      │
└───────────────────────────────────────────────────────────┘
```

### Planning Phase Rules

**Planner Output Schema**:
```json
{
  "intent": "discovery" | "inspection" | "governance" | "freshness",
  "entities": {
    "field": str,
    "asset": str,
    "namespace": str,
    "tag": str
  },
  "scope": "single_catalog" | "all_catalogs" | "specific_catalog",
  "filters": {
    "asset_type": ["table", "view"],
    "last_updated_after": "2026-01-01"
  },
  "output": "list" | "detail" | "summary"
}
```

**Rules**:
- ❌ No SQL in planning phase
- ✅ Explicit entity extraction
- ✅ Structured, deterministic output
- ✅ Declare ambiguity explicitly

### Query Execution Rules

1. **Metadata-only**: Never query production data tables
2. **Dialect-aware**: Translate to system-specific SQL
3. **Row limits**: Enforce maximum 1000 rows per query
4. **Timeout enforcement**: Kill queries exceeding timeout
5. **Deterministic formatting**: Consistent output across systems

### Result Interpretation Guidelines

**Agent must**:
- ✅ Reference concrete returned rows
- ✅ Explain reasoning ("Found this because...")
- ✅ Suggest next steps if incomplete
- ✅ Admit when information is missing

**Agent must not**:
- ❌ Speculate about data that wasn't returned
- ❌ Make assumptions about missing metadata
- ❌ Fabricate table or column names
- ❌ Silently ignore ambiguity

## Appendix G: Guardrails & Safety

### Strict Rules

1. **No Guessing Asset Names**
   ```
   ❌ Bad: "The revenue table probably exists..."
   ✅ Good: "I searched for 'revenue' and found these tables: ..."
   ```

2. **No Production Data Access**
   ```
   ❌ Bad: SELECT * FROM prod.users LIMIT 10
   ✅ Good: SELECT * FROM v_asset_overview WHERE qualified_name LIKE '%users%'
   ```

3. **No Silent Assumptions**
   ```
   ❌ Bad: Assuming "id" is primary key
   ✅ Good: Checking field metadata confirms "id" is primary key
   ```

4. **Explicit Disambiguation**
   ```
   User: "Show me the customer table"

   ❌ Bad: Picks "customers" arbitrarily
   ✅ Good: "Found 3 tables: customers, customer_history, dim_customers. Which one?"
   ```

5. **Reproducible Runs**
   ```
   Every search must be traceable:
   [search_catalog] query="customer email" → 15 results
   [describe_asset] asset="customers" → {...}
   ```

### Audit Logging

All tool invocations must be logged:

```json
{
  "timestamp": "2026-01-27T10:30:00Z",
  "user_id": "user_123",
  "session_id": "session_456",
  "tool": "search_catalog",
  "parameters": {
    "query": "customer email",
    "limit": 20
  },
  "results_count": 15,
  "execution_time_ms": 120
}
```

## Appendix H: Alternatives Considered

### Alternative 1: Vector Search / Embeddings

**Rejected because**:
- Poor explainability: "Why wasn't table X retrieved?"
- Operational cost: Requires embedding generation infrastructure
- Cross-system inconsistency: Different embedding models per connector
- Stale results: Embeddings lag behind schema changes

**When it's still useful**:
- Semantic similarity for ambiguous queries
- Fuzzy matching when exact patterns fail
- Hybrid strategy: vector candidates + Open Catalog verification

### Alternative 2: System-Specific Catalogs

**Rejected because**:
- Fragmentation: Each system has different catalog structure
- Vendor lock-in: Custom code per database
- No cross-system search: Can't find "email" across Postgres + Snowflake

### Alternative 3: Full-Text Search Engine (Elasticsearch)

**Rejected because**:
- Heavyweight infrastructure: Another service to deploy and maintain
- Still requires indexing: Doesn't solve freshness problem
- Overkill: Structured metadata doesn't need full-text ranking

### Alternative 4: GraphQL-Style Metadata API

**Rejected because**:
- Complexity mismatch: GraphQL is for apps, not agents
- Query language overhead: LLMs can already write SQL
- No search primitives: Still need to build search on top

## Appendix I: Future Work

### Phase 1: Core (This RFC)
- ✅ Define protocol and abstractions
- ✅ Reference implementation (SQLite)
- ✅ Documentation and RFC

### Phase 2: Connector Implementations
- PostgreSQL, MySQL adapters
- Snowflake, BigQuery adapters
- DuckDB, SQLite adapters

### Phase 3: Advanced Features
- Lineage graph traversal
- Cost and usage signals integration
- Policy enforcement hooks
- Multi-catalog federated search

### Phase 4: Enhanced Capabilities
- Optional semantic reranking (hybrid with vectors)
- UI/CLI catalog explorer
- Catalog diff and change detection
- Automated data profiling integration

### Phase 5: Governance & Observability
- Column-level access control integration
- Metadata quality scoring
- Usage analytics and recommendations
- Automated tagging and classification

## Appendix J: Open Questions

### For Community Discussion

1. **Normalization Strictness**
   - How strictly should we normalize metadata across systems?
   - Should we preserve system-specific properties or map to common schema?

2. **Non-Tabular Assets**
   - How to represent Kafka topics, S3 files, ML models?
   - Should we create subclasses or use extensible properties?

3. **Cross-Catalog Identity**
   - How to link same entity across systems (e.g., replicated tables)?
   - Should we support explicit cross-catalog references?

4. **Caching Strategy**
   - What's the right TTL for metadata cache (5min? 1hour?)?
   - Should it be system-specific (fast for Postgres, longer for Snowflake)?

5. **Versioning Granularity**
   - Should we track every schema change or only major versions?
   - What's the storage overhead vs. utility tradeoff?

6. **Performance Benchmarks**
   - What's acceptable P95 latency for 10K, 100K, 1M tables?
   - When should we recommend indexing/caching vs. live queries?

## Summary

This RFC defines Ryoma's **Open Catalog** vision:

1. **One abstraction** for all metadata across systems
2. **Deterministic, reproducible** search without embeddings
3. **LLM-native** design for agent-driven exploration
4. **Claude Code–style** iterative refinement workflow
5. **Debuggable, auditable** metadata operations

**Key Principles**:
- Treat metadata like source code
- Search → Narrow → Inspect → Query
- No guessing, no assumptions, no hallucinations
- Explainable, traceable, reproducible

**Next Steps**:
1. Review and approve this RFC
2. Implement core abstractions (Phase 1)
3. Build reference SQLite adapter
4. Gather feedback and iterate

---

**End of RFC-001**

---

*For questions or feedback, please open an issue in the Ryoma repository.*

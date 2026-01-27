# Pull Request: Introduce Open Catalog Metadata Search Framework (RFC-001)

## PR Type
- 🧩 **Architecture / Core Abstraction**
- 📄 **Documentation-First**
- 🛠️ **Scaffolding** (no production behavior changes yet)

## Summary

This PR introduces the **Open Catalog** metadata search framework for Ryoma AI, based on [RFC-001](./docs/source/rfc/RFC-001-open-catalog.md).

The goal is to establish a **database-agnostic, deterministic foundation** for answering natural-language questions about metadata from any data system (RDBMS, warehouse, lakehouse, streaming, etc.), using a **Claude Code–style search → narrow → inspect → query workflow**.

This PR is **intentionally non-invasive**:
- ✅ No changes to production code paths
- ✅ No vector search or embeddings
- ✅ No connector-specific logic
- ✅ Pure interface definitions and documentation

It focuses on **interfaces, abstractions, and documentation**, enabling incremental implementation in follow-up PRs.

---

## Motivation

### Current Challenges

Ryoma AI currently relies on vector-based catalog indexing for metadata search, which has several limitations:

1. **Fragmentation**: Metadata is scattered across different systems (RDBMS, data warehouses, lakehouses, streaming platforms)
2. **Opacity**: Vector embeddings are black boxes—hard to debug when retrieval fails
3. **Indexing Overhead**: Requires pre-indexing, vector stores, and embedding generation
4. **Hallucination Risk**: LLMs reason over incomplete or stale indexed metadata
5. **System-Specific Logic**: Each connector requires custom indexing code

### Example Scenario

**User**: "Show me customer revenue by region for Q4 2025"

**Current Flow (Vector-Based)**:
1. Generate embedding for "customer revenue region Q4"
2. Search vector store for similar tables
3. Retrieve top-k results (may miss relevant tables)
4. LLM generates SQL from incomplete context
5. Query fails or returns wrong results

**Problems**:
- What if "revenue" table wasn't indexed?
- What if embedding doesn't capture "Q4" temporal semantics?
- How do we debug why "regional_sales" wasn't retrieved?

### Proposed Solution

**Treat metadata like source code** — searchable, inspectable, deterministic.

Use structured search (glob, grep, filters) + LLM reasoning instead of embeddings:

```
search_tables(pattern="*customer*")  # Like: rg "customer"
→ narrow(filters={has_column: "email"})
→ inspect_table("customers")
→ verify_columns(["email", "created_at"])
→ generate_sql()
```

---

## What's Included

### 1. 📄 RFC (Authoritative Design)

**File**: [`docs/source/rfc/RFC-001-open-catalog.md`](./docs/source/rfc/RFC-001-open-catalog.md)

The complete specification defining:
- Problem statement and goals
- Core abstractions (MetadataElement, TableMetadata, ColumnMetadata)
- Search model (patterns, filters, operations)
- Agent workflow (iterative refinement)
- Implementation strategy (4 phases)
- Alternatives considered
- Success metrics

### 2. 🏗️ Core Abstractions

**Location**: `packages/ryoma_ai/ryoma_ai/catalog/open_catalog/`

#### Protocol Definition
**File**: [`protocol.py`](./packages/ryoma_ai/ryoma_ai/catalog/open_catalog/protocol.py)

Defines the `OpenCatalogAdapter` interface that all database-specific adapters must implement:

```python
class OpenCatalogAdapter(Protocol):
    def search_tables(
        self,
        pattern: Optional[str] = None,
        schema: Optional[str] = None,
        filters: Optional[SearchFilter] = None,
        limit: int = 100,
    ) -> List[TableMetadata]:
        """Search tables by pattern and filters."""
        ...

    def inspect_table(
        self,
        qualified_name: str,
        include_sample_data: bool = False,
    ) -> TableMetadata:
        """Get complete metadata for a table."""
        ...

    def get_relationships(
        self,
        table: str,
        direction: Literal["incoming", "outgoing", "both"] = "both",
    ) -> List[RelationshipMetadata]:
        """Get foreign key relationships."""
        ...

    # ... other operations
```

#### Metadata Models
**File**: [`models.py`](./packages/ryoma_ai/ryoma_ai/catalog/open_catalog/models.py)

Canonical dataclasses for metadata across all systems:
- `MetadataElement` (base)
- `TableMetadata` (tables, views, materialized views)
- `ColumnMetadata` (columns with types, constraints)
- `NamespaceMetadata` (schemas, databases)
- `RelationshipMetadata` (foreign keys, joins)
- `ForeignKeyRef` (FK references)

#### Search Filters
**File**: [`filters.py`](./packages/ryoma_ai/ryoma_ai/catalog/open_catalog/filters.py)

Declarative filters that translate to system-specific queries:

```python
@dataclass
class SearchFilter:
    # Column filters
    has_column: Optional[str]
    has_columns: Optional[List[str]]

    # Type filters
    has_primary_key: Optional[bool]
    has_foreign_keys: Optional[bool]

    # Size filters
    row_count_min: Optional[int]
    row_count_max: Optional[int]

    # Temporal filters
    modified_after: Optional[datetime]
    created_after: Optional[datetime]

    # Tag filters
    has_tag: Optional[str]
    has_tags: Optional[List[str]]

    # System-specific (extensible)
    properties: Dict[str, Any]
```

#### Exceptions
**File**: [`exceptions.py`](./packages/ryoma_ai/ryoma_ai/catalog/open_catalog/exceptions.py)

Clear, actionable error messages:
- `OpenCatalogError` (base)
- `TableNotFoundException` (with suggestions)
- `ColumnNotFoundException` (with available columns)
- `SearchTimeoutError` (with hints)
- `InvalidPatternError` (with syntax help)

### 3. 🔬 Reference Implementation

**Location**: `packages/ryoma_ai/ryoma_ai/catalog/adapters/reference/`

**File**: [`sqlite_adapter.py`](./packages/ryoma_ai/ryoma_ai/catalog/adapters/reference/sqlite_adapter.py)

A complete, working adapter for SQLite demonstrating:
- How to implement the protocol
- Pattern matching (glob → SQL LIKE)
- Filter translation (SearchFilter → SQL WHERE)
- Metadata extraction (sqlite_master, pragma_table_info)
- Relationship discovery (pragma_foreign_key_list)
- Caching strategy

**Example Usage**:
```python
from ryoma_data.sql import SqlDataSource
from ryoma_ai.catalog.adapters.reference import SQLiteOpenCatalogAdapter

datasource = SqlDataSource(uri="sqlite:///example.db")
adapter = SQLiteOpenCatalogAdapter(datasource)

# Search for customer tables with email column
filter = SearchFilter(has_column="email")
tables = adapter.search_tables(pattern="*customer*", filters=filter)

# Inspect specific table
table = adapter.inspect_table("customers")
print(f"Columns: {[col.name for col in table.columns]}")

# Get relationships
relationships = adapter.get_relationships("customers")
for rel in relationships:
    print(f"{rel.from_table} → {rel.to_table}")
```

### 4. 📚 Documentation

#### RFC Document
Comprehensive specification with:
- Problem statement
- Design overview
- Implementation strategy
- Agent workflow examples
- Performance considerations
- Alternatives considered
- Migration path

#### README
**File**: [`packages/ryoma_ai/ryoma_ai/catalog/open_catalog/README.md`](./packages/ryoma_ai/ryoma_ai/catalog/open_catalog/README.md)

User-facing documentation with:
- Quick start guide
- Usage examples
- Filter reference
- Pattern matching syntax
- Agent workflow walkthrough
- Error handling
- Best practices
- Custom adapter guide

---

## File Structure

```
ryoma/
├── docs/
│   └── source/
│       └── rfc/
│           └── RFC-001-open-catalog.md  ← RFC specification
│
├── packages/
│   └── ryoma_ai/
│       └── ryoma_ai/
│           └── catalog/
│               ├── open_catalog/
│               │   ├── __init__.py     ← Public API exports
│               │   ├── protocol.py     ← OpenCatalogAdapter protocol
│               │   ├── models.py       ← Metadata dataclasses
│               │   ├── filters.py      ← SearchFilter specification
│               │   ├── exceptions.py   ← Error classes
│               │   └── README.md       ← User documentation
│               │
│               └── adapters/
│                   ├── __init__.py
│                   └── reference/
│                       ├── __init__.py
│                       └── sqlite_adapter.py  ← Reference implementation
│
└── OPEN_CATALOG_PR.md  ← This file
```

---

## Design Highlights

### 1. Claude Code–Style Workflow

The agent follows an iterative refinement process:

```
User: "Show customer emails from last month"
  ↓
Step 1: BROAD SEARCH
  search_tables(pattern="*customer*")
  → [customers, customer_orders, customer_feedback, ...] (23 tables)
  ↓
Step 2: NARROW BY COLUMN
  search_tables(pattern="*customer*", filters={has_column: "email"})
  → [customers, customer_feedback] (2 tables)
  ↓
Step 3: INSPECT SCHEMA
  inspect_table("customers")
  → {columns: [id, name, email, created_at, region]}
  ↓
Step 4: CHECK RELATIONSHIPS
  get_relationships("customers")
  → [{from: "orders", to: "customers", on: "customer_id"}]
  ↓
Step 5: VERIFY TEMPORAL COLUMN
  Check: created_at (TIMESTAMP) ✓
  ↓
Step 6: GENERATE QUERY
  SELECT email FROM customers
  WHERE created_at >= DATE_TRUNC('month', NOW() - INTERVAL '1 month')
```

### 2. Pattern Matching

Glob-style patterns that translate to SQL:

| Pattern           | SQL Translation           |
|-------------------|---------------------------|
| `"*customer*"`    | `LIKE '%customer%'`       |
| `"dim_*"`         | `LIKE 'dim_%'`            |
| `"fact_*_daily"`  | `LIKE 'fact_%_daily'`     |

### 3. Declarative Filters

System-agnostic filters that adapt to each database:

```python
filter = SearchFilter(
    has_column="email",
    row_count_min=1000,
    modified_after=datetime(2025, 1, 1)
)

# PostgreSQL translation:
"""
WHERE EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE columns.table_name = tables.table_name
    AND columns.column_name = 'email'
)
AND pg_stat_user_tables.n_live_tup >= 1000
AND pg_stat_user_tables.last_autovacuum > '2025-01-01'
"""

# SQLite translation:
"""
WHERE EXISTS (
    SELECT 1 FROM pragma_table_info(sqlite_master.name)
    WHERE name = 'email'
)
-- (row count and modified_after require table scan)
"""
```

### 4. Debuggability

Every operation is traceable:

```
[Open Catalog Trace] Query: "customer revenue by region"

Step 1: search_tables(pattern="*customer*")
  ├─ SQL: SELECT ... FROM information_schema.tables WHERE ...
  ├─ Duration: 45ms
  └─ Results: 23 tables

Step 2: search_tables(pattern="*customer*", filters={has_column:"revenue"})
  ├─ SQL: SELECT ... WHERE EXISTS (... column_name = 'revenue')
  ├─ Duration: 120ms
  └─ Results: 2 tables

Total: 165ms, 2 operations
```

---

## Non-Goals (For This PR)

This PR intentionally **does not** include:

- ❌ Production agent integration
- ❌ Changes to existing catalog search
- ❌ Vector search modifications
- ❌ Connector implementations (Postgres, Snowflake, etc.)
- ❌ LangChain tool definitions
- ❌ CLI commands
- ❌ Performance optimizations

These will come in follow-up PRs.

---

## Implementation Phases

### Phase 1: Core Abstractions ✅ **(This PR)**

**Goal**: Establish interfaces and documentation

**Deliverables**:
- [x] RFC-001 specification
- [x] OpenCatalogAdapter protocol
- [x] Metadata models (MetadataElement, TableMetadata, etc.)
- [x] SearchFilter specification
- [x] Exception classes
- [x] SQLite reference adapter
- [x] Documentation and README

### Phase 2: Adapter Implementations (Future PR)

**Goal**: Implement adapters for production databases

**Connectors** (priority order):
1. PostgreSQL
2. Snowflake
3. DuckDB
4. BigQuery
5. MySQL/MariaDB
6. Delta Lake

### Phase 3: Agent Integration (Future PR)

**Goal**: Create Open Catalog–aware tools and agent modes

**New Tools**:
- `OpenCatalogSearchTool`
- `InspectTableTool`
- `RelationshipDiscoveryTool`

**Agent Mode**:
```python
SqlAgent(
    model="claude-sonnet-4",
    mode="enhanced",
    catalog_strategy="open_catalog"  # New option
)
```

### Phase 4: Hybrid Strategy (Future PR)

**Goal**: Allow mixing Open Catalog + vector search

Use Open Catalog for exact matches, vector for semantic similarity.

---

## Testing Strategy

### For This PR

**Manual Testing**:
- SQLite adapter can search, inspect, and discover relationships
- Filters work as expected
- Pattern matching translates correctly
- Error messages are actionable

### For Future PRs

**Unit Tests**:
- Each adapter implementation
- Filter translation
- Pattern matching
- Error handling

**Integration Tests**:
- Agent workflows end-to-end
- Cross-system searches
- Performance benchmarks

---

## Backward Compatibility

✅ **100% Backward Compatible**

This PR:
- Adds new code only, no modifications to existing code
- Does not change any public APIs
- Does not affect existing catalog search behavior
- Can be safely merged without impacting users

---

## Performance Considerations

**Concern**: "Won't querying `information_schema` be slow?"

**Response**:
1. **Caching**: Adapters cache results with TTL (e.g., 5 minutes)
2. **Lazy Loading**: Only fetch full schema when inspecting specific tables
3. **Parallel Queries**: Search operations can run concurrently
4. **Index Hints**: Use system catalog indexes (information_schema is usually indexed)
5. **Progressive Refinement**: Narrow search space quickly (1000 tables → 10 → 1)

**Target Benchmarks** (Phase 2):
- Search 10K tables: < 500ms
- Inspect single table: < 100ms
- Get relationships: < 200ms

---

## Alternatives Considered

### Alternative 1: Improve Vector Search

**Rejected**: Still requires indexing, still opaque, doesn't solve freshness

### Alternative 2: Full-Text Search (Elasticsearch)

**Rejected**: Too heavyweight, another infrastructure dependency

### Alternative 3: GraphQL-Style Metadata API

**Rejected**: Mismatch with agent workflow, overly complex for structured metadata

See RFC for detailed analysis.

---

## Success Metrics

**How we'll measure success (Phase 3+)**:

1. **Correctness**: 95% of queries identify correct tables
2. **Debuggability**: 100% of failures explainable from trace logs
3. **Latency**: P95 search latency < 500ms for 10K tables
4. **Adoption**: 20% of users enable `open_catalog` mode
5. **Agent Iterations**: <5 search steps per query on average

---

## Migration Path

### For Users

**No Breaking Changes**:
- Vector-based catalog search remains default
- Open Catalog is opt-in via agent configuration

**Gradual Adoption**:
```python
# Phase 1: Both available
agent = SqlAgent(catalog_strategy="hybrid")

# Phase 2: Open Catalog default
agent = SqlAgent(catalog_strategy="open_catalog")

# Phase 3: Vector deprecated (v0.5.0+)
```

---

## Related Issues

- Closes: N/A (new feature)
- Related: #XXX (if applicable)
- RFC: [RFC-001](./docs/source/rfc/RFC-001-open-catalog.md)

---

## Checklist

- [x] RFC document created and complete
- [x] Core abstractions implemented
  - [x] OpenCatalogAdapter protocol
  - [x] Metadata models (MetadataElement, TableMetadata, etc.)
  - [x] SearchFilter specification
  - [x] Exception classes
- [x] Reference implementation (SQLite adapter)
- [x] Documentation
  - [x] RFC specification
  - [x] README with examples
  - [x] Code documentation (docstrings)
- [x] No production code changes
- [x] Backward compatible
- [ ] Reviewed by maintainers
- [ ] Feedback incorporated

---

## Next Steps (After Merge)

1. **Phase 2 PR**: Implement PostgreSQL and Snowflake adapters
2. **Phase 3 PR**: Create LangChain tools and agent integration
3. **Phase 4 PR**: Implement hybrid strategy (Open Catalog + Vector)
4. **Documentation**: Update user guides with Open Catalog examples

---

## Questions for Reviewers

1. **Abstraction Level**: Is the `OpenCatalogAdapter` protocol at the right level of abstraction?
2. **Filter Design**: Are the `SearchFilter` options comprehensive enough for Phase 1?
3. **Error Handling**: Are the exception types appropriate? Should we add more?
4. **Naming**: Is "Open Catalog" the right name, or should we consider alternatives?
5. **SQLite Adapter**: Does the reference implementation clearly demonstrate the protocol?

---

## Additional Context

### Inspiration

- **Claude Code Search**: Glob → Grep → Read workflow for code exploration
- **SQL INFORMATION_SCHEMA**: Standard metadata interface
- **Trino Metadata API**: System-agnostic metadata abstraction
- **DBT Catalog**: Declarative metadata management

### References

- [PostgreSQL INFORMATION_SCHEMA](https://www.postgresql.org/docs/current/information-schema.html)
- [Snowflake INFORMATION_SCHEMA](https://docs.snowflake.com/en/sql-reference/info-schema)
- [Trino Metadata Protocol](https://trino.io/docs/current/develop/spi-overview.html)
- [Claude Code Agent SDK](https://docs.anthropic.com/claude/docs/claude-agent)

---

**Thank you for reviewing!** 🙏

This PR lays the foundation for a more deterministic, debuggable, and system-agnostic approach to metadata search in Ryoma AI.

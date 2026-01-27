# Open Catalog - Database-Agnostic Metadata Search

> **Status**: 🚧 **Experimental** - Part of RFC-001 implementation
>
> This framework is currently in scaffolding phase. APIs may change.

## Overview

Open Catalog provides a **zero-indexing, deterministic metadata search framework** for Ryoma AI. Instead of relying on vector embeddings and pre-indexed catalogs, Open Catalog treats metadata like source code—searchable, inspectable, and verifiable using pattern matching and filters.

## Key Principles

1. **No Vector Indexing**: Search metadata directly using glob patterns and filters
2. **Deterministic**: Same query always returns same results
3. **System-Agnostic**: Works uniformly across SQL, NoSQL, data warehouses, lakehouses
4. **LLM-Native**: Designed for agent-driven exploration (Claude Code style)
5. **Debuggable**: Every search operation is traceable and explainable

## Architecture

```
┌──────────────────────────────────────┐
│     LLM Agent (Claude)               │
│  "Find customer tables with email"   │
└─────────────┬────────────────────────┘
              │
              ▼
┌──────────────────────────────────────┐
│     OpenCatalogAdapter Protocol       │
│  - search_tables(pattern, filters)   │
│  - search_columns(pattern, table)    │
│  - inspect_table(name)               │
│  - get_relationships(table)          │
└─────────────┬────────────────────────┘
              │
     ┌────────┴────────┬───────────┐
     ▼                 ▼           ▼
┌──────────┐   ┌──────────┐  ┌──────────┐
│ SQLite   │   │ Postgres │  │ Snowflake│
│ Adapter  │   │ Adapter  │  │ Adapter  │
└──────────┘   └──────────┘  └──────────┘
```

## Quick Start

### 1. Create an Adapter

```python
from ryoma_data.sql import SqlDataSource
from ryoma_ai.catalog.adapters.reference import SQLiteOpenCatalogAdapter

# Connect to database
datasource = SqlDataSource(uri="sqlite:///example.db")

# Create Open Catalog adapter
adapter = SQLiteOpenCatalogAdapter(datasource)
```

### 2. Search for Tables

```python
from ryoma_ai.catalog.open_catalog import SearchFilter

# Search for customer-related tables
tables = adapter.search_tables(pattern="*customer*", limit=10)
for table in tables:
    print(f"{table.name}: {table.row_count} rows")

# Filter by column existence
filter = SearchFilter(has_column="email")
tables = adapter.search_tables(
    pattern="*customer*",
    filters=filter
)
```

### 3. Inspect Table Schema

```python
# Get complete metadata for a table
table = adapter.inspect_table("customers")

print(f"Table: {table.name}")
print(f"Columns:")
for col in table.columns:
    print(f"  - {col.name}: {col.data_type}")
    if col.primary_key:
        print(f"    [PRIMARY KEY]")
    if col.foreign_keys:
        for fk in col.foreign_keys:
            print(f"    [FK → {fk.referenced_table}.{fk.referenced_column}]")
```

### 4. Discover Relationships

```python
# Find all tables that reference customers
relationships = adapter.get_relationships(
    "customers",
    direction="incoming"
)

for rel in relationships:
    print(f"{rel.from_table} → {rel.to_table}")
    print(f"  ON {rel.from_columns} = {rel.to_columns}")
```

### 5. Get Sample Data

```python
# Inspect actual data values
rows = adapter.get_sample_data("customers", limit=5)
for row in rows:
    print(row)

# Get specific columns only
rows = adapter.get_sample_data(
    "customers",
    columns=["email", "created_at"],
    limit=10
)
```

## Agent Workflow Example

Here's how an LLM agent would use Open Catalog to answer:
**"Show me customer emails from last month"**

```python
from ryoma_ai.catalog.open_catalog import SearchFilter

# Step 1: Search for customer tables
agent.thought("Let me search for customer-related tables")
tables = adapter.search_tables(pattern="*customer*")
# Returns: [customers, customer_orders, customer_feedback] (10 tables)

# Step 2: Narrow by column
agent.thought("Which tables have email columns?")
filter = SearchFilter(has_column="email")
tables = adapter.search_tables(
    pattern="*customer*",
    filters=filter
)
# Returns: [customers, customer_feedback] (2 tables)

# Step 3: Inspect schema
agent.thought("Let me check the customers table structure")
table = adapter.inspect_table("customers")
# Returns: {columns: [id, name, email, created_at, ...]}

# Step 4: Verify temporal column
agent.thought("Does it have a date column for filtering?")
date_columns = [col for col in table.columns if "date" in col.name.lower()]
# Returns: [created_at (TIMESTAMP)]

# Step 5: Generate query
agent.thought("I have all the information I need")
sql = """
    SELECT email
    FROM customers
    WHERE created_at >= DATE_TRUNC('month', NOW() - INTERVAL '1 month')
"""
```

## Search Filters

### Column-Based Filters

```python
# Has specific column
SearchFilter(has_column="email")

# Has all columns
SearchFilter(has_columns=["email", "created_at"])

# Has any of these columns
SearchFilter(has_any_columns=["email", "email_address"])
```

### Type-Based Filters

```python
# Has primary key
SearchFilter(has_primary_key=True)

# Has foreign keys
SearchFilter(has_foreign_keys=True)

# Column type
SearchFilter(column_type="VARCHAR")
```

### Size-Based Filters

```python
# Minimum row count
SearchFilter(row_count_min=1000)

# Size range
SearchFilter(
    row_count_min=1000,
    row_count_max=100000
)
```

### Temporal Filters

```python
from datetime import datetime

# Modified after date
SearchFilter(
    modified_after=datetime(2025, 1, 1)
)

# Created in range
SearchFilter(
    created_after=datetime(2025, 1, 1),
    created_before=datetime(2025, 12, 31)
)
```

### Combining Filters

```python
# Multiple conditions
filter = SearchFilter(
    has_column="email",
    row_count_min=1000,
    has_primary_key=True,
    modified_after=datetime(2025, 1, 1)
)

tables = adapter.search_tables(
    pattern="*customer*",
    filters=filter
)
```

## Pattern Matching

Open Catalog uses glob-style patterns:

| Pattern           | Matches                           |
|-------------------|-----------------------------------|
| `"*customer*"`    | Any table containing "customer"   |
| `"dim_*"`         | Tables starting with "dim_"       |
| `"*_daily"`       | Tables ending with "_daily"       |
| `"fact_?_summary"`| Single character wildcard         |

```python
# Find all dimension tables
dim_tables = adapter.search_tables(pattern="dim_*")

# Find all daily fact tables
daily_facts = adapter.search_tables(pattern="fact_*_daily")

# Find specific pattern
tables = adapter.search_tables(pattern="customer_orders_202?")
```

## Error Handling

### Table Not Found

```python
from ryoma_ai.catalog.open_catalog import TableNotFoundException

try:
    table = adapter.inspect_table("nonexistent_table")
except TableNotFoundException as e:
    print(f"Table not found: {e.table_name}")
    print(f"Did you mean: {e.suggested_tables}")
```

### Column Not Found

```python
from ryoma_ai.catalog.open_catalog import ColumnNotFoundException

try:
    exists = adapter.validate_column_exists("customers", "nonexistent_col")
except ColumnNotFoundException as e:
    print(f"Column '{e.column_name}' not found in '{e.table_name}'")
    print(f"Available columns: {e.available_columns}")
```

### Search Timeout

```python
from ryoma_ai.catalog.open_catalog import SearchTimeoutError

try:
    tables = adapter.search_tables(pattern="*", limit=100000)
except SearchTimeoutError as e:
    print(f"Search timed out: {e.message}")
    print(f"Hint: {e.details.get('hint')}")
```

## Implementing a Custom Adapter

To support a new database system, implement the `OpenCatalogAdapter` protocol:

```python
from ryoma_ai.catalog.open_catalog import (
    OpenCatalogAdapter,
    TableMetadata,
    ColumnMetadata,
    SearchFilter,
)

class MyDatabaseAdapter:
    """Custom adapter for MyDatabase."""

    def __init__(self, datasource):
        self.datasource = datasource

    def search_tables(
        self,
        pattern: Optional[str] = None,
        schema: Optional[str] = None,
        filters: Optional[SearchFilter] = None,
        limit: int = 100,
    ) -> List[TableMetadata]:
        # Translate to system-specific query
        query = self._build_search_query(pattern, schema, filters)

        # Execute and convert to TableMetadata
        results = self.datasource.query(query)
        return [self._parse_table(row) for row in results]

    def inspect_table(self, qualified_name: str) -> TableMetadata:
        # Fetch complete table metadata
        ...

    # Implement other required methods
    ...
```

See `sqlite_adapter.py` for a complete reference implementation.

## Best Practices

### 1. Use Pattern Narrowing

```python
# ❌ Too broad
tables = adapter.search_tables(pattern="*")

# ✅ Start specific
tables = adapter.search_tables(pattern="*customer*")
```

### 2. Apply Filters Early

```python
# ❌ Filter in code
tables = adapter.search_tables(pattern="*customer*")
tables = [t for t in tables if any(c.name == "email" for c in t.columns)]

# ✅ Filter in adapter (faster)
filter = SearchFilter(has_column="email")
tables = adapter.search_tables(pattern="*customer*", filters=filter)
```

### 3. Cache Inspection Results

```python
# ❌ Re-inspect repeatedly
for _ in range(10):
    table = adapter.inspect_table("customers")

# ✅ Cache and reuse
table = adapter.inspect_table("customers")
# Use cached table metadata
```

### 4. Validate Before Querying

```python
# ✅ Check existence first
if adapter.validate_table_exists("customers"):
    if adapter.validate_column_exists("customers", "email"):
        # Safe to query
        sql = "SELECT email FROM customers"
```

## Debugging

Enable debug logging to trace operations:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("ryoma_ai.catalog.open_catalog")
logger.setLevel(logging.DEBUG)

# Now see detailed traces
tables = adapter.search_tables(pattern="*customer*")
```

Output:
```
DEBUG:ryoma_ai.catalog.open_catalog:Searching tables: pattern=*customer*, filters=None
DEBUG:ryoma_ai.catalog.open_catalog:Found 5 tables
```

## Comparison: Vector Search vs Open Catalog

| Aspect | Vector Search (Current) | Open Catalog (This RFC) |
|--------|------------------------|-------------------------|
| **Setup** | Requires indexing + embeddings | Direct query, no indexing |
| **Latency** | Fast (pre-indexed) | Moderate (on-demand) |
| **Freshness** | Stale (indexed data) | Always fresh |
| **Debuggability** | Opaque (why this result?) | Explicit (pattern + filters) |
| **Explainability** | Low | High |
| **Cross-system** | Requires per-system indexing | Uniform interface |

## Roadmap

- [x] **Phase 1**: Core abstractions and RFC (this package)
- [ ] **Phase 2**: Adapter implementations (Postgres, Snowflake, etc.)
- [ ] **Phase 3**: Agent integration (tools and workflows)
- [ ] **Phase 4**: Hybrid strategy (Open Catalog + Vector search)

## Related Documentation

- [RFC-001: Open Catalog](../../../../../../docs/source/rfc/RFC-001-open-catalog.md)
- [Protocol Definition](./protocol.py)
- [Models](./models.py)
- [Filters](./filters.py)
- [SQLite Adapter (Reference)](../adapters/reference/sqlite_adapter.py)

## Contributing

This is an experimental framework. Feedback and contributions are welcome!

To implement a new adapter:
1. Implement the `OpenCatalogAdapter` protocol
2. Add tests demonstrating search, inspection, and relationships
3. Submit a PR with documentation

---

For questions or discussions, please open an issue in the Ryoma repository.

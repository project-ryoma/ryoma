# Changelog

All notable changes to the Ryoma AI project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased] - v0.2.0

**Status:** In Development (63% complete)
**Branch:** `claude/understand-codebase-Suw7u`
**Release Date:** TBD

### 🎯 Overview

Major architectural refactoring to improve separation of concerns, reduce coupling, and provide cleaner APIs. This release includes **breaking changes** but results in a much more maintainable and extensible codebase.

**For detailed progress:** See [Refactoring Progress](docs/plans/REFACTORING_PROGRESS.md)

### ✨ Added

#### New Service Layer
- **DataSourceService** - Centralized datasource management
  - `add_datasource()`, `get_active_datasource()`, `set_active_datasource()`
  - `list_datasources()`, `remove_datasource()`, `has_active_datasource()`
- **CatalogService** - Catalog indexing and search operations
  - `index_datasource()`, `search_tables()`, `search_columns()`
  - `get_table_suggestions()`, `get_column_suggestions()`
- **AgentBuilder** - Convenience service for building agents
  - `build_sql_agent(model, mode)` - Create SQL agents (basic/enhanced/reforce)
  - `build_python_agent(model)` - Create Python execution agents
  - `build_chat_agent(model, system_prompt)` - Create chat agents

#### New Domain Layer
- **StoreKeys** - Centralized constants for store keys
  - `ACTIVE_DATASOURCE`, `DATASOURCES_PREFIX`, `ACTIVE_DATASOURCE_ID`, `DATASOURCE_IDS`
- **AgentDefaults** - Default configuration values
  - `DEFAULT_MODEL`, `DEFAULT_TEMPERATURE`, `MAX_ITERATIONS`, `DEFAULT_TOP_K`
- **Protocol Interfaces** - Type-safe contracts
  - `DataSourceRepository`, `CatalogIndexer`, `CatalogSearcher`

#### New Infrastructure Layer
- **StoreBasedDataSourceRepository** - Concrete datasource repository
- **CatalogIndexerAdapter** - Wraps existing catalog indexing service
- **CatalogSearcherAdapter** - Wraps existing catalog search service

#### Centralized Tools
- **sql_tools.py** - Single source of truth for SQL tool definitions
  - `get_basic_sql_tools()` - Core SQL tools (query, create, profile)
  - `get_enhanced_sql_tools()` - Advanced tools (+ explain, optimize)
  - `get_reforce_sql_tools()` - ReFoRCE mode tools

### 🔄 Changed

#### BaseAgent (Breaking Changes)
- **Simplified from 359 → 157 lines** (-56% reduction)
- **New signature:** `__init__(model, tools, system_prompt, store)`
- **Removed parameters:** `datasource`, `embedding`, `vector_store`
- **Removed methods:**
  - `add_datasource()`, `get_datasource()`
  - `index_datasource()`, `search_catalogs()`
  - `init_embedding()`, `init_vector_store()`
  - All catalog-related methods (15+ methods)
- **Focus:** Now only handles conversation logic, no infrastructure

#### ChatAgent (Breaking Changes)
- Updated to accept `Union[str, BaseChatModel]` for model parameter
- Loads model using `load_model_provider()` if string provided
- Passes loaded model to BaseAgent with new signature
- Removed datasource/embedding/vector_store parameters

#### WorkflowAgent (Breaking Changes)
- Updated parameter order: `model` first, then `tools`
- Changed signature to match new BaseAgent
- Properly passes all parameters to ChatAgent parent
- Removed infrastructure-related parameters

#### SqlAgent (Breaking Changes)
- **Factory method** updated to remove old parameters
- **BasicSqlAgent:** Uses centralized `get_basic_sql_tools()`
- **EnhancedSqlAgentImpl:** Uses centralized `get_enhanced_sql_tools()`
- **ReFoRCESqlAgentImpl:** Uses centralized `get_reforce_sql_tools()`
- **All variants:** Accept `Union[str, BaseChatModel]`, use `store` for InjectedStore

#### Tools
- Replaced magic string `"datasource_main"` with `StoreKeys.ACTIVE_DATASOURCE`
- All SQL tools now use constants from domain layer

### 📝 Documentation

- **NEW:** [Documentation Index](docs/INDEX.md) - Central hub for all documentation
- **NEW:** [Test Organization Plan](docs/TEST_ORGANIZATION.md) - Test suite reorganization
- **NEW:** [Architecture Comparison](docs/ARCHITECTURE_COMPARISON.md) - Before/after visuals
- **NEW:** [Refactoring Summary](docs/REFACTORING_SUMMARY.md) - Quick reference
- **UPDATED:** Progress tracking in [docs/plans/](docs/plans/)

### 🔧 Migration Guide

#### For v0.1.x Users

**Old API (v0.1.x - Deprecated):**
```python
from ryoma_ai.agent.sql import SqlAgent
from ryoma_ai.datasource import PostgresDataSource

datasource = PostgresDataSource("postgresql://...")
agent = SqlAgent(
    model="gpt-4",
    datasource=datasource,
    embedding={"model": "openai"},
    vector_store={"type": "qdrant"},
)
```

**New API (v0.2.0 - Recommended):**
```python
from ryoma_ai.services import AgentBuilder, DataSourceService
from ryoma_ai.infrastructure.datasource_repository import StoreBasedDataSourceRepository
from ryoma_ai.datasource import PostgresDataSource
from langchain_core.stores import InMemoryStore

# Create datasource
datasource = PostgresDataSource("postgresql://...")

# Setup services
store = InMemoryStore()
repo = StoreBasedDataSourceRepository(store)
datasource_service = DataSourceService(repo)
datasource_service.add_datasource(datasource)

# Build agent
builder = AgentBuilder(datasource_service=datasource_service)
agent = builder.build_sql_agent(model="gpt-4", mode="enhanced")
```

**Direct Instantiation (v0.2.0 - Also Supported):**
```python
from ryoma_ai.agent.sql import SqlAgent
from langchain_core.stores import InMemoryStore

store = InMemoryStore()
# Add datasource to store first
store.mset([("datasource_main", datasource)])

agent = SqlAgent(
    model="gpt-4",
    mode="enhanced",
    store=store
)
```

#### Key Changes Summary

1. **Infrastructure moved to services:**
   - Datasource management → `DataSourceService`
   - Catalog operations → `CatalogService`
   - Agent creation → `AgentBuilder`

2. **BaseAgent simplified:**
   - Only handles conversation logic
   - Uses `store` parameter for InjectedStore pattern
   - No more datasource/embedding/vector_store in constructor

3. **Centralized definitions:**
   - Constants in `domain/constants.py`
   - Tool definitions in `agent/sql_tools.py`
   - Protocols in `domain/interfaces.py`

### 🚧 Known Issues

- Some unit tests need updates for new API
- CLI needs refactoring to use new services (planned)
- Documentation examples still show v0.1.x API in some places

### 📊 Development Statistics

- **Steps Completed:** 5 of 8 (63%)
- **Files Created:** 15 new files
- **Files Modified:** 6 major files
- **Lines Added:** ~2,300
- **Lines Removed:** ~700
- **Net Change:** +1,600 lines
- **Commits:** 7 clean commits

### 🎯 Remaining Work

1. **Step 2.5:** Refactor CLI to use services (2-3 hours)
2. **Step 2.7:** Update tests for new API (2 hours)
3. **Step 2.8:** Update documentation examples (1 hour)

---

## [0.1.x] - Current Stable

**Status:** Maintenance mode
**Last Updated:** 2026-01-20

### Features

- SQL Agent with basic, enhanced, and ReFoRCE modes
- Python code execution agent
- Pandas DataFrame agent
- CLI interface (ryoma_cli)
- Lab UI (ryoma_lab)
- Support for multiple LLM providers
- Support for various data sources (PostgreSQL, MySQL, Snowflake, BigQuery, etc.)
- Catalog indexing and semantic search
- Jupyter notebook integration

### Architecture

- Monolithic BaseAgent with all functionality
- Direct datasource management in agents
- Embedding and vector store initialization in agents
- Tool definitions duplicated across agent modes

---

## Release Notes Format

Each release entry should include:

- **[Version]** - Release date or status
- **Added** - New features
- **Changed** - Changes to existing functionality
- **Deprecated** - Features marked for removal
- **Removed** - Features removed in this version
- **Fixed** - Bug fixes
- **Security** - Security fixes

For breaking changes, include migration examples.

---

**Next Release:** v0.2.0 (In Development)
**Previous Release:** v0.1.x (Current Stable)

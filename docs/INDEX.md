# Ryoma AI Documentation Index

**Welcome to the Ryoma AI documentation!** This index helps you navigate all available documentation organized by purpose and audience.

---

## 📚 Getting Started

For new users starting with Ryoma AI:

1. **[Main README](../README.md)** - Project overview and quick start
2. **[Getting Started Guide](source/getting-started/)** - Detailed setup and configuration
   - [Advanced Setup](source/getting-started/advanced-setup.md)
   - [CLI Usage](source/getting-started/cli-usage.md)
   - [Configuration Reference](source/getting-started/configuration-reference.md)

---

## 📖 API Reference

### Current API (v0.1.x - Stable)

**Basic Usage:**
```python
from ryoma_ai.agent.sql import SqlAgent
from ryoma_ai.datasource import PostgresDataSource

# Create datasource
datasource = PostgresDataSource("postgresql://user:password@localhost:5432/dbname")

# Create agent
agent = SqlAgent("gpt-3.5-turbo").add_datasource(datasource)

# Ask questions
agent.stream("What are the top 5 customers?", display=True)
```

**For detailed API documentation, see:**
- [SQL Agent Quick Reference](source/architecture/sql-agent-quick-reference.md)
- [Architecture Overview](source/architecture/architecture.md)

### Upcoming API (v0.2.0 - In Development)

**New Service-Based API:**
```python
from ryoma_ai.services import AgentBuilder, DataSourceService

# Setup services
datasource_service = DataSourceService(...)
builder = AgentBuilder(datasource_service=datasource_service)

# Build agent
agent = builder.build_sql_agent(model="gpt-4", mode="enhanced")
```

**For migration information, see:**
- **[CHANGELOG.md](../CHANGELOG.md)** - Detailed changelog with migration guide
- [Architecture Comparison](ARCHITECTURE_COMPARISON.md) - Visual comparison

---

## 🏗️ Architecture Documentation

Understanding Ryoma AI's internal structure:

- **[Store Architecture](source/architecture/store-architecture.md)** - InjectedStore pattern explained
- **[SQL Agent Design](source/architecture/enhanced-sql-agent.md)** - SQL agent architecture
- **[Database Profiling](source/architecture/database-profiling.md)** - Performance profiling features
- **[Architecture Comparison](ARCHITECTURE_COMPARISON.md)** - v0.1.x vs v0.2.0 (for contributors)

---

## 🛠️ Development

For contributors and maintainers:

- **[Contribution Guide](source/contribution/contribution.md)** - How to contribute
- **[Testing Guide](#testing-guide)** - Running and writing tests (see below)
- **[CHANGELOG.md](../CHANGELOG.md)** - Version history and release notes

### Active Development

Current development work on v0.2.0 architectural improvements:

- **[Refactoring Progress](plans/REFACTORING_PROGRESS.md)** - Live progress (63% complete)
- **[Direct Refactoring Plan](plans/DIRECT_REFACTORING_PLAN.md)** - Implementation plan
- **[Refactoring Summary](REFACTORING_SUMMARY.md)** - Quick reference

_Note: These documents are for active contributors working on the v0.2.0 refactoring._

### Testing Guide

**Test Organization:**

```
tests/
├── unit_tests/          # Unit tests for individual components
│   ├── test_agent.py
│   ├── test_catalog.py
│   ├── test_datasource.py
│   └── datasource/
│       └── test_duckdb.py
└── e2e/                 # End-to-end integration tests
    └── ryoma_ai/
        ├── test_agent.py
        ├── test_datasource.py
        └── test_llm.py

packages/ryoma_ai/tests/ # Package-specific tests
├── agent/              # Agent-specific tests
│   ├── test_sql_agent_gemini.py
│   ├── test_workflow_error_handling.py
│   └── test_sql_approval_*.py
├── llm/                # LLM provider tests
│   └── test_model_provider.py
└── unit/               # New architecture unit tests
    └── services/
        ├── test_datasource_service.py
        └── test_catalog_service.py
```

**Running Tests:**

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit_tests/           # Unit tests only
pytest tests/e2e/                  # E2E tests only
pytest packages/ryoma_ai/tests/    # Package tests only

# Run specific test file
pytest tests/unit_tests/test_agent.py

# Run with coverage
pytest --cov=ryoma_ai --cov-report=html
```

**Test Status After Refactoring:**
- ✅ Service layer tests (datasource, catalog) - passing
- ⚠️ Legacy agent tests - need updates for new API
- 📝 AgentBuilder tests - need to be added

---

## 📖 API Reference

### Current API (v0.2.0+)

**Service Layer:**
```python
from ryoma_ai.services import AgentBuilder, DataSourceService, CatalogService

# Build agents
builder = AgentBuilder(datasource_service, catalog_service)
agent = builder.build_sql_agent(model="gpt-4", mode="enhanced")

# Manage datasources
datasource_service.add_datasource(datasource)
datasource_service.get_active_datasource()

# Catalog operations
catalog_service.index_datasource(datasource_id, level="table")
catalog_service.search_tables(query, top_k=5)
```

**Direct Agent Usage:**
```python
from ryoma_ai.agent import SqlAgent, ChatAgent, WorkflowAgent

# SQL agents (basic, enhanced, reforce)
agent = SqlAgent(model="gpt-4", mode="enhanced", store=store)

# Chat agents
agent = ChatAgent(model="gpt-4", system_prompt="You are a helpful assistant.")

# Custom workflow agents
agent = WorkflowAgent(model="gpt-4", tools=tools, store=store)
```

### Legacy API (v0.1.x) - Deprecated

See [Architecture Overview](source/architecture/architecture.md) for deprecated APIs.

---

## 📝 Documentation Organization

### Directory Structure

```
docs/
├── INDEX.md                          # This file - documentation index
├── ARCHITECTURE_COMPARISON.md        # Architecture before/after comparison
├── REFACTORING_SUMMARY.md           # Quick reference of changes
├── plans/                           # Refactoring plans and progress
│   ├── DIRECT_REFACTORING_PLAN.md  # Current plan (active)
│   ├── MIGRATION_PLAN.md           # Original plan (archived)
│   ├── REFACTORING_PROGRESS.md     # Live progress tracker
│   └── PHASE_1_COMPLETE.md         # Phase 1 summary
└── source/                          # Sphinx/static documentation
    ├── architecture/                # Architecture docs (mixed new/legacy)
    ├── contribution/                # Contribution guides
    └── getting-started/             # Getting started guides
```

### Documentation Status

| Document | Status | Notes |
|----------|--------|-------|
| INDEX.md | ✅ Current | This file |
| ARCHITECTURE_COMPARISON.md | ✅ Current | Updated with v0.2.0 changes |
| REFACTORING_SUMMARY.md | ✅ Current | Quick reference |
| plans/DIRECT_REFACTORING_PLAN.md | ✅ Current | Active plan |
| plans/REFACTORING_PROGRESS.md | ✅ Current | Live tracker (63% complete) |
| plans/MIGRATION_PLAN.md | 📦 Archived | Reference only |
| plans/PHASE_1_COMPLETE.md | ✅ Current | Historical record |
| source/architecture/* | ⚠️ Mixed | Mix of v0.1.x and v0.2.0 docs |
| source/getting-started/* | ⚠️ Needs Update | Still shows v0.1.x API |

**Next Steps:**
1. Complete refactoring (Step 2.5, 2.7, 2.8)
2. Update getting-started guides for v0.2.0
3. Create comprehensive migration guide
4. Update architecture docs to remove deprecated content

---

## 🔍 Quick Links

**Most Common Questions:**

1. **How do I get started?** → [Getting Started](#getting-started)
2. **How do I create an agent?** → [API Reference](#api-reference)
3. **What are the supported data sources?** → [Main README](../README.md#supported-data-sources)
4. **How do I run tests?** → [Testing Guide](#testing-guide)
5. **How do I contribute?** → [Contribution Guide](source/contribution/contribution.md)
6. **What's new in each version?** → [CHANGELOG.md](../CHANGELOG.md)

---

## 📮 Support & Feedback

- **Issues:** Report issues on the project GitHub repository
- **Questions:** Ask in project discussions or Slack channel
- **Contributions:** See [Contribution Guide](source/contribution/contribution.md)

---

**Last Updated:** 2026-01-26
**Documentation Version:** 0.2.0-dev

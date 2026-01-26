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

## 🏗️ Architecture Documentation

Understanding Ryoma AI's internal structure:

### Current Architecture (v0.2.0+)

- **[Architecture Comparison](ARCHITECTURE_COMPARISON.md)** - Visual comparison of old vs new architecture
- **[Refactoring Summary](REFACTORING_SUMMARY.md)** - Quick reference of architectural changes
- **[Store Architecture](source/architecture/store-architecture.md)** - InjectedStore pattern explained

### Legacy Architecture (v0.1.x)

- **[Architecture Overview](source/architecture/architecture.md)** - Original architecture (deprecated)
- **[SQL Agent Design](source/architecture/enhanced-sql-agent.md)** - Legacy SQL agent design
- **[Quick Reference](source/architecture/sql-agent-quick-reference.md)** - Legacy API reference
- **[Database Profiling](source/architecture/database-profiling.md)** - Performance profiling features

---

## 🔄 Refactoring & Migration

For developers working with or migrating code:

### Refactoring Plans

Located in **[docs/plans/](plans/)**:

1. **[DIRECT_REFACTORING_PLAN.md](plans/DIRECT_REFACTORING_PLAN.md)** - Current refactoring plan (active)
   - 8 steps to clean architecture
   - Breaking changes accepted
   - Estimated 15 hours total

2. **[MIGRATION_PLAN.md](plans/MIGRATION_PLAN.md)** - Original backward-compatible plan (archived)
   - 4 phases, 69 hours
   - Kept for reference only

3. **[REFACTORING_PROGRESS.md](plans/REFACTORING_PROGRESS.md)** - Live progress tracker
   - Current status: 63% complete (5 of 8 steps)
   - Detailed completion notes
   - Next steps and statistics

4. **[PHASE_1_COMPLETE.md](plans/PHASE_1_COMPLETE.md)** - Phase 1 completion summary
   - Foundation layer (domain, infrastructure, services)
   - 13 files created

### Migration Guides

**Coming soon:** Comprehensive migration guide from v0.1.x to v0.2.0

Key breaking changes:
- BaseAgent simplified (removed infrastructure methods)
- Agent instantiation changed (use AgentBuilder)
- Datasource management moved to DataSourceService
- Catalog operations moved to CatalogService

---

## 🛠️ Development

For contributors and maintainers:

- **[Contribution Guide](source/contribution/contribution.md)** - How to contribute
- **[Testing Guide](#testing-guide)** - Running and writing tests (see below)

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

1. **How do I create an agent?** → [API Reference](#api-reference)
2. **What changed in v0.2.0?** → [Architecture Comparison](ARCHITECTURE_COMPARISON.md)
3. **How do I migrate from v0.1.x?** → [Migration Guides](#migration-guides)
4. **Where is the refactoring progress?** → [Refactoring Progress](plans/REFACTORING_PROGRESS.md)
5. **How do I run tests?** → [Testing Guide](#testing-guide)
6. **How do I contribute?** → [Contribution Guide](source/contribution/contribution.md)

---

## 📮 Support & Feedback

- **Issues:** Report issues on the project GitHub repository
- **Questions:** Ask in project discussions or Slack channel
- **Contributions:** See [Contribution Guide](source/contribution/contribution.md)

---

**Last Updated:** 2026-01-26
**Documentation Version:** 0.2.0-dev

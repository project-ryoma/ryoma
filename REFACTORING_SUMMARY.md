# Ryoma AI Refactoring - Quick Reference

## 🎯 Goal
Remove datasource/indexer responsibilities from agents → Create clean service layer

## 📊 Current vs Future State

### Current (BaseAgent - 359 lines)
```python
class BaseAgent:
    def __init__(self, datasource, embedding, vector_store, store):
        self.resource_registry = ResourceRegistry()
        self.store = store
        self.embedding = self.init_embedding(embedding)
        self.vector_store = self.init_vector_store(...)
        self._catalog_index_service = UnifiedCatalogIndexService(...)
        # ... 8+ responsibilities!

    # Infrastructure methods (WRONG!)
    def add_datasource(self, datasource): ...
    def index_datasource(self, datasource): ...
    def search_catalogs(self, query): ...
```

### Future (BaseAgent - ~50 lines)
```python
class BaseAgent:
    def __init__(self, model, tools, system_prompt):
        self.model = model
        self.tools = tools
        self.system_prompt = system_prompt
        # That's it! Clean and focused

    # Agent methods (CORRECT!)
    def stream(self, user_input): ...
    def invoke(self, user_input): ...
```

## 📅 4-Phase Migration Plan (4-6 weeks)

### Phase 1: Foundation (Week 1-2) ✅ LOW RISK
**Add new code, don't touch existing**

```
New Structure:
├── domain/
│   ├── interfaces.py      # Protocols: DataSourceRepository, CatalogIndexer
│   └── constants.py       # StoreKeys, no more magic strings
├── infrastructure/
│   ├── datasource_repository.py  # Store-based repository
│   └── catalog_adapter.py        # Wraps existing services
└── services/
    ├── datasource_service.py     # DataSource management
    └── catalog_service.py        # Catalog operations
```

**Deliverables:**
- ✅ 7 new files
- ✅ Zero existing files modified
- ✅ All tests passing
- ✅ 100% backward compatible

---

### Phase 2: Backward Compatible Refactoring (Week 3-4) ⚠️ MEDIUM RISK
**Update existing code to use services internally, keep old APIs**

**Changes:**
1. **BaseAgent** - Add deprecation warnings, use services internally
2. **SQL Tools** - Use constants instead of magic strings
3. **SQL Agents** - Extract tool definitions (no duplication)
4. **CLI** - Use services alongside old managers

**Example:**
```python
# agent/base.py - UPDATED
class BaseAgent:
    def __init__(self, ..., datasource_service=None, catalog_service=None):
        # Create services if not provided
        self._datasource_service = datasource_service or DataSourceService(...)
        self._catalog_service = catalog_service or CatalogService(...)

    def add_datasource(self, datasource):
        warnings.warn("Deprecated! Use DataSourceService", DeprecationWarning)
        self._datasource_service.add_datasource(datasource)  # Delegate!
```

**Deliverables:**
- ✅ 4 key files modified
- ✅ All old code still works
- ✅ Deprecation warnings added
- ✅ Can rollback if needed

---

### Phase 3: Agent Simplification (Week 5) ✅ LOW RISK
**Create new v2 agents alongside old ones**

**New Files:**
1. **base_v2.py** - Clean agent (50 lines)
2. **agent_builder.py** - Service to build agents

**Usage:**
```python
# Old way (still works)
agent = SqlAgent(model="gpt-4", datasource=ds, vector_store=vs, ...)

# New way (opt-in with --v2 flag)
agent = agent_builder.build_sql_agent(model="gpt-4", mode="enhanced")
```

**Deliverables:**
- ✅ New clean API available
- ✅ Old API unchanged
- ✅ CLI flag: `--v2` to opt-in
- ✅ Side-by-side comparison

---

### Phase 4: Cleanup (Week 6) 🔴 HIGH RISK
**Remove deprecated code - BREAKING CHANGES**

**Actions:**
1. Version bump: 0.1.5 → 0.2.0
2. Remove all deprecated methods
3. Rename base_v2.py → base.py
4. Update all imports
5. Release migration guide

**Deliverables:**
- 🚨 Breaking changes for unmigrated users
- ✅ Clean architecture
- ✅ ~300 lines of code removed
- ✅ Complete migration guide

---

## 📁 New Architecture Overview

```
User/CLI
   ↓
Services Layer (NEW)
   ├── DataSourceService    → Manages datasources
   ├── CatalogService       → Handles indexing/search
   └── AgentBuilder         → Wires agents with tools
   ↓
Domain Layer (Agents)
   └── BaseAgent            → ONLY chat + tool execution
   ↓
Infrastructure Layer (NEW)
   ├── DataSourceRepository → Persistence
   └── CatalogAdapter       → Wraps existing catalog code
```

## 🔑 Key Changes

### 1. Magic Strings → Constants
```python
# Before
self.store.mset([("datasource_main", datasource)])
results = store.mget(["datasource_main"])

# After
from ryoma_ai.domain.constants import StoreKeys
self.store.mset([(StoreKeys.ACTIVE_DATASOURCE, datasource)])
results = store.mget([StoreKeys.ACTIVE_DATASOURCE])
```

### 2. Tool Duplication → Centralized
```python
# Before: Defined 3 times!
# BasicSqlAgent
tools = [SqlQueryTool(), CreateTableTool(), ...]
# EnhancedSqlAgent
tools = [SqlQueryTool(), CreateTableTool(), ...]
# ReFoRCESqlAgent
tools = [SqlQueryTool(), CreateTableTool(), ...]

# After: Defined once
from ryoma_ai.agent.sql_tools import get_basic_sql_tools
tools = get_basic_sql_tools()
```

### 3. BaseAgent Responsibilities
```python
# Before: 8+ responsibilities
- Chat with user ✅
- Manage datasources ❌
- Index catalogs ❌
- Search catalogs ❌
- Manage resources ❌
- Initialize embeddings ❌
- Initialize vector stores ❌
- Validate indexing ❌

# After: 1 responsibility
- Chat with user ✅
```

### 4. Agent Creation
```python
# Before: Complex initialization
agent = SqlAgent(
    model="gpt-4",
    datasource=DataSource(...),
    embedding={"model": "openai"},
    vector_store={"type": "qdrant", ...},
    store=meta_store,
    mode="enhanced"
)

# After: Simple and clean
agent = agent_builder.build_sql_agent(
    model="gpt-4",
    mode="enhanced"
)
# Services handle all the wiring!
```

## ⚠️ Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Break existing users | Phases 1-3 are backward compatible |
| Hard to rollback | Each phase is independently reversible |
| Incomplete migration | Deprecation warnings guide users |
| Performance regression | Add benchmarks in Phase 3 |
| Community resistance | Beta release (0.2.0-beta) before stable |

## ✅ Testing Strategy

```bash
# Phase 1: Test new services
pytest tests/unit/services/ -v

# Phase 2: Test backward compatibility
pytest tests/ -v -W error::DeprecationWarning

# Phase 3: Test both v1 and v2
pytest tests/integration/ -v

# Phase 4: Full suite
pytest tests/ -v --cov=ryoma_ai --cov-report=html
```

## 📈 Success Metrics

### Code Quality
- ✅ BaseAgent: 359 lines → 50 lines (86% reduction)
- ✅ Coupling: HIGH → LOW
- ✅ Testability: HARD → EASY
- ✅ Test coverage: 50% → 80%

### Architecture
- ✅ Clear layer boundaries
- ✅ Dependency inversion
- ✅ Single responsibility
- ✅ Open/closed principle

### Developer Experience
- ✅ Easier to understand
- ✅ Faster to test
- ✅ Simpler to extend
- ✅ Better error messages

## 🚀 Getting Started

### Step 1: Review Plan
Read `MIGRATION_PLAN.md` for detailed steps

### Step 2: Create Branch
```bash
git checkout -b refactor/service-layer
```

### Step 3: Start Phase 1
```bash
# Create domain layer
mkdir -p packages/ryoma_ai/ryoma_ai/domain
touch packages/ryoma_ai/ryoma_ai/domain/__init__.py
touch packages/ryoma_ai/ryoma_ai/domain/interfaces.py
touch packages/ryoma_ai/ryoma_ai/domain/constants.py
```

### Step 4: Follow TDD
1. Write tests first
2. Implement to make tests pass
3. Refactor
4. Repeat

## 📚 Resources

- **Full Plan**: `MIGRATION_PLAN.md` (detailed step-by-step)
- **This Summary**: `REFACTORING_SUMMARY.md` (quick reference)
- **Migration Guide**: Will be created in Phase 4 for end users

## 🎯 Timeline

- **Part-time (10 hrs/week)**: 6-7 weeks
- **Full-time (40 hrs/week)**: 2 weeks
- **Total effort**: ~69 hours

## 💡 Key Principles

1. **Incremental** - Small, safe steps
2. **Backward Compatible** - Until Phase 4
3. **Testable** - Tests at every step
4. **Reversible** - Can rollback phases 1-3
5. **Professional** - Following industry best practices

---

**Ready to start? Begin with Phase 1 in `MIGRATION_PLAN.md`**

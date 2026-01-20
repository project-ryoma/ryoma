# Direct Refactoring Plan - Breaking Changes OK

**Date:** 2026-01-19
**Status:** 🚀 READY TO EXECUTE
**Backward Compatibility:** ❌ NOT REQUIRED

---

## Overview

Since backward compatibility is not required, we can skip the gradual migration and **implement the clean architecture directly**. This will be much faster!

**Original Timeline:** 4-6 weeks (with backward compat)
**New Timeline:** 2-3 days (direct implementation)

---

## Phase 2 (Direct): Clean Implementation

### Step 2.1: Simplify BaseAgent (2 hours)

**Goal:** Remove all infrastructure responsibilities from BaseAgent

**Actions:**
1. Remove datasource management methods
2. Remove catalog indexing methods
3. Remove embedding/vector store initialization
4. Remove resource registry
5. Keep ONLY chat/invoke methods

**Files to Modify:**
- `packages/ryoma_ai/ryoma_ai/agent/base.py`

**Before (359 lines):**
```python
class BaseAgent:
    def __init__(self, datasource, embedding, vector_store, store, **kwargs):
        self.resource_registry = ResourceRegistry()
        self.store = store
        self.embedding = self.init_embedding(embedding)
        self.vector_store = self.init_vector_store(...)
        self._catalog_index_service = UnifiedCatalogIndexService(...)
        # ... 300+ more lines

    def add_datasource(self, datasource): ...
    def index_datasource(self, datasource): ...
    def search_catalogs(self, query): ...
    # ... 20+ methods
```

**After (~80 lines):**
```python
class BaseAgent:
    def __init__(
        self,
        model: BaseChatModel,
        tools: Optional[List[BaseTool]] = None,
        system_prompt: Optional[str] = None,
        store: Optional[BaseStore] = None,  # For InjectedStore pattern
    ):
        self.model = model
        self.tools = tools or []
        self.system_prompt = system_prompt
        self.store = store  # Only for LangGraph tool injection

    def stream(self, user_input: str): ...
    def invoke(self, user_input: str): ...
    def ainvoke(self, user_input: str): ...
    # That's it!
```

---

### Step 2.2: Extract SQL Tool Definitions (1 hour)

**Goal:** Eliminate duplication in SQL agent tool creation

**Actions:**
1. Create `agent/sql_tools.py` with centralized tool definitions
2. Update `agent/sql.py` to use shared definitions

**New File:** `packages/ryoma_ai/ryoma_ai/agent/sql_tools.py`
```python
"""Centralized SQL tool definitions"""

def get_basic_sql_tools() -> List[BaseTool]:
    return [
        SqlQueryTool(),
        CreateTableTool(),
        QueryProfileTool(),
    ]

def get_enhanced_sql_tools() -> List[BaseTool]:
    return get_basic_sql_tools() + [
        QueryExplanationTool(),
        QueryOptimizationTool(),
        SchemaAnalysisTool(),
    ]
```

---

### Step 2.3: Update Tools to Use Constants (1 hour)

**Goal:** Replace all magic strings with constants

**Files to Modify:**
- `packages/ryoma_ai/ryoma_ai/tool/sql_tool.py`
- `packages/ryoma_ai/ryoma_ai/tool/python_tool.py`
- `packages/ryoma_ai/ryoma_ai/tool/pandas_tool.py`
- `packages/ryoma_ai/ryoma_ai/tool/spark_tool.py`

**Before:**
```python
def get_datasource_from_store(store) -> SqlDataSource:
    results = store.mget(["datasource_main"])  # ❌ Magic string
    # ...
```

**After:**
```python
from ryoma_ai.domain.constants import StoreKeys

def get_datasource_from_store(store) -> SqlDataSource:
    results = store.mget([StoreKeys.ACTIVE_DATASOURCE])  # ✅ Constant
    # ...
```

---

### Step 2.4: Create AgentBuilder Service (3 hours)

**Goal:** Create a builder that constructs agents with all dependencies

**New File:** `packages/ryoma_ai/ryoma_ai/services/agent_builder.py`

```python
class AgentBuilder:
    """Builds fully-configured agents"""

    def __init__(
        self,
        datasource_service: DataSourceService,
        catalog_service: Optional[CatalogService] = None,
    ):
        self._datasource_service = datasource_service
        self._catalog_service = catalog_service

    def build_sql_agent(
        self,
        model: str = "gpt-3.5-turbo",
        mode: Literal["basic", "enhanced", "reforce"] = "basic",
    ) -> WorkflowAgent:
        """Build SQL agent with all tools configured"""
        # Get datasource from service
        datasource = self._datasource_service.get_active_datasource()

        # Create tools based on mode
        if mode == "basic":
            tools = get_basic_sql_tools()
        elif mode == "enhanced":
            tools = get_enhanced_sql_tools()
        else:
            tools = get_reforce_sql_tools()

        # Create LLM
        llm = load_model_provider(model)

        # Create clean agent - just model + tools!
        agent = WorkflowAgent(
            model=llm,
            tools=tools,
            system_prompt=self._get_sql_prompt(mode),
            store=InMemoryStore()  # For tool injection
        )

        # Add datasource to store for tools
        agent.store.mset([(StoreKeys.ACTIVE_DATASOURCE, datasource)])

        return agent
```

**Usage:**
```python
# Old way (complex, coupled)
agent = SqlAgent(
    model="gpt-4",
    datasource=DataSource(...),
    embedding={"model": "openai"},
    vector_store={"type": "qdrant", ...},
    store=InMemoryStore(),
    mode="enhanced"
)

# New way (simple, clean)
agent = agent_builder.build_sql_agent(model="gpt-4", mode="enhanced")
```

---

### Step 2.5: Refactor CLI to Use Services (3 hours)

**Goal:** Update CLI to use service layer

**File to Modify:** `packages/ryoma_ai/ryoma_ai/cli/app.py`

**Key Changes:**
```python
class RyomaAI:
    def __init__(self):
        # Initialize infrastructure
        self.store = self._setup_store()
        self.vector_store = self._setup_vector_store()
        self.embedding = self._setup_embedding()

        # Create services
        self.datasource_service = DataSourceService(
            StoreBasedDataSourceRepository(self.store)
        )

        self.catalog_service = CatalogService(
            CatalogIndexerAdapter(UnifiedCatalogIndexService(...)),
            CatalogSearcherAdapter(CatalogStore(...))
        )

        # Create agent builder
        self.agent_builder = AgentBuilder(
            datasource_service=self.datasource_service,
            catalog_service=self.catalog_service
        )

    def handle_datasource_add(self, config):
        """Add datasource using service"""
        datasource = self._create_datasource(config)
        self.datasource_service.add_datasource(datasource)
        self.console.print(f"[green]Added datasource: {datasource.id}[/green]")

    def handle_index_catalog(self):
        """Index catalog using service"""
        datasource = self.datasource_service.get_active_datasource()
        catalog_id = self.catalog_service.index_datasource(datasource)
        self.console.print(f"[green]Indexed: {catalog_id}[/green]")

    def create_agent(self, agent_type: str):
        """Create agent using builder"""
        if agent_type == "sql":
            return self.agent_builder.build_sql_agent()
        elif agent_type == "python":
            return self.agent_builder.build_python_agent()
        # ...
```

---

### Step 2.6: Update Agent Subclasses (2 hours)

**Goal:** Update all agent subclasses to work with new BaseAgent

**Files to Modify:**
- `packages/ryoma_ai/ryoma_ai/agent/chat_agent.py`
- `packages/ryoma_ai/ryoma_ai/agent/workflow.py`
- `packages/ryoma_ai/ryoma_ai/agent/sql.py`
- `packages/ryoma_ai/ryoma_ai/agent/python_agent.py`
- `packages/ryoma_ai/ryoma_ai/agent/pandas_agent.py`

**Example - ChatAgent:**
```python
class ChatAgent(BaseAgent):
    def __init__(
        self,
        model: Union[str, BaseChatModel],
        tools: Optional[List[BaseTool]] = None,
        system_prompt: Optional[str] = None,
        store: Optional[BaseStore] = None,
        **kwargs
    ):
        # Load model if string
        if isinstance(model, str):
            model = load_model_provider(model, **kwargs)

        # Call simple base constructor
        super().__init__(
            model=model,
            tools=tools,
            system_prompt=system_prompt,
            store=store
        )

        # Build chat chain
        self._chain = self._build_chain()
```

---

### Step 2.7: Update Tests (2 hours)

**Goal:** Update existing tests to work with new architecture

**Actions:**
1. Update agent tests to not expect datasource/catalog methods
2. Add tests for AgentBuilder
3. Ensure all existing tests pass

---

### Step 2.8: Update Documentation (1 hour)

**Goal:** Update README and examples

**Files to Update:**
- `README.md`
- Example scripts
- API documentation

---

## Summary: Direct Refactoring Timeline

| Step | Duration | Cumulative |
|------|----------|------------|
| 2.1: Simplify BaseAgent | 2 hours | 2 hours |
| 2.2: Extract SQL Tools | 1 hour | 3 hours |
| 2.3: Update Tools (Constants) | 1 hour | 4 hours |
| 2.4: Create AgentBuilder | 3 hours | 7 hours |
| 2.5: Refactor CLI | 3 hours | 10 hours |
| 2.6: Update Agent Subclasses | 2 hours | 12 hours |
| 2.7: Update Tests | 2 hours | 14 hours |
| 2.8: Update Documentation | 1 hour | 15 hours |

**Total Time:** ~15 hours (2 days full-time, 3 days part-time)

---

## Breaking Changes

### For End Users

**Old API:**
```python
from ryoma_ai.agent.sql import SqlAgent

agent = SqlAgent(
    model="gpt-4",
    datasource=my_datasource,
    embedding={"model": "openai"},
    vector_store={"type": "qdrant"},
)

agent.add_datasource(datasource)
agent.index_datasource(datasource, "ds-1")
```

**New API:**
```python
from ryoma_ai.services import DataSourceService, AgentBuilder
from ryoma_ai.infrastructure import StoreBasedDataSourceRepository

# Setup services
repo = StoreBasedDataSourceRepository(store)
datasource_service = DataSourceService(repo)
datasource_service.add_datasource(my_datasource)

# Build agent
builder = AgentBuilder(datasource_service)
agent = builder.build_sql_agent(model="gpt-4")

# Agent is clean - just chat!
agent.stream("What are top customers?")
```

### For Developers

**Breaking Changes:**
1. ❌ `BaseAgent.add_datasource()` removed → Use `DataSourceService.add_datasource()`
2. ❌ `BaseAgent.index_datasource()` removed → Use `CatalogService.index_datasource()`
3. ❌ `BaseAgent.search_catalogs()` removed → Use `CatalogService.search_tables()`
4. ❌ `BaseAgent.__init__` signature changed → Simplified parameters
5. ❌ `SqlAgent.__init__` signature changed → Use `AgentBuilder` instead

**Migration Guide:** Will be provided in documentation

---

## Benefits of Direct Approach

### Advantages ✅
- **Much Faster:** 15 hours vs 69 hours
- **Cleaner Result:** No deprecated code
- **Simpler Codebase:** No dual APIs
- **Easier to Maintain:** Single approach
- **Better for Team:** Clear direction

### Disadvantages ⚠️
- **Breaking Changes:** Users must update code
- **Higher Initial Impact:** All changes at once
- **Requires Migration Guide:** Must document clearly

---

## Risk Mitigation

Even though we're breaking compatibility, we can mitigate risks:

1. **Version Bump:** Release as v0.2.0 (breaking change)
2. **Clear Migration Guide:** Document all breaking changes
3. **Example Scripts:** Provide before/after examples
4. **Comprehensive Tests:** Ensure new code works
5. **Beta Release:** Release v0.2.0-beta first

---

## Next Steps

Ready to start? Here's the order:

1. ✅ **Step 2.1:** Simplify BaseAgent (most important)
2. ✅ **Step 2.2:** Extract SQL tools
3. ✅ **Step 2.3:** Update tools to use constants
4. ✅ **Step 2.4:** Create AgentBuilder
5. ✅ **Step 2.5:** Refactor CLI
6. ✅ **Step 2.6:** Update agent subclasses
7. ✅ **Step 2.7:** Update tests
8. ✅ **Step 2.8:** Update documentation

**Start now?** Let me know and I'll begin with Step 2.1: Simplify BaseAgent! 🚀

---

**Ready for rapid refactoring!**

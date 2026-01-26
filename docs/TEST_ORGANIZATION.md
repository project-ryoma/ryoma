# Test Organization & Optimization Plan

**Purpose:** Reorganize and optimize the Ryoma AI test suite for better maintainability, faster execution, and clearer test categories.

**Status:** Planning Phase
**Date:** 2026-01-26

---

## 🎯 Goals

1. **Clear Organization:** Tests organized by type (unit, integration, e2e)
2. **Fast Execution:** Unit tests run in < 1 second, full suite in < 30 seconds
3. **High Coverage:** Maintain > 80% code coverage
4. **Easy Maintenance:** Tests are easy to find, update, and extend
5. **CI/CD Ready:** Tests run reliably in CI pipelines

---

## 📂 Current Test Structure (Issues)

### Problems Identified

1. **Scattered Tests:** Tests in 3 different locations
   - `/home/user/ryoma/tests/` (root-level)
   - `/home/user/ryoma/packages/ryoma_ai/tests/` (package-level)
   - Mixed organization within these directories

2. **Inconsistent Naming:**
   - Some use `test_*.py` prefix
   - Some use `*_test.py` suffix
   - Mixed snake_case and descriptions

3. **Missing Test Categories:**
   - No clear separation of unit vs integration vs e2e
   - Some "unit" tests actually do integration
   - Some e2e tests in unit directories

4. **Outdated Tests:**
   - Many tests expect old v0.1.x API
   - Tests use deprecated BaseAgent methods
   - No tests for new service layer

5. **Slow Tests:**
   - Some tests make real API calls
   - Database setup in every test
   - No mocking/fixtures for expensive operations

---

## 🏗️ Proposed New Structure

### Directory Layout

```
tests/
├── conftest.py                      # Shared fixtures (pytest)
├── unit/                            # Fast, isolated unit tests
│   ├── __init__.py
│   ├── domain/                      # Domain layer tests
│   │   ├── __init__.py
│   │   └── test_constants.py
│   ├── infrastructure/              # Infrastructure layer tests
│   │   ├── __init__.py
│   │   ├── test_datasource_repository.py
│   │   └── test_catalog_adapter.py
│   ├── services/                    # Service layer tests
│   │   ├── __init__.py
│   │   ├── test_datasource_service.py
│   │   ├── test_catalog_service.py
│   │   └── test_agent_builder.py
│   ├── agent/                       # Agent unit tests (mocked)
│   │   ├── __init__.py
│   │   ├── test_base_agent.py
│   │   ├── test_chat_agent.py
│   │   ├── test_workflow_agent.py
│   │   └── test_sql_agent.py
│   ├── tool/                        # Tool tests (mocked)
│   │   ├── __init__.py
│   │   ├── test_sql_tool.py
│   │   └── test_python_tool.py
│   └── llm/                         # LLM provider tests (mocked)
│       ├── __init__.py
│       └── test_model_provider.py
├── integration/                     # Integration tests (real dependencies)
│   ├── __init__.py
│   ├── test_datasource_integration.py
│   ├── test_catalog_integration.py
│   └── test_agent_workflow.py
├── e2e/                             # End-to-end tests
│   ├── __init__.py
│   ├── test_sql_agent_e2e.py
│   ├── test_chat_agent_e2e.py
│   └── test_cli_e2e.py
└── fixtures/                        # Test data and fixtures
    ├── __init__.py
    ├── sample_databases.py
    ├── mock_responses.py
    └── test_data/
        ├── sample.db
        └── sample.csv
```

### Test Categories

| Category | Purpose | Speed | Dependencies | Coverage Target |
|----------|---------|-------|--------------|-----------------|
| **Unit** | Test individual components in isolation | < 0.1s per test | Mocked | 90%+ |
| **Integration** | Test component interactions | < 1s per test | Real (local) | 70%+ |
| **E2E** | Test full user workflows | < 5s per test | Real (may need API keys) | 50%+ |

---

## 🔧 Migration Plan

### Phase 1: Create New Structure ✅

1. Create new directory structure
2. Set up conftest.py with shared fixtures
3. Create fixture files for common test data

### Phase 2: Migrate Unit Tests

**Priority Tests to Migrate:**

1. **Domain Layer** (NEW - needs tests)
   - `test_constants.py` - Test StoreKeys and AgentDefaults
   - Status: **Need to create**

2. **Infrastructure Layer** (EXISTING - need updates)
   - `test_datasource_repository.py` - Already exists in `packages/ryoma_ai/tests/unit/services/`
   - `test_catalog_adapter.py` - Status: **Need to create**
   - Action: **Move + Update**

3. **Services Layer** (EXISTING - need updates)
   - `test_datasource_service.py` - Already exists, works ✅
   - `test_catalog_service.py` - Already exists, works ✅
   - `test_agent_builder.py` - Status: **Need to create**
   - Action: **Move + Add missing tests**

4. **Agent Layer** (EXISTING - needs major updates)
   - `test_base_agent.py` - Update for new v0.2.0 API
   - `test_chat_agent.py` - Update for new v0.2.0 API
   - `test_workflow_agent.py` - Update for new v0.2.0 API
   - `test_sql_agent.py` - Update for new v0.2.0 API
   - Action: **Update + Mock LLMs**

5. **Tool Layer** (EXISTING)
   - `test_sql_tool.py` - Update to use StoreKeys constants
   - `test_python_tool.py` - Update if needed
   - Action: **Update**

6. **LLM Layer** (EXISTING)
   - `test_model_provider.py` - Already exists
   - Action: **Move + Update**

### Phase 3: Migrate Integration Tests

**Existing Integration Tests:**
- `tests/unit_tests/test_datasource.py` → `tests/integration/test_datasource_integration.py`
- `tests/unit_tests/test_injected_datasource.py` → `tests/integration/test_injected_store.py`
- `packages/ryoma_ai/tests/agent/test_workflow_error_handling.py` → `tests/integration/test_workflow_error_handling.py`

**Action:** Move and rename to integration/

### Phase 4: Migrate E2E Tests

**Existing E2E Tests:**
- `tests/e2e/ryoma_ai/test_agent.py` → Keep, update for v0.2.0
- `tests/e2e/ryoma_ai/test_datasource.py` → Keep, update for v0.2.0
- `tests/e2e/ryoma_ai/test_llm.py` → Keep, update for v0.2.0
- `packages/ryoma_ai/tests/agent/test_sql_agent_gemini.py` → Move to e2e/
- `packages/ryoma_ai/tests/agent/test_sql_approval_*.py` → Move to e2e/

**Action:** Move, consolidate, and update

### Phase 5: Add Missing Tests

**Critical Missing Tests:**

1. **AgentBuilder Tests** (HIGH PRIORITY)
   ```python
   # tests/unit/services/test_agent_builder.py
   def test_build_sql_agent_basic_mode()
   def test_build_sql_agent_enhanced_mode()
   def test_build_sql_agent_reforce_mode()
   def test_build_sql_agent_no_datasource_raises()
   def test_build_python_agent()
   def test_build_chat_agent()
   ```

2. **Updated Agent Tests** (HIGH PRIORITY)
   ```python
   # tests/unit/agent/test_sql_agent.py
   def test_basic_sql_agent_instantiation()
   def test_enhanced_sql_agent_instantiation()
   def test_reforce_sql_agent_instantiation()
   def test_sql_agent_factory_basic()
   def test_sql_agent_factory_enhanced()
   def test_sql_agent_factory_reforce()
   ```

3. **Store Architecture Tests** (MEDIUM PRIORITY)
   ```python
   # tests/unit/infrastructure/test_injected_store.py
   def test_store_provides_datasource_to_tools()
   def test_store_key_constants_used()
   ```

4. **Domain Tests** (MEDIUM PRIORITY)
   ```python
   # tests/unit/domain/test_constants.py
   def test_store_keys_values()
   def test_agent_defaults_values()
   ```

### Phase 6: Optimize Test Execution

**Optimization Strategies:**

1. **Use Mocking Extensively:**
   ```python
   # Mock LLM calls
   @patch('ryoma_ai.llm.provider.load_model_provider')
   def test_agent_creation(mock_provider):
       mock_provider.return_value = MockLLM()
       agent = SqlAgent(model="gpt-4")
       assert agent.model is not None
   ```

2. **Shared Fixtures:**
   ```python
   # tests/conftest.py
   @pytest.fixture
   def mock_datasource():
       return DataSource(name="test", type="sqlite", config={"database": ":memory:"})

   @pytest.fixture
   def mock_llm():
       return MockChatModel()

   @pytest.fixture
   def agent_builder(mock_datasource):
       store = InMemoryStore()
       repo = StoreBasedDataSourceRepository(store)
       ds_service = DataSourceService(repo)
       ds_service.add_datasource(mock_datasource)
       return AgentBuilder(ds_service)
   ```

3. **Parallel Test Execution:**
   ```bash
   # pytest.ini
   [pytest]
   addopts = -n auto  # Use all CPU cores
   testpaths = tests
   python_files = test_*.py
   python_classes = Test*
   python_functions = test_*
   ```

4. **Fast Fail Strategy:**
   ```bash
   # Run fast unit tests first, skip slow tests on failure
   pytest tests/unit/ -x  # Stop on first failure
   ```

---

## 📊 Test Metrics & Goals

### Current State (Estimated)

- **Total Tests:** ~30-40
- **Passing Tests:** ~60% (many broken by v0.2.0 changes)
- **Code Coverage:** Unknown (need to measure)
- **Execution Time:** Unknown (need to measure)
- **Organization:** Poor (3 different locations)

### Target State

| Metric | Target | Timeline |
|--------|--------|----------|
| **Total Tests** | 100+ | End of refactoring |
| **Passing Rate** | 100% | End of refactoring |
| **Code Coverage** | > 80% | End of refactoring |
| **Unit Test Speed** | < 10s | Immediate |
| **Full Suite Speed** | < 30s | Immediate |
| **Organization** | Single `/tests` directory | Immediate |

---

## 🚀 Implementation Steps

### Step 1: Setup (30 min)

```bash
# 1. Create new test structure
mkdir -p tests/{unit,integration,e2e,fixtures}/{domain,infrastructure,services,agent,tool,llm}

# 2. Create __init__.py files
find tests -type d -exec touch {}/__init__.py \;

# 3. Create conftest.py
touch tests/conftest.py

# 4. Create pytest.ini
touch pytest.ini
```

### Step 2: Create Shared Fixtures (1 hour)

File: `tests/conftest.py`

```python
import pytest
from unittest.mock import MagicMock
from langchain_core.stores import InMemoryStore
from ryoma_ai.datasource import DataSource
from ryoma_ai.services import DataSourceService, AgentBuilder
from ryoma_ai.infrastructure.datasource_repository import StoreBasedDataSourceRepository


@pytest.fixture
def memory_store():
    """In-memory store for testing."""
    return InMemoryStore()


@pytest.fixture
def mock_datasource():
    """Mock datasource for testing."""
    return DataSource(
        name="test_db",
        type="sqlite",
        config={"database": ":memory:"}
    )


@pytest.fixture
def datasource_repository(memory_store):
    """Repository with in-memory store."""
    return StoreBasedDataSourceRepository(memory_store)


@pytest.fixture
def datasource_service(datasource_repository, mock_datasource):
    """DataSourceService with a test datasource."""
    service = DataSourceService(datasource_repository)
    service.add_datasource(mock_datasource)
    return service


@pytest.fixture
def agent_builder(datasource_service):
    """AgentBuilder ready for testing."""
    return AgentBuilder(datasource_service=datasource_service)


@pytest.fixture
def mock_llm():
    """Mock language model for testing."""
    mock = MagicMock()
    mock.invoke.return_value = "Mocked response"
    return mock
```

### Step 3: Create Priority Tests (2 hours)

**Test 1:** AgentBuilder Tests
```python
# tests/unit/services/test_agent_builder.py
import pytest
from ryoma_ai.services import AgentBuilder
from ryoma_ai.agent.workflow import WorkflowAgent
from ryoma_ai.agent.chat_agent import ChatAgent


def test_build_sql_agent_basic(agent_builder):
    agent = agent_builder.build_sql_agent(model="gpt-3.5-turbo", mode="basic")
    assert isinstance(agent, WorkflowAgent)
    assert len(agent.tools) == 3  # Basic tools


def test_build_sql_agent_enhanced(agent_builder):
    agent = agent_builder.build_sql_agent(model="gpt-3.5-turbo", mode="enhanced")
    assert isinstance(agent, WorkflowAgent)
    assert len(agent.tools) == 5  # Enhanced tools


def test_build_sql_agent_reforce(agent_builder):
    agent = agent_builder.build_sql_agent(model="gpt-3.5-turbo", mode="reforce")
    assert isinstance(agent, WorkflowAgent)
    assert len(agent.tools) == 5  # ReFoRCE tools


def test_build_sql_agent_no_datasource_raises():
    # AgentBuilder without datasource should raise
    from ryoma_ai.services import DataSourceService
    from ryoma_ai.infrastructure.datasource_repository import StoreBasedDataSourceRepository
    from langchain_core.stores import InMemoryStore

    repo = StoreBasedDataSourceRepository(InMemoryStore())
    service = DataSourceService(repo)
    builder = AgentBuilder(datasource_service=service)

    with pytest.raises(ValueError, match="No active datasource"):
        builder.build_sql_agent(model="gpt-3.5-turbo")


def test_build_python_agent(agent_builder):
    agent = agent_builder.build_python_agent(model="gpt-3.5-turbo")
    assert isinstance(agent, WorkflowAgent)
    assert len(agent.tools) == 1  # PythonREPLTool


def test_build_chat_agent(agent_builder):
    agent = agent_builder.build_chat_agent(
        model="gpt-3.5-turbo",
        system_prompt="Test prompt"
    )
    assert isinstance(agent, ChatAgent)
    assert agent.system_prompt == "Test prompt"
```

### Step 4: Migrate Existing Tests (2 hours)

Move and update existing tests one category at a time.

### Step 5: Add Coverage Reporting (30 min)

```bash
# Install coverage
pip install pytest-cov

# Run with coverage
pytest --cov=ryoma_ai --cov-report=html --cov-report=term

# View report
open htmlcov/index.html
```

### Step 6: Configure CI/CD (1 hour)

Add to `.github/workflows/test.yml` (if using GitHub Actions):

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install -e packages/ryoma_ai
          pip install pytest pytest-cov pytest-xdist
      - name: Run unit tests
        run: pytest tests/unit/ -v
      - name: Run integration tests
        run: pytest tests/integration/ -v
      - name: Run coverage
        run: pytest --cov=ryoma_ai --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

---

## 📋 Checklist

### Phase 1: Setup
- [x] Document current test issues
- [x] Design new test structure
- [x] Create implementation plan
- [ ] Create new test directories
- [ ] Set up conftest.py with fixtures
- [ ] Configure pytest.ini

### Phase 2: Unit Tests
- [ ] Move service tests to new location
- [ ] Create AgentBuilder tests (HIGH PRIORITY)
- [ ] Update agent tests for v0.2.0 API
- [ ] Add domain layer tests
- [ ] Add infrastructure tests
- [ ] Mock all expensive operations

### Phase 3: Integration Tests
- [ ] Move existing integration tests
- [ ] Update for v0.2.0 API
- [ ] Add store integration tests

### Phase 4: E2E Tests
- [ ] Consolidate e2e tests in one location
- [ ] Update for v0.2.0 API
- [ ] Add CLI e2e tests

### Phase 5: Optimization
- [ ] Measure current test execution time
- [ ] Add parallel execution (-n auto)
- [ ] Optimize slow tests
- [ ] Achieve < 30s full suite execution

### Phase 6: CI/CD
- [ ] Set up GitHub Actions workflow
- [ ] Add coverage reporting
- [ ] Add test badges to README

---

## 🎯 Success Criteria

The test reorganization is complete when:

1. ✅ All tests pass (100% passing rate)
2. ✅ Tests organized in clear categories (unit/integration/e2e)
3. ✅ Code coverage > 80%
4. ✅ Unit tests run in < 10 seconds
5. ✅ Full suite runs in < 30 seconds
6. ✅ Tests run automatically in CI/CD
7. ✅ New v0.2.0 features have comprehensive tests

---

## 📝 Notes

- **Priority:** Start with AgentBuilder tests (most critical for v0.2.0)
- **Approach:** Incremental migration (don't break existing tests)
- **Mocking:** Mock all LLM calls to avoid API costs and latency
- **Documentation:** Update test docs as we go

**Next Steps:**
1. Create new test structure (Phase 1)
2. Write AgentBuilder tests (Phase 2, High Priority)
3. Migrate and update agent tests (Phase 2)
4. Set up coverage reporting (Phase 5)

---

**Status:** Planning Complete - Ready for Implementation
**Estimated Total Time:** 7-8 hours
**Last Updated:** 2026-01-26

# Ryoma AI Refactoring - Detailed Migration Plan

## 📋 Executive Summary

**Objective:** Refactor ryoma_ai to separate infrastructure concerns from domain logic, reducing coupling and improving maintainability.

**Key Goals:**
- ✅ Remove datasource/indexer responsibilities from agents
- ✅ Reduce BaseAgent from 359 lines to ~50 lines
- ✅ Introduce proper service layer for infrastructure
- ✅ Maintain backward compatibility during migration
- ✅ Zero breaking changes for existing users

**Timeline:** 4-6 weeks (part-time) or 2-3 weeks (full-time)

**Risk Level:** MEDIUM (using incremental approach with backward compatibility)

---

## 🎯 Migration Strategy

### Core Principles
1. **Incremental Changes** - Small, testable steps
2. **Backward Compatibility** - No breaking changes until final phase
3. **Deprecation Warnings** - Warn users before removing old APIs
4. **Parallel Implementation** - New code alongside old code
5. **Test Everything** - Comprehensive tests at each phase
6. **Can Rollback** - Each phase is independently reversible

### Migration Approach
```
Current State → Phase 1 → Phase 2 → Phase 3 → Phase 4 → Final State
     ↓           ↓         ↓         ↓         ↓         ↓
  Coupled → Add Services → Dual APIs → Agents Use → Deprecate → Clean
              (new)        (old+new)   Services    Old APIs    Architecture
```

---

## 📅 Phase 1: Foundation (Week 1-2)

**Goal:** Create new service layer and interfaces WITHOUT touching existing code

**Risk:** LOW (only adding new code)

### Step 1.1: Create Domain Interfaces (2 hours)

**New Files:**
```
packages/ryoma_ai/ryoma_ai/domain/
├── __init__.py
├── interfaces.py          # NEW - Protocol definitions
└── constants.py           # NEW - Centralized constants
```

**File: `domain/constants.py`**
```python
"""Centralized constants to eliminate magic strings"""

class StoreKeys:
    """Keys used in metadata store"""
    ACTIVE_DATASOURCE = "datasource_main"
    DATASOURCES_PREFIX = "datasources:"
    ACTIVE_DATASOURCE_ID = "active_datasource_id"

class AgentDefaults:
    """Default configurations for agents"""
    DEFAULT_MODEL = "gpt-3.5-turbo"
    DEFAULT_TEMPERATURE = 0.0
    MAX_ITERATIONS = 10
```

**File: `domain/interfaces.py`**
```python
"""Domain interfaces - protocols for dependency inversion"""

from typing import Protocol, List, Optional, Literal
from ryoma_data.base import DataSource
from ryoma_data.metadata import Catalog

class DataSourceRepository(Protocol):
    """Repository for managing datasources"""

    def save(self, datasource: DataSource) -> None:
        """Save a datasource"""
        ...

    def get_active(self) -> DataSource:
        """Get the currently active datasource"""
        ...

    def set_active(self, datasource_id: str) -> None:
        """Set which datasource is active"""
        ...

    def get_by_id(self, datasource_id: str) -> DataSource:
        """Get datasource by ID"""
        ...

    def list_all(self) -> List[DataSource]:
        """List all datasources"""
        ...

    def delete(self, datasource_id: str) -> None:
        """Delete a datasource"""
        ...


class CatalogIndexer(Protocol):
    """Protocol for catalog indexing operations"""

    def index_datasource(
        self,
        datasource: DataSource,
        data_source_id: str,
        level: Literal["catalog", "schema", "table", "column"] = "column"
    ) -> str:
        """Index a datasource's catalog"""
        ...

    def validate_indexing(
        self,
        catalog_id: str
    ) -> bool:
        """Validate that catalog is properly indexed"""
        ...


class CatalogSearcher(Protocol):
    """Protocol for catalog search operations"""

    def search_catalogs(
        self,
        query: str,
        top_k: int = 5,
        level: Literal["catalog", "schema", "table", "column"] = "column",
        datasource_id: Optional[str] = None
    ) -> List[dict]:
        """Search catalogs semantically"""
        ...

    def get_table_suggestions(
        self,
        query: str,
        top_k: int = 5
    ) -> List[str]:
        """Get table name suggestions"""
        ...

    def get_column_suggestions(
        self,
        table_name: str,
        query: str,
        top_k: int = 5
    ) -> List[str]:
        """Get column suggestions for a table"""
        ...
```

**Verification:**
```bash
# Run these commands to verify
python -c "from ryoma_ai.domain.interfaces import DataSourceRepository; print('✓ Interfaces OK')"
python -c "from ryoma_ai.domain.constants import StoreKeys; print('✓ Constants OK')"
```

---

### Step 1.2: Create Infrastructure Layer (4 hours)

**New Files:**
```
packages/ryoma_ai/ryoma_ai/infrastructure/
├── __init__.py
├── datasource_repository.py    # NEW - DataSource persistence
└── catalog_adapter.py           # NEW - Wraps existing catalog services
```

**File: `infrastructure/datasource_repository.py`**
```python
"""Repository implementation for datasource persistence"""

import logging
from typing import List, Optional
from langchain_core.stores import BaseStore
from ryoma_data.base import DataSource
from ryoma_ai.domain.constants import StoreKeys

logger = logging.getLogger(__name__)


class StoreBasedDataSourceRepository:
    """
    DataSource repository using LangChain BaseStore.
    Implements DataSourceRepository protocol.
    """

    def __init__(self, store: BaseStore):
        """
        Initialize repository.

        Args:
            store: LangChain BaseStore for persistence
        """
        self._store = store

    def save(self, datasource: DataSource) -> None:
        """Save a datasource to the store"""
        key = f"{StoreKeys.DATASOURCES_PREFIX}{datasource.id}"
        self._store.mset([(key, datasource)])
        logger.info(f"Saved datasource: {datasource.id}")

    def get_active(self) -> DataSource:
        """Get the currently active datasource"""
        # Try new key first (multi-datasource support)
        results = self._store.mget([StoreKeys.ACTIVE_DATASOURCE_ID])
        active_id = results[0] if results and results[0] else None

        if active_id:
            return self.get_by_id(active_id)

        # Fall back to old key for backward compatibility
        results = self._store.mget([StoreKeys.ACTIVE_DATASOURCE])
        datasource = results[0] if results and results[0] else None

        if not datasource:
            raise ValueError(
                "No active datasource configured. "
                "Use add_datasource() or set_active_datasource() first."
            )

        return datasource

    def set_active(self, datasource_id: str) -> None:
        """Set which datasource is active"""
        # Verify datasource exists
        datasource = self.get_by_id(datasource_id)

        # Set new key
        self._store.mset([
            (StoreKeys.ACTIVE_DATASOURCE_ID, datasource_id),
            (StoreKeys.ACTIVE_DATASOURCE, datasource),  # Backward compat
        ])
        logger.info(f"Set active datasource: {datasource_id}")

    def get_by_id(self, datasource_id: str) -> DataSource:
        """Get datasource by ID"""
        key = f"{StoreKeys.DATASOURCES_PREFIX}{datasource_id}"
        results = self._store.mget([key])
        datasource = results[0] if results and results[0] else None

        if not datasource:
            raise ValueError(f"Datasource not found: {datasource_id}")

        return datasource

    def list_all(self) -> List[DataSource]:
        """List all datasources"""
        # Note: This requires store.search() which may not be available
        # in all store implementations. For now, we'll track datasource IDs
        # in a separate key.
        results = self._store.mget(["datasource_ids"])
        datasource_ids = results[0] if results and results[0] else []

        datasources = []
        for ds_id in datasource_ids:
            try:
                datasources.append(self.get_by_id(ds_id))
            except ValueError:
                logger.warning(f"Datasource {ds_id} not found in store")

        return datasources

    def delete(self, datasource_id: str) -> None:
        """Delete a datasource"""
        # Verify exists
        self.get_by_id(datasource_id)

        # Delete from store
        key = f"{StoreKeys.DATASOURCES_PREFIX}{datasource_id}"
        # Note: BaseStore doesn't have delete, so we set to None
        # This is a limitation of the current store interface
        self._store.mset([(key, None)])

        # Remove from datasource_ids list
        results = self._store.mget(["datasource_ids"])
        datasource_ids = results[0] if results and results[0] else []
        if datasource_id in datasource_ids:
            datasource_ids.remove(datasource_id)
            self._store.mset([("datasource_ids", datasource_ids)])

        logger.info(f"Deleted datasource: {datasource_id}")
```

**File: `infrastructure/catalog_adapter.py`**
```python
"""Adapter for existing catalog indexing/search services"""

import logging
from typing import List, Optional, Literal
from ryoma_data.base import DataSource
from ryoma_ai.catalog.indexer import UnifiedCatalogIndexService
from ryoma_ai.store.catalog_store import CatalogStore

logger = logging.getLogger(__name__)


class CatalogIndexerAdapter:
    """
    Adapter that wraps UnifiedCatalogIndexService.
    Implements CatalogIndexer protocol.
    """

    def __init__(self, service: UnifiedCatalogIndexService):
        """
        Initialize adapter.

        Args:
            service: Existing UnifiedCatalogIndexService instance
        """
        self._service = service

    def index_datasource(
        self,
        datasource: DataSource,
        data_source_id: str,
        level: Literal["catalog", "schema", "table", "column"] = "column"
    ) -> str:
        """Index a datasource's catalog"""
        return self._service.index_datasource(
            datasource=datasource,
            data_source_id=data_source_id,
            level=level
        )

    def validate_indexing(self, catalog_id: str) -> bool:
        """Validate catalog is properly indexed"""
        try:
            # Try to get catalog metadata
            # This is a simple check - enhance as needed
            return catalog_id is not None and len(catalog_id) > 0
        except Exception as e:
            logger.warning(f"Catalog validation failed: {e}")
            return False


class CatalogSearcherAdapter:
    """
    Adapter that wraps CatalogStore.
    Implements CatalogSearcher protocol.
    """

    def __init__(self, catalog_store: CatalogStore):
        """
        Initialize adapter.

        Args:
            catalog_store: Existing CatalogStore instance
        """
        self._catalog_store = catalog_store

    def search_catalogs(
        self,
        query: str,
        top_k: int = 5,
        level: Literal["catalog", "schema", "table", "column"] = "column",
        datasource_id: Optional[str] = None
    ) -> List[dict]:
        """Search catalogs semantically"""
        return self._catalog_store.search_catalogs(
            query=query,
            top_k=top_k,
            level=level
        )

    def get_table_suggestions(
        self,
        query: str,
        top_k: int = 5
    ) -> List[str]:
        """Get table name suggestions"""
        return self._catalog_store.get_table_suggestions(
            query=query,
            top_k=top_k
        )

    def get_column_suggestions(
        self,
        table_name: str,
        query: str,
        top_k: int = 5
    ) -> List[str]:
        """Get column suggestions for a table"""
        return self._catalog_store.get_column_suggestions(
            table_name=table_name,
            query=query,
            top_k=top_k
        )
```

**Verification:**
```bash
# Test imports
python -c "from ryoma_ai.infrastructure.datasource_repository import StoreBasedDataSourceRepository; print('✓ Repository OK')"
python -c "from ryoma_ai.infrastructure.catalog_adapter import CatalogIndexerAdapter; print('✓ Adapter OK')"
```

---

### Step 1.3: Create Service Layer (6 hours)

**New Files:**
```
packages/ryoma_ai/ryoma_ai/services/
├── __init__.py
├── datasource_service.py      # NEW - DataSource management
├── catalog_service.py         # NEW - Catalog operations
└── agent_builder.py           # NEW - Agent construction
```

**File: `services/datasource_service.py`**
```python
"""Service for datasource management"""

import logging
from typing import List, Optional
from ryoma_data.base import DataSource
from ryoma_ai.domain.interfaces import DataSourceRepository

logger = logging.getLogger(__name__)


class DataSourceService:
    """
    Service for managing datasources.
    Encapsulates all datasource-related operations.
    """

    def __init__(self, repository: DataSourceRepository):
        """
        Initialize service.

        Args:
            repository: Repository for datasource persistence
        """
        self._repository = repository

    def add_datasource(self, datasource: DataSource) -> None:
        """
        Add a new datasource.

        Args:
            datasource: DataSource to add
        """
        self._repository.save(datasource)
        logger.info(f"Added datasource: {datasource.id}")

    def get_active_datasource(self) -> DataSource:
        """
        Get the currently active datasource.

        Returns:
            The active datasource

        Raises:
            ValueError: If no active datasource is configured
        """
        return self._repository.get_active()

    def set_active_datasource(self, datasource_id: str) -> None:
        """
        Set which datasource is active.

        Args:
            datasource_id: ID of datasource to make active

        Raises:
            ValueError: If datasource not found
        """
        self._repository.set_active(datasource_id)
        logger.info(f"Activated datasource: {datasource_id}")

    def get_datasource(self, datasource_id: str) -> DataSource:
        """
        Get a datasource by ID.

        Args:
            datasource_id: ID of datasource to retrieve

        Returns:
            The requested datasource

        Raises:
            ValueError: If datasource not found
        """
        return self._repository.get_by_id(datasource_id)

    def list_datasources(self) -> List[DataSource]:
        """
        List all registered datasources.

        Returns:
            List of all datasources
        """
        return self._repository.list_all()

    def remove_datasource(self, datasource_id: str) -> None:
        """
        Remove a datasource.

        Args:
            datasource_id: ID of datasource to remove

        Raises:
            ValueError: If datasource not found
        """
        self._repository.delete(datasource_id)
        logger.info(f"Removed datasource: {datasource_id}")
```

**File: `services/catalog_service.py`**
```python
"""Service for catalog indexing and search operations"""

import logging
from typing import List, Optional, Literal
from ryoma_data.base import DataSource
from ryoma_ai.domain.interfaces import CatalogIndexer, CatalogSearcher

logger = logging.getLogger(__name__)


class CatalogService:
    """
    Service for catalog indexing and search.
    Encapsulates all catalog-related operations.
    """

    def __init__(
        self,
        indexer: CatalogIndexer,
        searcher: CatalogSearcher,
    ):
        """
        Initialize service.

        Args:
            indexer: Catalog indexing implementation
            searcher: Catalog search implementation
        """
        self._indexer = indexer
        self._searcher = searcher

    # === Indexing Operations ===

    def index_datasource(
        self,
        datasource: DataSource,
        level: Literal["catalog", "schema", "table", "column"] = "column"
    ) -> str:
        """
        Index a datasource's catalog.

        Args:
            datasource: DataSource to index
            level: Level of indexing (catalog/schema/table/column)

        Returns:
            Catalog ID
        """
        catalog_id = self._indexer.index_datasource(
            datasource=datasource,
            data_source_id=datasource.id,
            level=level
        )
        logger.info(
            f"Indexed datasource {datasource.id} at level {level}: {catalog_id}"
        )
        return catalog_id

    def index_multiple_datasources(
        self,
        datasources: List[DataSource],
        level: Literal["catalog", "schema", "table", "column"] = "column"
    ) -> List[str]:
        """
        Index multiple datasources.

        Args:
            datasources: List of datasources to index
            level: Level of indexing

        Returns:
            List of catalog IDs
        """
        catalog_ids = []
        for datasource in datasources:
            try:
                catalog_id = self.index_datasource(datasource, level)
                catalog_ids.append(catalog_id)
            except Exception as e:
                logger.error(f"Failed to index {datasource.id}: {e}")

        logger.info(f"Indexed {len(catalog_ids)}/{len(datasources)} datasources")
        return catalog_ids

    def validate_indexing(self, catalog_id: str) -> bool:
        """
        Validate that a catalog is properly indexed.

        Args:
            catalog_id: Catalog ID to validate

        Returns:
            True if valid, False otherwise
        """
        return self._indexer.validate_indexing(catalog_id)

    # === Search Operations ===

    def search_tables(
        self,
        query: str,
        top_k: int = 5,
        datasource_id: Optional[str] = None
    ) -> List[dict]:
        """
        Search for relevant tables.

        Args:
            query: Search query
            top_k: Number of results to return
            datasource_id: Optional filter by datasource

        Returns:
            List of table metadata dicts
        """
        return self._searcher.search_catalogs(
            query=query,
            top_k=top_k,
            level="table",
            datasource_id=datasource_id
        )

    def search_columns(
        self,
        query: str,
        table_name: Optional[str] = None,
        top_k: int = 5
    ) -> List[dict]:
        """
        Search for relevant columns.

        Args:
            query: Search query
            table_name: Optional filter by table
            top_k: Number of results to return

        Returns:
            List of column metadata dicts
        """
        if table_name:
            return self._searcher.get_column_suggestions(
                table_name=table_name,
                query=query,
                top_k=top_k
            )
        else:
            return self._searcher.search_catalogs(
                query=query,
                top_k=top_k,
                level="column"
            )

    def get_table_suggestions(
        self,
        query: str,
        top_k: int = 5
    ) -> List[str]:
        """
        Get table name suggestions based on query.

        Args:
            query: Search query
            top_k: Number of suggestions

        Returns:
            List of table names
        """
        return self._searcher.get_table_suggestions(query, top_k)

    def get_column_suggestions(
        self,
        table_name: str,
        query: str,
        top_k: int = 5
    ) -> List[str]:
        """
        Get column suggestions for a table.

        Args:
            table_name: Table to search columns in
            query: Search query
            top_k: Number of suggestions

        Returns:
            List of column names
        """
        return self._searcher.get_column_suggestions(table_name, query, top_k)
```

**Verification:**
```bash
# Test service layer
python -c "from ryoma_ai.services.datasource_service import DataSourceService; print('✓ DataSourceService OK')"
python -c "from ryoma_ai.services.catalog_service import CatalogService; print('✓ CatalogService OK')"
```

---

### Step 1.4: Write Tests for New Code (4 hours)

**New Files:**
```
packages/ryoma_ai/tests/unit/services/
├── __init__.py
├── test_datasource_service.py
├── test_catalog_service.py
└── test_infrastructure.py
```

**File: `tests/unit/services/test_datasource_service.py`**
```python
"""Tests for DataSourceService"""

import pytest
from unittest.mock import Mock, MagicMock
from ryoma_ai.services.datasource_service import DataSourceService
from ryoma_data.sql import DataSource


@pytest.fixture
def mock_repository():
    """Mock datasource repository"""
    return Mock()


@pytest.fixture
def service(mock_repository):
    """DataSourceService instance"""
    return DataSourceService(mock_repository)


@pytest.fixture
def sample_datasource():
    """Sample datasource for testing"""
    return DataSource(
        backend="duckdb",
        database=":memory:",
        id="test_ds"
    )


def test_add_datasource(service, mock_repository, sample_datasource):
    """Test adding a datasource"""
    service.add_datasource(sample_datasource)

    mock_repository.save.assert_called_once_with(sample_datasource)


def test_get_active_datasource(service, mock_repository, sample_datasource):
    """Test getting active datasource"""
    mock_repository.get_active.return_value = sample_datasource

    result = service.get_active_datasource()

    assert result == sample_datasource
    mock_repository.get_active.assert_called_once()


def test_set_active_datasource(service, mock_repository):
    """Test setting active datasource"""
    service.set_active_datasource("test_ds")

    mock_repository.set_active.assert_called_once_with("test_ds")


def test_list_datasources(service, mock_repository, sample_datasource):
    """Test listing datasources"""
    mock_repository.list_all.return_value = [sample_datasource]

    result = service.list_datasources()

    assert len(result) == 1
    assert result[0] == sample_datasource


def test_remove_datasource(service, mock_repository):
    """Test removing a datasource"""
    service.remove_datasource("test_ds")

    mock_repository.delete.assert_called_once_with("test_ds")
```

**Run tests:**
```bash
cd packages/ryoma_ai
pytest tests/unit/services/test_datasource_service.py -v
```

---

### Phase 1 Deliverables

✅ **New Files Created:**
- 3 domain files (interfaces, constants)
- 2 infrastructure files (repository, adapter)
- 2 service files (datasource, catalog)
- 3 test files

✅ **No Existing Code Modified**

✅ **Backward Compatibility:** 100% (nothing broken)

✅ **Tests:** All new code is tested

---

## 📅 Phase 2: Backward Compatible Refactoring (Week 3-4)

**Goal:** Update existing code to USE new services while maintaining old APIs

**Risk:** MEDIUM (modifying existing code but maintaining compatibility)

### Step 2.1: Update BaseAgent to Support Both APIs (6 hours)

**Modified File: `agent/base.py`**

```python
# agent/base.py - UPDATED (backward compatible)
import logging
import warnings
from typing import Any, Dict, List, Literal, Optional, Union

from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import VectorStore
from ryoma_ai.agent.resource_registry import ResourceRegistry
from ryoma_ai.catalog.indexer import UnifiedCatalogIndexService
from ryoma_data.base import DataSource
from ryoma_data.metadata import Catalog
from ryoma_ai.embedding.client import get_embedding_client
from ryoma_ai.models.agent import AgentType
from ryoma_ai.store.catalog_store import CatalogNotIndexedError, CatalogStore
from ryoma_ai.vector_store.config import VectorStoreConfig
from ryoma_ai.vector_store.factory import create_vector_store

# NEW IMPORTS
from ryoma_ai.domain.interfaces import (
    DataSourceRepository,
    CatalogIndexer,
    CatalogSearcher,
)
from ryoma_ai.services.datasource_service import DataSourceService
from ryoma_ai.services.catalog_service import CatalogService
from ryoma_ai.infrastructure.datasource_repository import StoreBasedDataSourceRepository
from ryoma_ai.infrastructure.catalog_adapter import (
    CatalogIndexerAdapter,
    CatalogSearcherAdapter,
)

logger = logging.getLogger(__name__)


class BaseAgent:
    """
    Base class for all agents in Ryoma.

    DEPRECATION NOTICE: Direct datasource and catalog management
    will be removed in v0.2.0. Use DataSourceService and CatalogService instead.
    """

    type: AgentType = AgentType.base
    description: str = "Ryoma Agent is your best friend!"
    vector_store: Optional[VectorStore] = None

    def __init__(
        self,
        datasource: Optional[DataSource] = None,
        embedding: Optional[Union[dict, Embeddings]] = None,
        vector_store: Optional[Union[dict, VectorStore]] = None,
        store=None,
        # NEW: Optional service injection
        datasource_service: Optional[DataSourceService] = None,
        catalog_service: Optional[CatalogService] = None,
        **kwargs,
    ):
        self.resource_registry = ResourceRegistry()

        # Initialize store for InjectedStore functionality
        if store is None:
            from langchain_core.stores import InMemoryStore
            self.store = InMemoryStore()
            logger.info(
                "Using default InMemoryStore - for production, pass unified store from CLI"
            )
        else:
            self.store = store

        # NEW: Initialize services (new way)
        if datasource_service:
            self._datasource_service = datasource_service
        else:
            # Create default service for backward compatibility
            repository = StoreBasedDataSourceRepository(self.store)
            self._datasource_service = DataSourceService(repository)

        # Keep old pattern for backward compatibility
        if datasource:
            self.add_datasource(datasource)

        if embedding:
            self.embedding = self.init_embedding(embedding)

        if vector_store:
            embedding_to_use = getattr(self, "embedding", None)
            self.vector_store = self.init_vector_store(vector_store, embedding_to_use)

        # Initialize catalog service (new way) or old service (backward compat)
        if catalog_service:
            self._catalog_service = catalog_service
            # Also keep old service for backward compat
            self._catalog_index_service = None
        else:
            # Old pattern for backward compatibility
            self._catalog_index_service = None
            if hasattr(self, "vector_store") and self.vector_store:
                self._catalog_index_service = UnifiedCatalogIndexService(
                    vector_store=self.vector_store,
                    metadata_store=self.store,
                )
                # Wrap in new service
                indexer = CatalogIndexerAdapter(self._catalog_index_service)
                searcher = CatalogSearcherAdapter(self._get_catalog_store())
                self._catalog_service = CatalogService(indexer, searcher)

        self._catalog_store = None

    # ... (keep all existing init methods) ...

    def add_datasource(self, datasource: DataSource):
        """
        Register a DataSource as a resource.

        DEPRECATED: Use DataSourceService.add_datasource() instead.
        This method will be removed in v0.2.0.

        Args:
            datasource: DataSource instance to add
        """
        warnings.warn(
            "BaseAgent.add_datasource() is deprecated. "
            "Use DataSourceService.add_datasource() instead. "
            "This will be removed in v0.2.0.",
            DeprecationWarning,
            stacklevel=2
        )

        # Use new service internally
        self._datasource_service.add_datasource(datasource)

        # Keep old behavior for resource registry
        self.resource_registry.register_resource(
            "DataSource", datasource.id, datasource
        )

    def get_datasource(self) -> DataSource:
        """
        Get the active DataSource.

        DEPRECATED: Use DataSourceService.get_active_datasource() instead.
        This method will be removed in v0.2.0.

        Returns:
            The active DataSource
        """
        warnings.warn(
            "BaseAgent.get_datasource() is deprecated. "
            "Use DataSourceService.get_active_datasource() instead. "
            "This will be removed in v0.2.0.",
            DeprecationWarning,
            stacklevel=2
        )

        return self._datasource_service.get_active_datasource()

    def index_datasource(
        self,
        datasource: DataSource,
        data_source_id: str,
        level: Literal["catalog", "schema", "table", "column"] = "column",
    ) -> str:
        """
        Index a datasource's catalog.

        DEPRECATED: Use CatalogService.index_datasource() instead.
        This method will be removed in v0.2.0.

        Args:
            datasource: DataSource to index
            data_source_id: Unique identifier for the datasource
            level: Level of indexing

        Returns:
            Catalog ID
        """
        warnings.warn(
            "BaseAgent.index_datasource() is deprecated. "
            "Use CatalogService.index_datasource() instead. "
            "This will be removed in v0.2.0.",
            DeprecationWarning,
            stacklevel=2
        )

        if not self._catalog_service:
            raise ValueError(
                "Catalog service not initialized. "
                "Provide vector_store during agent creation."
            )

        return self._catalog_service.index_datasource(datasource, level)

    def search_catalogs(
        self,
        query: str,
        top_k: int = 5,
        level: Literal["catalog", "schema", "table", "column"] = "column",
    ) -> List[dict]:
        """
        Search catalogs semantically.

        DEPRECATED: Use CatalogService.search_tables() or search_columns() instead.
        This method will be removed in v0.2.0.
        """
        warnings.warn(
            "BaseAgent.search_catalogs() is deprecated. "
            "Use CatalogService methods instead. "
            "This will be removed in v0.2.0.",
            DeprecationWarning,
            stacklevel=2
        )

        if not self._catalog_service:
            raise ValueError("Catalog service not initialized")

        # Delegate to new service
        if level == "table":
            return self._catalog_service.search_tables(query, top_k)
        elif level == "column":
            return self._catalog_service.search_columns(query, top_k=top_k)
        else:
            # For other levels, use the searcher directly
            catalog_store = self._get_catalog_store()
            return catalog_store.search_catalogs(query, top_k, level)

    # ... (keep other existing methods) ...
```

**Key Changes:**
- ✅ Add optional service parameters to `__init__`
- ✅ Create services if not provided (backward compat)
- ✅ Wrap old APIs with deprecation warnings
- ✅ Delegate to new services internally
- ✅ Keep all old methods working

**Verification:**
```bash
# Run existing tests - they should all pass
cd packages/ryoma_ai
pytest tests/ -v -k "not slow"

# Check for deprecation warnings
python -c "
from ryoma_ai.agent.base import BaseAgent
from ryoma_data.sql import DataSource
import warnings
warnings.simplefilter('always', DeprecationWarning)

agent = BaseAgent()
ds = DataSource(backend='duckdb', database=':memory:')
agent.add_datasource(ds)  # Should show deprecation warning
"
```

---

### Step 2.2: Update SQL Tools to Use Constants (2 hours)

**Modified File: `tool/sql_tool.py`**

```python
# tool/sql_tool.py - UPDATED
import logging
from typing import TYPE_CHECKING, Any, Optional

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from ryoma_data.sql import SqlDataSource

# NEW IMPORT
from ryoma_ai.domain.constants import StoreKeys

if TYPE_CHECKING:
    from langchain_core.stores import BaseStore

logger = logging.getLogger(__name__)


def get_datasource_from_store(store: "BaseStore") -> SqlDataSource:
    """
    Get datasource from injected store.

    Args:
        store: Injected store from LangGraph

    Returns:
        Active SQL datasource

    Raises:
        ValueError: If no datasource found
    """
    # USE CONSTANT instead of magic string
    results = store.mget([StoreKeys.ACTIVE_DATASOURCE])
    datasource = results[0] if results and results[0] is not None else None

    if not datasource:
        raise ValueError(
            "No datasource available in store. "
            f"Expected key: {StoreKeys.ACTIVE_DATASOURCE}"
        )

    return ensure_sql_datasource(datasource)

# ... rest of file unchanged ...
```

**Apply same changes to:**
- `tool/python_tool.py`
- `tool/pandas_tool.py`
- `tool/spark_tool.py`

**Verification:**
```bash
# Grep for hardcoded strings - should find none in tools
cd packages/ryoma_ai
grep -r '"datasource_main"' ryoma_ai/tool/
# Should return no results after changes
```

---

### Step 2.3: Extract SQL Tool Definitions (3 hours)

**New File: `agent/sql_tools.py`**

```python
"""Centralized SQL tool definitions to avoid duplication"""

from typing import List
from langchain_core.tools import BaseTool
from ryoma_ai.tool.sql_tool import (
    SqlQueryTool,
    CreateTableTool,
    QueryProfileTool,
    QueryExplanationTool,
    QueryOptimizationTool,
)


def get_basic_sql_tools() -> List[BaseTool]:
    """Get basic SQL tools for simple agent mode"""
    return [
        SqlQueryTool(),
        CreateTableTool(),
        QueryProfileTool(),
    ]


def get_enhanced_sql_tools() -> List[BaseTool]:
    """Get enhanced SQL tools with additional capabilities"""
    basic_tools = get_basic_sql_tools()
    enhanced_tools = [
        QueryExplanationTool(),
        QueryOptimizationTool(),
        # Add other enhanced tools
    ]
    return basic_tools + enhanced_tools


def get_reforce_sql_tools() -> List[BaseTool]:
    """Get ReFoRCE SQL tools"""
    # ReFoRCE uses same tools as enhanced for now
    return get_enhanced_sql_tools()
```

**Modified File: `agent/sql.py`**

```python
# agent/sql.py - UPDATED
from ryoma_ai.agent.sql_tools import (
    get_basic_sql_tools,
    get_enhanced_sql_tools,
    get_reforce_sql_tools,
)

# In BasicSqlAgent.__init__ (Line ~122)
def __init__(self, model, datasource=None, store=None, **kwargs):
    # OLD: tools = [SqlQueryTool(), CreateTableTool(), QueryProfileTool()]
    # NEW: Use centralized definition
    tools = get_basic_sql_tools()

    super().__init__(
        model=model,
        tools=tools,
        datasource=datasource,
        store=store,
        **kwargs
    )

# Similar changes for EnhancedSqlAgent and ReFoRCESqlAgent
```

**Verification:**
```bash
# Check for tool duplication - should find none
cd packages/ryoma_ai
grep -A5 "SqlQueryTool()" ryoma_ai/agent/sql.py
# Should only see imports, not inline definitions
```

---

### Step 2.4: Update CLI to Use Services (8 hours)

**Modified File: `cli/app.py`**

This is a larger change - I'll show the key parts:

```python
# cli/app.py - UPDATED (key sections)
from ryoma_ai.services.datasource_service import DataSourceService
from ryoma_ai.services.catalog_service import CatalogService
from ryoma_ai.infrastructure.datasource_repository import StoreBasedDataSourceRepository
from ryoma_ai.infrastructure.catalog_adapter import (
    CatalogIndexerAdapter,
    CatalogSearcherAdapter,
)

class RyomaAI:
    def __init__(self):
        self.console = Console()
        self.config_manager = ConfigManager()

        # Setup store (unchanged)
        self.meta_store = self._setup_meta_store()

        # Setup embedding and vector store (unchanged)
        self.embedding = self._setup_embedding()
        self.vector_store = self._setup_vector_store()

        # NEW: Initialize services
        self.datasource_service = self._create_datasource_service()
        self.catalog_service = self._create_catalog_service()

        # Keep old managers for backward compatibility
        self.datasource_manager = DataSourceManager(...)
        self.agent_manager = AgentManager(...)
        self.command_handler = CommandHandler(...)

    def _create_datasource_service(self) -> DataSourceService:
        """Create datasource service"""
        repository = StoreBasedDataSourceRepository(self.meta_store)
        return DataSourceService(repository)

    def _create_catalog_service(self) -> CatalogService:
        """Create catalog service"""
        if not self.vector_store:
            return None

        # Create indexing service
        from ryoma_ai.catalog.indexer import UnifiedCatalogIndexService
        index_service = UnifiedCatalogIndexService(
            vector_store=self.vector_store,
            metadata_store=self.meta_store,
        )

        # Create catalog store for search
        from ryoma_ai.store.catalog_store import CatalogStore
        catalog_store = CatalogStore(
            vector_store=self.vector_store,
            metadata_store=self.meta_store,
        )

        # Wrap in adapters
        indexer = CatalogIndexerAdapter(index_service)
        searcher = CatalogSearcherAdapter(catalog_store)

        return CatalogService(indexer, searcher)

    # Update command handlers to use services
    def handle_datasource_add(self, config):
        """Add datasource using new service"""
        datasource = self._create_datasource_from_config(config)

        # Use new service
        self.datasource_service.add_datasource(datasource)

        # Also update old manager for backward compat
        self.datasource_manager.add_datasource(datasource)

        self.console.print(f"[green]Added datasource: {datasource.id}[/green]")

    def handle_index_catalog(self):
        """Index catalog using new service"""
        datasource = self.datasource_service.get_active_datasource()

        with self.console.status("Indexing catalog..."):
            catalog_id = self.catalog_service.index_datasource(datasource)

        self.console.print(f"[green]Indexed catalog: {catalog_id}[/green]")
```

**Verification:**
```bash
# Run CLI and test commands
cd packages/ryoma_ai
python -m ryoma_ai.cli.main

# In CLI:
# /datasource add --type duckdb --database :memory:
# /index-catalog
# Should work without errors
```

---

### Phase 2 Deliverables

✅ **Modified Files:**
- `agent/base.py` - Dual API (old + new)
- `tool/sql_tool.py` - Uses constants
- `agent/sql.py` - No tool duplication
- `cli/app.py` - Uses services

✅ **Deprecation Warnings:** Added to all old APIs

✅ **Backward Compatibility:** 100% (all old code still works)

✅ **Tests:** All existing tests pass

---

## 📅 Phase 3: Agent Simplification (Week 5)

**Goal:** Create new simplified agent classes that ONLY use services

**Risk:** LOW (creating new classes alongside old ones)

### Step 3.1: Create New Minimal BaseAgent (4 hours)

**New File: `agent/base_v2.py`**

```python
"""
Simplified BaseAgent (v2) - Clean architecture version.
This will become the new BaseAgent in v0.2.0.
"""

import logging
from typing import List, Optional
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool

logger = logging.getLogger(__name__)


class BaseAgentV2:
    """
    Simplified base agent - ONLY handles conversation.
    All infrastructure managed by services.

    This is the future of Ryoma agents - clean, focused, testable.
    """

    def __init__(
        self,
        model: BaseChatModel,
        tools: Optional[List[BaseTool]] = None,
        system_prompt: Optional[str] = None,
    ):
        """
        Initialize agent.

        Args:
            model: Language model for reasoning
            tools: List of tools available to agent
            system_prompt: System instructions
        """
        self.model = model
        self.tools = tools or []
        self.system_prompt = system_prompt or "You are a helpful AI assistant."

        logger.info(
            f"Initialized {self.__class__.__name__} with "
            f"{len(self.tools)} tools"
        )

    def stream(self, user_input: str):
        """
        Stream response to user input.

        Args:
            user_input: User's question or command

        Yields:
            Response chunks
        """
        raise NotImplementedError("Subclasses must implement stream()")

    def invoke(self, user_input: str):
        """
        Synchronously invoke agent.

        Args:
            user_input: User's question or command

        Returns:
            Complete response
        """
        raise NotImplementedError("Subclasses must implement invoke()")

    async def ainvoke(self, user_input: str):
        """
        Asynchronously invoke agent.

        Args:
            user_input: User's question or command

        Returns:
            Complete response
        """
        raise NotImplementedError("Subclasses must implement ainvoke()")
```

**Benefits:**
- ✅ Only ~50 lines
- ✅ Single responsibility
- ✅ No infrastructure dependencies
- ✅ Easy to test

---

### Step 3.2: Create AgentBuilder Service (6 hours)

**New File: `services/agent_builder.py`**

```python
"""Service for building fully-configured agents"""

import logging
from typing import Optional, List, Literal
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool

from ryoma_data.base import DataSource
from ryoma_ai.services.datasource_service import DataSourceService
from ryoma_ai.services.catalog_service import CatalogService
from ryoma_ai.agent.base_v2 import BaseAgentV2
from ryoma_ai.agent.workflow import WorkflowAgent
from ryoma_ai.llm.provider import load_model_provider

logger = logging.getLogger(__name__)


class AgentBuilder:
    """
    Service for building fully-configured agents.
    Handles all infrastructure wiring so agents stay clean.
    """

    def __init__(
        self,
        datasource_service: DataSourceService,
        catalog_service: Optional[CatalogService] = None,
    ):
        """
        Initialize builder.

        Args:
            datasource_service: Service for datasource management
            catalog_service: Optional service for catalog operations
        """
        self._datasource_service = datasource_service
        self._catalog_service = catalog_service

    def build_sql_agent(
        self,
        model: str = "gpt-3.5-turbo",
        mode: Literal["basic", "enhanced", "reforce"] = "basic",
        model_params: Optional[dict] = None,
    ) -> BaseAgentV2:
        """
        Build a SQL agent with all tools configured.

        Args:
            model: Model identifier
            mode: Agent mode (basic/enhanced/reforce)
            model_params: Optional model parameters

        Returns:
            Configured SQL agent
        """
        # Get datasource
        try:
            datasource = self._datasource_service.get_active_datasource()
        except ValueError:
            raise ValueError(
                "No active datasource. "
                "Use datasource_service.add_datasource() first."
            )

        # Build tools based on mode
        tools = self._build_sql_tools(datasource, mode)

        # Get LLM
        llm = self._create_llm(model, model_params)

        # Create agent
        system_prompt = self._get_sql_prompt(mode)
        agent = WorkflowAgent(
            model=llm,
            tools=tools,
            system_prompt=system_prompt,
        )

        logger.info(f"Built SQL agent (mode={mode}, tools={len(tools)})")
        return agent

    def build_python_agent(
        self,
        model: str = "gpt-3.5-turbo",
        model_params: Optional[dict] = None,
    ) -> BaseAgentV2:
        """Build a Python agent"""
        from ryoma_ai.tool.python_tool import PythonREPLTool

        llm = self._create_llm(model, model_params)
        tools = [PythonREPLTool()]

        agent = WorkflowAgent(
            model=llm,
            tools=tools,
            system_prompt="You are a Python programming expert.",
        )

        return agent

    def _build_sql_tools(
        self,
        datasource: DataSource,
        mode: str
    ) -> List[BaseTool]:
        """Build SQL tools based on mode"""
        from ryoma_ai.agent.sql_tools import (
            get_basic_sql_tools,
            get_enhanced_sql_tools,
            get_reforce_sql_tools,
        )

        if mode == "basic":
            return get_basic_sql_tools()
        elif mode == "enhanced":
            tools = get_enhanced_sql_tools()

            # Add catalog-aware tools if available
            if self._catalog_service:
                tools.extend(self._get_catalog_tools(datasource))

            return tools
        elif mode == "reforce":
            return get_reforce_sql_tools()
        else:
            raise ValueError(f"Unknown SQL mode: {mode}")

    def _get_catalog_tools(self, datasource: DataSource) -> List[BaseTool]:
        """Get catalog-aware tools"""
        # Implementation for schema analysis tools
        # that use catalog_service
        return []

    def _create_llm(
        self,
        model: str,
        model_params: Optional[dict] = None
    ) -> BaseChatModel:
        """Create LLM instance"""
        params = model_params or {}
        return load_model_provider(model, model_parameters=params)

    def _get_sql_prompt(self, mode: str) -> str:
        """Get system prompt for SQL agent"""
        prompts = {
            "basic": "You are a SQL expert. Write queries to answer questions.",
            "enhanced": (
                "You are an advanced SQL expert. "
                "Use schema analysis and query planning for complex queries."
            ),
            "reforce": (
                "You are a SQL expert using the ReFoRCE approach. "
                "Plan queries carefully, reflect on results, and refine as needed."
            ),
        }
        return prompts.get(mode, prompts["basic"])
```

**Usage Example:**
```python
# New clean way to create agents
from ryoma_ai.services.agent_builder import AgentBuilder

# Services already initialized by CLI/app
agent = agent_builder.build_sql_agent(
    model="gpt-4",
    mode="enhanced"
)

# Agent is clean - just chat!
response = agent.stream("What are the top 5 customers?")
```

---

### Step 3.3: Update CLI to Support Both Old and New (4 hours)

**Modified File: `cli/app.py`**

```python
# cli/app.py - UPDATED with v2 support
class RyomaAI:
    def __init__(self, use_v2_agents: bool = False):
        """
        Initialize CLI app.

        Args:
            use_v2_agents: If True, use new simplified agents (experimental)
        """
        # ... existing initialization ...

        self.use_v2_agents = use_v2_agents

        # NEW: Create agent builder
        if use_v2_agents:
            from ryoma_ai.services.agent_builder import AgentBuilder
            self.agent_builder = AgentBuilder(
                datasource_service=self.datasource_service,
                catalog_service=self.catalog_service,
            )

    def create_agent(self, agent_type: str):
        """Create agent (supports v1 and v2)"""
        if self.use_v2_agents:
            # Use new builder
            if agent_type == "sql":
                return self.agent_builder.build_sql_agent()
            elif agent_type == "python":
                return self.agent_builder.build_python_agent()
            else:
                raise ValueError(f"Unknown agent type: {agent_type}")
        else:
            # Use old factory (backward compat)
            return self.agent_manager.create_agent(agent_type)
```

**Add CLI flag:**
```python
# cli/main.py - UPDATED
import typer

app = typer.Typer()

@app.command()
def main(
    v2: bool = typer.Option(
        False,
        "--v2",
        help="Use experimental v2 agents (simplified architecture)"
    )
):
    """Start Ryoma AI CLI"""
    ryoma = RyomaAI(use_v2_agents=v2)
    ryoma.run()
```

**Usage:**
```bash
# Use old agents (default)
python -m ryoma_ai.cli.main

# Use new v2 agents (opt-in)
python -m ryoma_ai.cli.main --v2
```

---

### Phase 3 Deliverables

✅ **New Files:**
- `agent/base_v2.py` - Clean agent base class
- `services/agent_builder.py` - Agent construction service

✅ **Modified Files:**
- `cli/app.py` - Supports both v1 and v2

✅ **Backward Compatibility:** 100% (v2 is opt-in)

✅ **New API:** Available for testing

---

## 📅 Phase 4: Cleanup & Optimization (Week 6)

**Goal:** Remove deprecated code and optimize new architecture

**Risk:** HIGH (breaking changes for those not migrated)

### Step 4.1: Version Bump and Deprecation Notices (2 hours)

**Modified File: `pyproject.toml`**

```toml
[project]
name = "ryoma-ai"
version = "0.2.0"  # MAJOR VERSION BUMP
description = "AI-Powered Data Agent Framework - Simplified Architecture"

[project.optional-dependencies]
# Add migration guide
migration = [
    "ryoma-ai-v1==0.1.5"  # Old version for comparison
]
```

**New File: `MIGRATION_GUIDE_v0.2.md`**

Document all breaking changes and migration steps.

---

### Step 4.2: Remove Deprecated Code (8 hours)

**High-Risk Changes:**

1. **Remove old methods from BaseAgent:**
```python
# agent/base.py - UPDATED for v0.2.0
class BaseAgent(BaseAgentV2):
    """
    Base agent class - simplified in v0.2.0.

    BREAKING CHANGES from v0.1.x:
    - Removed: add_datasource() - Use DataSourceService
    - Removed: get_datasource() - Use DataSourceService
    - Removed: index_datasource() - Use CatalogService
    - Removed: search_catalogs() - Use CatalogService
    - Removed: resource_registry - No longer needed
    """

    # Now just inherits from BaseAgentV2
    # All old methods removed
```

2. **Rename base_v2.py to base.py:**
```bash
cd packages/ryoma_ai/ryoma_ai/agent
mv base.py base_v1_deprecated.py
mv base_v2.py base.py
```

3. **Update all imports:**
```python
# All files that imported BaseAgent
from ryoma_ai.agent.base import BaseAgent  # Now gets BaseAgentV2
```

---

### Step 4.3: Optimize Service Layer (4 hours)

**Add caching, connection pooling, etc.**

Example:
```python
# services/catalog_service.py - OPTIMIZED
from functools import lru_cache

class CatalogService:
    @lru_cache(maxsize=100)
    def search_tables(self, query: str, top_k: int = 5):
        """Search with caching"""
        # Implementation
```

---

### Step 4.4: Update All Documentation (6 hours)

Update:
- README.md
- API documentation
- Examples
- Migration guide

---

### Phase 4 Deliverables

✅ **Version:** 0.2.0 (breaking changes)

✅ **Removed:** All deprecated code

✅ **Optimized:** Service layer

✅ **Documentation:** Complete migration guide

---

## 🧪 Testing Strategy

### Test Categories

1. **Unit Tests** (Phase 1-3)
   - Test each service in isolation
   - Mock all dependencies
   - Target: 80% coverage

2. **Integration Tests** (Phase 2-3)
   - Test service interactions
   - Use real stores (InMemory)
   - Test old and new APIs

3. **End-to-End Tests** (Phase 3-4)
   - Test full workflows
   - CLI commands
   - Agent creation and execution

4. **Backward Compatibility Tests** (Phase 2-3)
   - Ensure old code still works
   - Verify deprecation warnings
   - Test migration path

### Test Commands

```bash
# Phase 1: Unit tests for new code
pytest tests/unit/services/ -v

# Phase 2: Backward compatibility
pytest tests/ -v -W error::DeprecationWarning

# Phase 3: Integration tests
pytest tests/integration/ -v

# Phase 4: Full test suite
pytest tests/ -v --cov=ryoma_ai --cov-report=html
```

---

## 🔄 Rollback Plan

### Phase 1 Rollback
**Risk:** LOW

**Rollback Steps:**
1. Delete new directories: `domain/`, `infrastructure/`, `services/`
2. Revert `pyproject.toml`
3. No code dependencies, so safe to remove

### Phase 2 Rollback
**Risk:** MEDIUM

**Rollback Steps:**
1. Revert `agent/base.py` to original
2. Revert `tool/sql_tool.py` to use magic strings
3. Revert `cli/app.py`
4. Remove deprecation warnings
5. Keep Phase 1 files (they're not used)

### Phase 3 Rollback
**Risk:** LOW

**Rollback Steps:**
1. Remove `agent/base_v2.py`
2. Remove `services/agent_builder.py`
3. Revert CLI to not support `--v2` flag
4. No impact on existing users

### Phase 4 Rollback
**Risk:** HIGH (can't rollback easily)

**Mitigation:**
1. Release v0.2.0-beta first
2. Get community feedback
3. Wait 2-4 weeks before stable v0.2.0
4. Maintain v0.1.x branch for critical fixes

---

## 📊 Risk Assessment

| Phase | Risk | Mitigation | Can Rollback? |
|-------|------|------------|---------------|
| Phase 1 | LOW | Only adding new code, no changes to existing | ✅ YES (easy) |
| Phase 2 | MEDIUM | Deprecation warnings, dual API support | ✅ YES (moderate) |
| Phase 3 | LOW | New code opt-in with flag | ✅ YES (easy) |
| Phase 4 | HIGH | Breaking changes | ⚠️ NO (hard) |

---

## 📅 Timeline Summary

| Phase | Duration | Effort | Risk |
|-------|----------|--------|------|
| Phase 1: Foundation | 1-2 weeks | 16 hours | LOW |
| Phase 2: Compat Refactor | 1-2 weeks | 19 hours | MEDIUM |
| Phase 3: Simplification | 1 week | 14 hours | LOW |
| Phase 4: Cleanup | 1 week | 20 hours | HIGH |
| **TOTAL** | **4-6 weeks** | **69 hours** | **MEDIUM** |

**Recommended Pace:**
- Part-time (10 hrs/week): 6-7 weeks
- Full-time (40 hrs/week): 2 weeks

---

## ✅ Success Criteria

### Phase 1 Success
- [ ] All new interfaces and services created
- [ ] All tests passing
- [ ] No existing code modified
- [ ] Documentation for new services

### Phase 2 Success
- [ ] BaseAgent uses services internally
- [ ] All deprecation warnings in place
- [ ] All existing tests passing
- [ ] No breaking changes

### Phase 3 Success
- [ ] BaseAgentV2 created and working
- [ ] AgentBuilder can create all agent types
- [ ] CLI supports `--v2` flag
- [ ] Side-by-side comparison docs

### Phase 4 Success
- [ ] Version 0.2.0 released
- [ ] Migration guide complete
- [ ] All deprecated code removed
- [ ] Performance benchmarks improved
- [ ] Community feedback addressed

---

## 🎯 Next Steps

To begin this migration:

1. **Review this plan** with team/stakeholders
2. **Create feature branch**: `git checkout -b refactor/service-layer`
3. **Start Phase 1**: Create domain interfaces
4. **Write tests first**: TDD approach for new services
5. **Small commits**: Commit after each step
6. **Continuous integration**: Ensure tests pass after each change

---

## 📝 Notes

### Why This Approach?

- **Incremental**: Small, reviewable changes
- **Safe**: Backward compatible until Phase 4
- **Testable**: Each phase can be tested independently
- **Reversible**: Can rollback phases 1-3 easily
- **Professional**: Following industry best practices

### Alternative Approaches Considered

1. **Big Bang Rewrite**: Too risky, would break all users
2. **Fork v2**: Doubles maintenance burden
3. **Gradual Inline Refactor**: Too slow, confusing for users

**Chosen Approach**: Incremental with backward compatibility - best balance of safety and progress.

---

**END OF MIGRATION PLAN**

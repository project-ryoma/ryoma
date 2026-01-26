"""Centralized constants to eliminate magic strings"""


class StoreKeys:
    """Keys used in metadata store"""

    # Primary key for active datasource (backward compatible)
    ACTIVE_DATASOURCE = "datasource_main"

    # Prefix for storing multiple datasources
    DATASOURCES_PREFIX = "datasources:"

    # Key for tracking which datasource is active (new multi-datasource support)
    ACTIVE_DATASOURCE_ID = "active_datasource_id"

    # Key for list of all datasource IDs
    DATASOURCE_IDS = "datasource_ids"


class AgentDefaults:
    """Default configurations for agents"""

    # Default LLM model
    DEFAULT_MODEL = "gpt-3.5-turbo"

    # Default temperature for LLM
    DEFAULT_TEMPERATURE = 0.0

    # Maximum iterations for agent loops
    MAX_ITERATIONS = 10

    # Default top-k for catalog search
    DEFAULT_TOP_K = 5


class CatalogLevels:
    """Valid catalog indexing/search levels"""

    CATALOG = "catalog"
    SCHEMA = "schema"
    TABLE = "table"
    COLUMN = "column"

    @classmethod
    def all(cls) -> list[str]:
        """Get all valid levels"""
        return [cls.CATALOG, cls.SCHEMA, cls.TABLE, cls.COLUMN]

    @classmethod
    def is_valid(cls, level: str) -> bool:
        """Check if level is valid"""
        return level in cls.all()

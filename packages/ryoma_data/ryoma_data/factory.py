from enum import Enum
from importlib import import_module
from typing import Any, Dict, Type

from pydantic import BaseModel

# Map datasource names to their module paths and class names
DATASOURCE_REGISTRY = {
    # SQL datasources now use unified DataSource
    "mysql": {
        "module": "ryoma_data.sql",
        "class": "DataSource",
        "backend": "mysql",
        "config": None,
    },
    "postgres": {
        "module": "ryoma_data.sql",
        "class": "DataSource",
        "backend": "postgres",
        "config": None,
    },
    "bigquery": {
        "module": "ryoma_data.sql",
        "class": "DataSource",
        "backend": "bigquery",
        "config": None,
    },
    "snowflake": {
        "module": "ryoma_data.sql",
        "class": "DataSource",
        "backend": "snowflake",
        "config": None,
    },
    "sqlite": {
        "module": "ryoma_data.sql",
        "class": "DataSource",
        "backend": "sqlite",
        "config": None,
    },
    "duckdb": {
        "module": "ryoma_data.sql",
        "class": "DataSource",
        "backend": "duckdb",
        "config": None,
    },
    # Non-SQL datasources keep their original implementations
    "file": {
        "module": "ryoma_data.file",
        "class": "FileDataSource",
        "config": "FileConfig",
    },
    "dynamodb": {
        "module": "ryoma_data.nosql",
        "class": "DynamodbDataSource",
        "config": "DynamodbConfig",
    },
    "iceberg": {
        "module": "ryoma_data.iceberg",
        "class": "IcebergDataSource",
        "config": "IcebergConfig",
    },
}


class DataSourceProvider(Enum):
    """Enumeration of supported datasource providers."""

    mysql = "mysql"
    postgres = "postgres"
    bigquery = "bigquery"
    snowflake = "snowflake"
    file = "file"
    dynamodb = "dynamodb"
    sqlite = "sqlite"
    duckdb = "duckdb"
    iceberg = "iceberg"


def _lazy_import(datasource: str, import_type: str = "class") -> Type[Any]:
    """Lazily import a datasource class or config to avoid dependency issues."""
    if datasource not in DATASOURCE_REGISTRY:
        raise ValueError(f"Unsupported datasource: {datasource}")

    registry_info = DATASOURCE_REGISTRY[datasource]
    module_path = registry_info["module"]

    if import_type == "class":
        class_name = registry_info["class"]
    elif import_type == "config":
        class_name = registry_info["config"]
        if not class_name:
            raise ValueError(f"No config class defined for datasource: {datasource}")
    else:
        raise ValueError(f"Invalid import_type: {import_type}")

    try:
        module = import_module(module_path)
        return getattr(module, class_name)
    except ImportError as e:
        # Provide helpful error message about missing dependencies
        raise ImportError(
            f"Failed to import {datasource} datasource. "
            f"Please install required dependencies for {datasource}. "
            f"Original error: {str(e)}"
        )
    except AttributeError:
        raise ImportError(f"Class {class_name} not found in module {module_path}")


def get_supported_datasources():
    return list(DataSourceProvider)


class DataSourceFactory:
    @staticmethod
    def create_datasource(datasource: str, *args, **kwargs) -> Any:
        """
        Create a datasource instance using lazy import to avoid dependency issues.

        Args:
            datasource: Datasource type (e.g., "postgres", "mysql", "snowflake")
            *args: Positional arguments passed to datasource constructor
            **kwargs: Keyword arguments passed to datasource constructor

        Returns:
            Datasource instance

        Example:
            # Create PostgreSQL datasource
            ds = DataSourceFactory.create_datasource(
                "postgres",
                host="localhost",
                port=5432,
                database="mydb"
            )
        """
        if not hasattr(DataSourceProvider, datasource):
            raise ValueError(f"Unsupported datasource: {datasource}")

        # Import base classes only when needed
        from ryoma_data.base import BaseDataSource

        registry_info = DATASOURCE_REGISTRY[datasource]
        datasource_class = _lazy_import(datasource, "class")

        # For DataSource, inject the backend parameter
        if registry_info.get("backend"):
            kwargs["backend"] = registry_info["backend"]

        instance = datasource_class(*args, **kwargs)

        # Verify it's a proper datasource instance
        if not isinstance(instance, BaseDataSource):
            raise TypeError(f"{datasource} must inherit from BaseDataSource")

        return instance

    @staticmethod
    def get_model_fields(model: Type[BaseModel]) -> Dict[str, Any]:
        """Get model fields from a Pydantic BaseModel class."""
        return model.model_fields.copy()

    @staticmethod
    def get_datasource_config(datasource: str) -> Dict[str, Any]:
        """Get datasource configuration fields using lazy import."""
        if not hasattr(DataSourceProvider, datasource):
            raise ValueError(f"Unsupported datasource: {datasource}")

        try:
            config_class = _lazy_import(datasource, "config")
            return DataSourceFactory.get_model_fields(config_class)
        except ValueError:
            # Some datasources don't have a config class
            return {}

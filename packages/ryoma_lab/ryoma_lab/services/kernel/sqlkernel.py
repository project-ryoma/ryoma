import logging
import re
from typing import Any, Dict

from ryoma_ai.datasource.base import SqlDataSource
from ryoma_ai.datasource.factory import DataSourceFactory
from ryoma_lab.services.kernel.base import BaseKernel
from sqlalchemy.exc import SQLAlchemyError


class SqlKernel(BaseKernel):
    datasource: SqlDataSource

    def __init__(self, datasource: SqlDataSource, **kwargs):
        if not datasource:
            datasource = DataSourceFactory.create_datasource("duckdb")
        super().__init__(datasource, **kwargs)

    def execute(self, query: str) -> Dict[str, Any]:
        logging.info(f"Executing SQL query: {query}")

        try:
            df = self.datasource.query(query)
            return {
                "output_type": "dataframe",
                "data": df,
            }
        except SQLAlchemyError as e:
            logging.error(f"SQLAlchemy error: {str(e)}")
            return self._create_error_response(e)
        except Exception as e:
            logging.error(f"Unexpected error: {str(e)}")
            return self._create_error_response(e)

    def _extract_datasource_from_query(self, query: str) -> str:
        # This regex looks for table names in common SQL patterns
        pattern = r'\bFROM\s+"?(\w+)"?|\bJOIN\s+"?(\w+)"?'
        matches = re.findall(pattern, query, re.IGNORECASE)
        # Flatten and filter the matches
        datasources = [ds for match in matches for ds in match if ds]
        return datasources[0] if datasources else None

    def _get_datasource(self, name: str) -> SqlDataSource:
        datasource = self.datasources.get(name)
        if datasource:
            logging.info(f"Found type: {name}")
        else:
            logging.warning(f"Datasource not found: {name}")
        return datasource

    def _remove_datasource_from_query(self, query: str, datasource_name: str) -> str:
        # Remove the type name from the query
        pattern = r"\b" + re.escape(datasource_name) + r"\."
        return re.sub(pattern, "", query, flags=re.IGNORECASE)

    def set_datasources(self, datasources: Dict[str, SqlDataSource]):
        self.datasources = datasources
        logging.info(f"Updated datasources: {list(self.datasources.keys())}")

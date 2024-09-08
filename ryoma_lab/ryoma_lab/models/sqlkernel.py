import logging
import re
from typing import Any, Dict

from sqlalchemy.exc import SQLAlchemyError

from ryoma_ai.datasource.base import DataSource
from ryoma_lab.models.kernel import BaseKernel


class SqlKernel(BaseKernel):
    def execute(self, code: str) -> Dict[str, Any]:
        logging.info(f"Executing SQL code: {code}")

        try:
            datasource_name = self._extract_datasource_from_query(code)
            logging.info(f"Extracted type name from query: {datasource_name}")

            if not datasource_name:
                raise ValueError("No valid type found in the query")

            datasource = self._get_datasource(datasource_name)
            if not datasource:
                raise ValueError(
                    f"Datasource '{datasource_name}' not found. Available datasources: {list(self.datasources.keys())}"
                )

            modified_query = self._remove_datasource_from_query(code, datasource_name)
            logging.info(f"Modified query: {modified_query}")

            df = datasource.query(modified_query)

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

    def _get_datasource(self, name: str) -> DataSource:
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

    def set_datasources(self, datasources: Dict[str, DataSource]):
        self.datasources = datasources
        logging.info(f"Updated datasources: {list(self.datasources.keys())}")

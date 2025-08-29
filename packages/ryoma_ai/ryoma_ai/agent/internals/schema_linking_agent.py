import logging
import re
from typing import Dict, List, Optional

from ryoma_ai.agent.chat_agent import ChatAgent
from ryoma_ai.datasource.metadata import Catalog, Column, Schema, Table
from ryoma_ai.datasource.sql import SqlDataSource

logger = logging.getLogger(__name__)


class SchemaLinkingAgent(ChatAgent):
    """
    Specialized agent for intelligent schema linking and table relationship analysis.
    Helps identify relevant tables and suggest optimal joins for complex queries.
    """

    def __init__(
        self,
        model: str,
        model_parameters: Optional[Dict] = None,
        datasource: Optional[SqlDataSource] = None,
        **kwargs,
    ):
        super().__init__(
            model=model,
            model_parameters=model_parameters,
            datasource=datasource,
            **kwargs,
        )
        self.catalog_cache = None

    def analyze_schema_relationships(self, question: str) -> Dict:
        """
        Analyze schema relationships and suggest relevant tables for a given question.

        Args:
            question: Natural language question

        Returns:
            Dictionary containing suggested tables, relationships, and join strategies
        """
        print("Step 1.1 - Analyzing schema relationships for question:", question)
        if not self.get_datasource():
            raise ValueError("DataSource is required for schema analysis")

        # Get catalog information
        catalog = self._get_catalog()

        # Extract entities and concepts from the question
        entities = self._extract_entities(question)

        # Find relevant tables
        relevant_tables = self._find_relevant_tables(entities, catalog)

        # Analyze relationships between tables
        relationships = self._analyze_table_relationships(relevant_tables, catalog)

        # Suggest join strategies
        join_strategies = self._suggest_join_strategies(relevant_tables, relationships)

        return {
            "question": question,
            "extracted_entities": entities,
            "relevant_tables": relevant_tables,
            "relationships": relationships,
            "join_strategies": join_strategies,
            "confidence_score": self._calculate_confidence(relevant_tables, entities),
        }

    def suggest_table_selection(self, question: str, max_tables: int = 5) -> List[Dict]:
        """
        Suggest the most relevant tables for a given question.

        Args:
            question: Natural language question
            max_tables: Maximum number of tables to suggest

        Returns:
            List of table suggestions with relevance scores
        """
        print("Step 1.2 - Suggesting table selection for question:", question)
        catalog = self._get_catalog()
        entities = self._extract_entities(question)

        table_scores = []

        for schema in catalog.schemas:
            for table in schema.tables:
                score = self._calculate_table_relevance(table, entities, question)
                if score > 0:
                    table_scores.append(
                        {
                            "schema": schema.schema_name,
                            "table": table.table_name,
                            "score": score,
                            "columns": [col.name for col in table.columns],
                            "reasoning": self._explain_table_relevance(table, entities),
                        }
                    )

        # Sort by score and return top results
        table_scores.sort(key=lambda x: x["score"], reverse=True)
        return table_scores[:max_tables]

    def generate_join_suggestions(self, tables: List[str]) -> List[Dict]:
        """
        Generate join suggestions for a list of tables.

        Args:
            tables: List of table names

        Returns:
            List of join suggestions with SQL snippets
        """
        catalog = self._get_catalog()
        join_suggestions = []

        # Find potential join paths between tables
        for i, table1 in enumerate(tables):
            for table2 in tables[i + 1 :]:
                join_info = self._find_join_path(table1, table2, catalog)
                if join_info:
                    join_suggestions.append(join_info)

        return join_suggestions

    def _get_catalog(self) -> Catalog:
        """Get catalog with caching - tries optimized search first if available."""
        if not self.catalog_cache:
            # Try optimized catalog access if vector store is available
            try:
                catalog_store = self._get_catalog_store()
                if catalog_store:
                    # Use table suggestions to get a relevant subset
                    table_suggestions = catalog_store.get_table_suggestions(
                        query="all tables",
                        max_tables=50,
                        min_score=0.0,  # Get all indexed tables
                    )
                    if table_suggestions:
                        # Build catalog from table suggestions
                        self.catalog_cache = self._build_catalog_from_suggestions(
                            table_suggestions
                        )
                    else:
                        # Fallback to full catalog
                        logger.warning(
                            "No indexed tables found. Loading full catalog - this may be slow for large databases. "
                            "Consider running '/index-catalog' command to improve performance."
                        )
                        self.catalog_cache = self.get_datasource().get_catalog()
                else:
                    # No vector store available, use full catalog
                    logger.warning(
                        "No vector store configured. Loading full catalog - this may be slow for large databases. "
                        "Consider configuring vector_store and running '/index-catalog' command to improve performance."
                    )
                    self.catalog_cache = self.get_datasource().get_catalog()
            except Exception as e:
                # Fallback to full catalog on any error
                logger.warning(
                    f"Optimized catalog access failed: {e}. Loading full catalog - this may be slow for large databases. "
                    "Consider configuring vector_store and running '/index-catalog' command to improve performance."
                )
                self.catalog_cache = self.get_datasource().get_catalog()
        return self.catalog_cache

    def _build_catalog_from_suggestions(self, table_suggestions: List[Dict]) -> Catalog:
        """Build a simplified catalog from table suggestions."""
        schema_data = {}

        for suggestion in table_suggestions:
            schema_name = suggestion.get("schema", "default")
            table_name = suggestion.get("table")

            if not table_name:
                continue

            if schema_name not in schema_data:
                schema_data[schema_name] = []

            # Create a basic table with minimal column info
            # In a real implementation, you might fetch column details from the catalog store
            table = Table(
                table_name=table_name,
                columns=[
                    Column(
                        name="*",
                        column_type="unknown",
                        nullable=True,
                        primary_key=False,
                        profile=None,
                    )
                ],  # Placeholder
                profile=None,
            )
            schema_data[schema_name].append(table)

        # Build schemas
        schemas = []
        for schema_name, tables in schema_data.items():
            if tables:
                schemas.append(Schema(schema_name=schema_name, tables=tables))

        return Catalog(catalog_name="indexed_tables", schemas=schemas)

    def _extract_entities(self, question: str) -> List[str]:
        """Extract business entities and concepts from the question."""
        question_lower = question.lower()

        # Common business entities
        business_entities = {
            "customer": ["customer", "client", "user", "buyer", "account"],
            "order": ["order", "purchase", "transaction", "sale", "buy"],
            "product": ["product", "item", "goods", "merchandise", "inventory"],
            "employee": ["employee", "staff", "worker", "person", "team"],
            "payment": ["payment", "invoice", "bill", "charge", "fee"],
            "date": ["date", "time", "when", "period", "year", "month", "day"],
            "amount": ["amount", "price", "cost", "value", "total", "sum"],
            "location": ["location", "address", "city", "state", "country", "region"],
        }

        found_entities = []
        for entity_type, keywords in business_entities.items():
            if any(keyword in question_lower for keyword in keywords):
                found_entities.append(entity_type)

        # Extract specific terms that might be table or column names
        words = re.findall(r"\b[a-zA-Z_][a-zA-Z0-9_]*\b", question)
        found_entities.extend([word.lower() for word in words if len(word) > 2])

        return list(set(found_entities))

    def _find_relevant_tables(
        self, entities: List[str], catalog: Catalog
    ) -> List[Dict]:
        """Find tables relevant to the extracted entities."""
        relevant_tables = []

        for schema in catalog.schemas:
            for table in schema.tables:
                relevance_score = self._calculate_table_relevance(table, entities, "")
                if relevance_score > 0:
                    relevant_tables.append(
                        {
                            "schema": schema.schema_name,
                            "table": table.table_name,
                            "score": relevance_score,
                            "table_obj": table,
                        }
                    )

        return sorted(relevant_tables, key=lambda x: x["score"], reverse=True)

    def _calculate_table_relevance(
        self, table: Table, entities: List[str], question: str
    ) -> float:
        """Calculate how relevant a table is to the given entities and question."""
        score = 0.0

        # Score based on table name matching entities
        table_name_lower = table.table_name.lower()
        for entity in entities:
            if entity in table_name_lower:
                score += 3.0
            elif any(part in table_name_lower for part in entity.split("_")):
                score += 1.5

        # Score based on column names matching entities
        for column in table.columns:
            column_name_lower = column.name.lower()
            for entity in entities:
                if entity in column_name_lower:
                    score += 2.0
                elif any(part in column_name_lower for part in entity.split("_")):
                    score += 1.0

        # Boost score for common relationship patterns
        if any(col.name.lower().endswith("_id") for col in table.columns):
            score += 0.5  # Tables with foreign keys are often important

        return score

    def _analyze_table_relationships(
        self, relevant_tables: List[Dict], catalog: Catalog
    ) -> List[Dict]:
        """Analyze relationships between relevant tables."""
        relationships = []

        for i, table1 in enumerate(relevant_tables):
            for table2 in relevant_tables[i + 1 :]:
                relationship = self._find_relationship(
                    table1["table_obj"], table2["table_obj"]
                )
                if relationship:
                    relationships.append(
                        {
                            "table1": f"{table1['schema']}.{table1['table']}",
                            "table2": f"{table2['schema']}.{table2['table']}",
                            "relationship_type": relationship["type"],
                            "join_columns": relationship["columns"],
                            "confidence": relationship["confidence"],
                        }
                    )

        return relationships

    def _find_relationship(self, table1: Table, table2: Table) -> Optional[Dict]:
        """Find relationship between two tables."""
        # Look for foreign key relationships
        for col1 in table1.columns:
            for col2 in table2.columns:
                if self._is_likely_foreign_key_relationship(col1, col2, table1, table2):
                    return {
                        "type": "foreign_key",
                        "columns": [(col1.name, col2.name)],
                        "confidence": 0.8,
                    }

        # Look for common column names (potential joins)
        common_columns = []
        for col1 in table1.columns:
            for col2 in table2.columns:
                if col1.name.lower() == col2.name.lower():
                    common_columns.append((col1.name, col2.name))

        if common_columns:
            return {
                "type": "common_column",
                "columns": common_columns,
                "confidence": 0.6,
            }

        return None

    def _is_likely_foreign_key_relationship(
        self, col1: Column, col2: Column, table1: Table, table2: Table
    ) -> bool:
        """Determine if two columns likely represent a foreign key relationship."""
        # Check if one column name contains the other table's name
        if (
            table2.table_name.lower() + "_id" == col1.name.lower()
            or table1.table_name.lower() + "_id" == col2.name.lower()
        ):
            return True

        # Check for id columns
        if (col1.name.lower() == "id" and col2.name.lower().endswith("_id")) or (
            col2.name.lower() == "id" and col1.name.lower().endswith("_id")
        ):
            return True

        return False

    def _suggest_join_strategies(
        self, relevant_tables: List[Dict], relationships: List[Dict]
    ) -> List[Dict]:
        """Suggest optimal join strategies."""
        strategies = []

        if len(relevant_tables) < 2:
            return strategies

        # Create join strategy for each relationship
        for rel in relationships:
            strategy = {
                "tables": [rel["table1"], rel["table2"]],
                "join_type": "INNER JOIN",  # Default to INNER JOIN
                "join_condition": self._format_join_condition(rel),
                "reasoning": f"Join based on {rel['relationship_type']} relationship",
            }
            strategies.append(strategy)

        return strategies

    def _format_join_condition(self, relationship: Dict) -> str:
        """Format the join condition SQL."""
        table1, table2 = relationship["table1"], relationship["table2"]
        join_columns = relationship["join_columns"]

        conditions = []
        for col1, col2 in join_columns:
            conditions.append(f"{table1}.{col1} = {table2}.{col2}")

        return " AND ".join(conditions)

    def _find_join_path(
        self, table1: str, table2: str, catalog: Catalog
    ) -> Optional[Dict]:
        """Find join path between two specific tables."""
        # This is a simplified implementation
        # In a real system, you might use graph algorithms to find optimal join paths

        table1_obj = self._find_table_by_name(table1, catalog)
        table2_obj = self._find_table_by_name(table2, catalog)

        if not table1_obj or not table2_obj:
            return None

        relationship = self._find_relationship(table1_obj, table2_obj)
        if relationship:
            return {
                "table1": table1,
                "table2": table2,
                "join_sql": f"JOIN {table2} ON {self._format_join_condition({'table1': table1, 'table2': table2, 'join_columns': relationship['columns']})}",
                "confidence": relationship["confidence"],
            }

        return None

    def _find_table_by_name(self, table_name: str, catalog: Catalog) -> Optional[Table]:
        """Find a table by name in the catalog."""
        for schema in catalog.schemas:
            for table in schema.tables:
                if table.table_name == table_name:
                    return table
        return None

    def _explain_table_relevance(self, table: Table, entities: List[str]) -> str:
        """Explain why a table is relevant."""
        reasons = []

        table_name_lower = table.table_name.lower()
        for entity in entities:
            if entity in table_name_lower:
                reasons.append(f"Table name contains '{entity}'")

        matching_columns = []
        for column in table.columns:
            for entity in entities:
                if entity in column.name.lower():
                    matching_columns.append(column.name)

        if matching_columns:
            reasons.append(f"Columns match entities: {', '.join(matching_columns[:3])}")

        return "; ".join(reasons) if reasons else "General relevance"

    def _calculate_confidence(
        self, relevant_tables: List[Dict], entities: List[str]
    ) -> float:
        """Calculate overall confidence in the schema linking results."""
        if not relevant_tables:
            return 0.0

        # Base confidence on number of relevant tables and their scores
        total_score = sum(table["score"] for table in relevant_tables)
        avg_score = total_score / len(relevant_tables)

        # Normalize to 0-1 range
        confidence = min(avg_score / 10.0, 1.0)

        return round(confidence, 2)

    def generate_initial_sql(self, user_query: str, table_name: str) -> str:
        schema_profile = self.datasource.profile_table(table_name)
        schema_nl = self.summarizer.summarize_schema(schema_profile)
        prompt = f"""Given the user question and metadata summaries, write a SQL query.

Question: {user_query}

"""
        for col, desc in schema_nl.items():
            prompt += f"Column: {col}\nDescription: {desc}\n"

        prompt += "\nSQL:"
        return self.chat(prompt).content

    def extract_literals_and_columns(self, sql: str) -> Dict[str, list]:
        import re

        import sqlparse

        tokens = sqlparse.parse(sql)[0].tokens
        [t.value for t in tokens if t.ttype is None and str(t).strip()]
        literals = re.findall(r"'(.*?)'", sql)
        columns = re.findall(r"\b\w+\b", sql)
        return {"columns": list(set(columns)), "literals": literals}

    def refine_sql(self, user_query: str, table_name: str, max_iter: int = 2) -> str:
        current_sql = self.generate_initial_sql(user_query, table_name)
        extracted = self.extract_literals_and_columns(current_sql)

        for _ in range(max_iter):
            # Match literals to other columns
            extended_cols = set(extracted["columns"])
            schema_profile = self.datasource.profile_table(table_name)
            for col, stats in schema_profile.items():
                sample_values = stats.get("sample_values", [])
                if any(
                    lit in str(v)
                    for v in sample_values
                    for lit in extracted["literals"]
                ):
                    extended_cols.add(col)

            prompt = f"""
Update SQL to include additional relevant columns:

User Query: {user_query}
Detected Columns: {list(extended_cols)}
Literals: {extracted["literals"]}

Original SQL: {current_sql}

Improved SQL:
"""
            current_sql = self.chat(prompt).content
            extracted = self.extract_literals_and_columns(current_sql)

        return current_sql

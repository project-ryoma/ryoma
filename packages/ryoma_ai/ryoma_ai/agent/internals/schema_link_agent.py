from typing import Dict

from ryoma_ai.agent.chat_agent import ChatAgent
from ryoma_ai.datasource.base import DataSource


class SchemaLinkingAgent(ChatAgent):
    def __init__(self,
                 *args,
                 datasource: DataSource,
                 summarizer,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.datasource = datasource
        self.summarizer = summarizer

    def generate_initial_sql(self,
                             user_query: str,
                             table_name: str) -> str:
        schema_profile = self.datasource.profile_table(table_name)
        schema_nl = self.summarizer.summarize_schema(schema_profile)
        prompt = f"""Given the user question and metadata summaries, write a SQL query.

Question: {user_query}

"""
        for col, desc in schema_nl.items():
            prompt += f"Column: {col}\nDescription: {desc}\n"

        prompt += "\nSQL:"
        return self.chat(prompt).content

    def extract_literals_and_columns(self,
                                     sql: str) -> Dict[str, list]:
        import sqlparse
        import re
        tokens = sqlparse.parse(sql)[0].tokens
        identifiers = [t.value for t in tokens if t.ttype is None and str(t).strip()]
        literals = re.findall(r"'(.*?)'", sql)
        columns = re.findall(r"\b\w+\b", sql)
        return {"columns": list(set(columns)), "literals": literals}

    def refine_sql(self,
                   user_query: str,
                   table_name: str,
                   max_iter: int = 2) -> str:
        current_sql = self.generate_initial_sql(user_query, table_name)
        extracted = self.extract_literals_and_columns(current_sql)

        for _ in range(max_iter):
            # Match literals to other columns
            extended_cols = set(extracted["columns"])
            schema_profile = self.datasource.profile_table(table_name)
            for col, stats in schema_profile.items():
                sample_values = stats.get("sample_values", [])
                if any(lit in str(v) for v in sample_values for lit in extracted["literals"]):
                    extended_cols.add(col)

            prompt = f"""
Update SQL to include additional relevant columns:

User Query: {user_query}
Detected Columns: {list(extended_cols)}
Literals: {extracted['literals']}

Original SQL: {current_sql}

Improved SQL:
"""
            current_sql = self.chat(prompt).content
            extracted = self.extract_literals_and_columns(current_sql)

        return current_sql

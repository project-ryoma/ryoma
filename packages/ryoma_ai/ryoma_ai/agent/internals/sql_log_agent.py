from typing import List, Dict

from ryoma_ai.agent.chat_agent import ChatAgent


class SQLLogToNLAgent(ChatAgent):
    def __init__(self,
                 *args,
                 datasource,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.datasource = datasource

    def generate_nl_from_sql(self,
                             sql: str,
                             table_name: str) -> str:
        profile = self.datasource.profile_table(table_name)
        schema_desc = "\n".join(
            f"{col}: {desc}" for col, desc in profile.items()
        )

        prompt = f"""
Given the following SQL query and table column descriptions, write a natural language question that would generate this query.

Table: {table_name}
Schema:
{schema_desc}

SQL:
{sql}

Question:
"""
        return self.chat(prompt).content

    def process_sql_logs(self,
                         sql_log: List[str],
                         table_name: str) -> List[Dict[str, str]]:
        return [
            {
                "sql": sql,
                "question": self.generate_nl_from_sql(sql, table_name),
            }
            for sql in sql_log
        ]

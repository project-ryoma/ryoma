import os
import pandas as pd
from ryoma_ai.agent.pandas_agent import PandasAgent
from ryoma_ai.agent.workflow import ToolMode
from ryoma_ai.datasource.postgres import PostgresDataSource


def get_postgres_datasource():
    return PostgresDataSource(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", 5432),
        database=os.getenv("POSTGRES_DB", "postgres"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        db_schema=os.getenv("POSTGRES_SCHEMA", "public"),
    )


postgres_db = get_postgres_datasource()
pandas_agent = PandasAgent("gpt-3.5-turbo")
df = pd.DataFrame(
    {
        "artist": ["Artist A", "Artist B", "Artist C", "Artist A", "Artist B"],
        "album": ["Album 1", "Album 2", "Album 3", "Album 4", "Album 5"],
    }
)
pandas_agent.add_dataframe(df)
pandas_agent.invoke("show me the artits with the most albums in descending order")
pandas_agent.invoke(tool_mode=ToolMode.ONCE)

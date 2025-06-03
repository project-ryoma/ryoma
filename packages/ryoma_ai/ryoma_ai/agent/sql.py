from typing import Dict, Optional, Union

from langchain_core.embeddings import Embeddings
from ryoma_ai.agent.workflow import WorkflowAgent
from ryoma_ai.datasource.base import DataSource
from ryoma_ai.tool.sql_tool import CreateTableTool, QueryProfileTool, SqlQueryTool
from ryoma_ai.vector_store.base import VectorStore


class SqlAgent(WorkflowAgent):
    description: str = (
        "A SQL agent that can use SQL Tools to interact with SQL schemas."
    )

    def __init__(
        self,
        model: str,
        model_parameters: Optional[Dict] = None,
        datasource: Optional[DataSource] = None,
        embedding: Optional[Union[dict, Embeddings]] = None,
        vector_store: Optional[Union[dict, VectorStore]] = None,
        **kwargs,
    ):
        super().__init__(
            [SqlQueryTool(), CreateTableTool(), QueryProfileTool()],
            model,
            model_parameters,
            datasource=datasource,
            embedding=embedding,
            vector_store=vector_store,
        )

from typing import Dict

import pyarrow as pa

from aita.agent.base import AitaAgent
from aita.tool.pyarrow_tool import ArrowTool


class PyArrowAgent(AitaAgent):

    prompt_context = """
    Meta data of all available data source as pyarrow table:
    {script_context}
    """

    def __init__(self, tables: Dict[str, pa.Table], model_id: str, model_parameters: Dict = None):
        tool = ArrowTool(script_context=tables)
        table_metadata = []
        for name, table in tables.items():
            table_metadata.append({"name": name, "schema": table.schema})
        self.prompt_context = self.prompt_context.format(script_context=tables)
        super().__init__(model_id, model_parameters, [tool], prompt_context=self.prompt_context)

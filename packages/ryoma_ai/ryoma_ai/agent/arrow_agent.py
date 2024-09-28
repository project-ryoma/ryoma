from typing import Dict

import pyarrow as pa
from ryoma_ai.agent.workflow import WorkflowAgent
from ryoma_ai.tool.pyarrow_tool import ArrowTool
from ryoma_ai.tool.python_tool import PythonTool


class ArrowAgent(WorkflowAgent):
    description: str = (
        "An Arrow agent that can use Arrow tools to interact with Arrow Tables."
    )

    def __init__(self, model: str, model_parameters: Dict = None):
        super().__init__([ArrowTool()], model, model_parameters)

    def add_table(self, table: pa.Table):
        table_id = f"table_{id(table)}"
        self.add_prompt_context(
            f"""
        pyarrow table name: {table_id}
        pyarrow table metadata: {table.schema}
        """
        )
        for tool in self.tools:
            if isinstance(tool, PythonTool):
                tool.update_script_context(script_context={table_id: table})
        return self

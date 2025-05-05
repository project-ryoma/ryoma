import io
from typing import Dict, Optional

from pandas import DataFrame
from ryoma_ai.agent.workflow import WorkflowAgent
from ryoma_ai.tool.pandas_tool import PandasTool
from ryoma_ai.tool.python_tool import PythonTool


class PandasAgent(WorkflowAgent):
    description: str = (
        "A pandas agent that can use pandas tools to interact with pandas DataFrames."
    )

    def __init__(self,
                 model: str,
                 model_parameters: Dict = None):
        super().__init__(
            [
                PandasTool(),
            ],
            model,
            model_parameters,
        )

    def add_dataframe(
        self,
        dataframe: DataFrame,
        df_id: Optional[str] = None,
    ) -> "PandasAgent":
        """
        Register a DataFrame as a resource, update the prompt context and tool script context.

        Args:
            dataframe: The pandas DataFrame to register.
            df_id: Optional custom name for the DataFrame.

        Returns:
            self (for chaining)
        """
        # Register DataFrame in the agent's registry
        obj_id = self.register_resource(dataframe)
        df_name = df_id or f"df_{obj_id}"

        # Add prompt context (note: dataframe.info() prints, we capture as string)
        buffer = io.StringIO()
        dataframe.info(buf=buffer)
        metadata_str = buffer.getvalue()

        self.add_prompt_context(
            f"""
            dataframe name: {df_name}
            dataframe metadata:\n{metadata_str}
            """
        )

        # Inject into PythonTool script context
        for tool in self.tools:
            if isinstance(tool, PythonTool):
                tool.update_script_context(script_context={df_name: dataframe})

        return self

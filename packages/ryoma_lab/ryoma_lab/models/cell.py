from typing import Any, Callable, Coroutine, List, Literal, Optional, Union

import pandas as pd
import reflex as rx


class CellOutput(rx.Base):
    output_type: Literal["stream", "execute_result", "dataframe", "error"]
    ename: str = ""
    evalue: str = ""
    traceback: str = ""


class DataframeOutput(CellOutput):
    output_type: Literal["stream", "execute_result", "dataframe", "error"] = "dataframe"
    dataframe: pd.DataFrame


class StreamOutput(CellOutput):
    output_type: Literal["stream", "execute_result", "dataframe", "error"] = "stream"
    text: str


class ExecuteResultOutput(CellOutput):
    output_type: Literal["stream", "execute_result", "dataframe", "error"] = (
        "execute_result"
    )
    execute_result: Union[dict[str, Any], None] = None


class ErrorOutput(CellOutput):
    output_type: Literal["stream", "execute_result", "dataframe", "error"] = "error"


class UnknownOutput(ErrorOutput):
    text: str = "Unknown output type"


class Cell(rx.Base):
    cell_type: str = "code"
    content: str = ""
    output: List[
        Union[
            StreamOutput,
            ExecuteResultOutput,
            DataframeOutput,
            ErrorOutput,
            UnknownOutput,
        ]
    ] = []
    tool_id: Optional[str] = None
    execute_function: Optional[Callable[[str, str], Coroutine[Any, Any, None]]] = None
    update_function: Optional[Callable[[str, str], None]] = None

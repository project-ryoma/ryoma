from typing import Any, Callable, Coroutine, List, Optional, Union, Literal

import reflex as rx
import pandas as pd


class CellOutput(rx.Base):
    output_type: Literal["stream", "execute_result", "dataframe", "error"]
    text: Optional[str] = None
    data: Optional[Union[dict, pd.DataFrame]] = None
    ename: Optional[str] = None
    evalue: Optional[str] = None
    traceback: Optional[str] = None


class Cell(rx.Base):
    cell_type: Literal["code", "markdown"] = "code"
    content: str = ""
    output: List[CellOutput] = []
    tool_id: Optional[str] = None
    execute_function: Optional[Callable[[str, str], Coroutine[Any, Any, None]]] = None
    update_function: Optional[Callable[[str, str], None]] = None

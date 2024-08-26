import logging
import sys
from io import StringIO
from typing import Any, Dict, List, Literal, Optional

import reflex as rx
from IPython.core.displaypub import DisplayPublisher
from IPython.core.interactiveshell import InteractiveShell

from ryoma_lab.models.tool import Tool


class CellOutput(rx.Base):
    output_type: Literal["stream", "execute_result", "error"]
    text: Optional[str] = None
    data: Optional[dict] = None
    ename: Optional[str] = None
    evalue: Optional[str] = None


class Cell(rx.Base):
    cell_type: Literal["code", "markdown"] = "code"
    content: str = ""
    output: List[CellOutput] = []


class NotebookState(rx.State):
    cells: List[Cell] = [Cell()]
    kernel: str = "Python 3"
    namespace: dict = {}

    def data_contains_html(self, item: CellOutput) -> bool:
        return item.data & item.data.contains("text/html")

    def get_html_content(self, item: CellOutput) -> str:
        return (
            item.data["text/html"]
            if item.data & item.data.contains("text/html")
            else ""
        )

    def data_contains_image(self, item: CellOutput) -> bool:
        return item.data and item.data.contains("image/png")

    def get_image_content(self, item: CellOutput) -> str:
        return (
            item.data["image/png"]
            if item.data & item.data.contains("image/png")
            else ""
        )

    def get_plain_text_content(self, item: CellOutput) -> str:
        if item.data & item.data.contains("text/plain"):
            return str(item.data["text/plain"])
        else:
            return ""

    def get_ipython_shell(self):
        shell = InteractiveShell.instance()
        shell.display_pub = NotebookDisplayPublisher(self)
        return shell

    def run_cell(self, index: int):
        logging.info(f"Running cell {index}")
        cell = self.cells[index]
        if cell.cell_type == "code":
            old_stdout = sys.stdout
            redirected_output = StringIO()
            sys.stdout = redirected_output

            try:
                # Clear previous output
                cell.output = []

                # Get a fresh IPython shell for this execution
                ipython_shell = self.get_ipython_shell()

                # Execute the cell
                result = ipython_shell.run_cell(cell.content, store_history=False)

                # Capture stdout
                stdout = redirected_output.getvalue()
                if stdout:
                    cell.output.append(CellOutput(output_type="stream", text=stdout))

                # Handle execution result
                if result.result is not None:
                    cell.output.append(
                        CellOutput(
                            output_type="execute_result",
                            data={"text/plain": str(result.result)},
                        )
                    )

                if result.error_before_exec or result.error_in_exec:
                    cell.output.append(
                        CellOutput(
                            output_type="error",
                            ename=type(result.error_in_exec).__name__,
                            evalue=str(result.error_in_exec),
                        )
                    )

            finally:
                sys.stdout = old_stdout
        else:
            # Markdown cell
            cell.output.append(
                CellOutput(
                    output_type="execute_result", data={"text/plain": cell.content}
                )
            )

        self.cells[index] = cell

    def clear_all_outputs(self):
        for cell in self.cells:
            cell.output = []
        self.namespace = {}  # Reset the namespace

    def restart_kernel(self):
        self.clear_all_outputs()
        self.namespace = {}  # Reset the namespace

    def add_tool_cell(self, tool: Tool):
        content = f"# Tool: {tool.name}\n"
        for arg in tool.args:
            content += f"{arg.name} = {arg.value}\n"
        new_cell = Cell(content=content)
        self.cells = [*self.cells, new_cell]  # Create a new list to trigger update

        # Log for debugging
        logging.info(f"Added new tool cell: {new_cell}")
        logging.info(f"Total cells after adding: {len(self.cells)}")

    def delete_cell(self, index: int):
        if len(self.cells) > 1:
            self.cells.pop(index)
        else:
            # If it's the last cell, clear its content instead of deleting
            self.cells[0] = Cell()

    def add_cell(self):
        self.cells.append(Cell())

    def add_cell_at(self, index: int, position: str):
        if position == "before":
            self.cells.insert(index, Cell())
        elif position == "after" or position == "only":
            self.cells.insert(index + 1, Cell())

    def set_cell_type(self, index: int, cell_type: str):
        self.cells[index].cell_type = cell_type

    def update_cell_content(self, index: int, content: str):
        self.cells[index].content = content

    def set_kernel(self, kernel: str):
        self.kernel = kernel

    def run_all_cells(self):
        for index in range(len(self.cells)):
            self.run_cell(index)

    def on_load(self):
        # Initialize with an empty cell if there are no cells
        if not self.cells:
            self.add_cell()


class NotebookDisplayPublisher(DisplayPublisher):
    def __init__(self, state):
        super().__init__()
        self.state = state

    def publish(self, data, metadata=None, source=None):
        current_cell = self.state.cells[-1]
        current_cell.output.append(CellOutput(output_type="display_data", data=data))
        self.state.cells[-1] = current_cell

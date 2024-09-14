import logging
from typing import Any, Callable, Coroutine, List, Optional

import reflex as rx
from feast import FeatureStore
from IPython.core.displaypub import DisplayPublisher
from IPython.core.interactiveshell import InteractiveShell

from ryoma_ai.datasource.base import DataSource
from ryoma_lab.models.cell import Cell, CellOutput
from ryoma_lab.models.data_catalog import CatalogTable, SchemaTable
from ryoma_lab.models.tool import Tool
from ryoma_lab.services.catalog import CatalogService
from ryoma_lab.services.file_manager import FileManager, FileNode
from ryoma_lab.services.kernel.base import BaseKernel
from ryoma_lab.services.kernel.factory import KernelFactory
from ryoma_lab.states.base import BaseState
from ryoma_lab.states.datasource import DataSourceState


class WorkspaceState(BaseState):
    _current_store: Optional[FeatureStore] = None

    # datasource and catalog state
    current_catalog_name: str = ""
    current_schema_name: str = ""
    catalogs: list[CatalogTable] = []
    schemas: list[SchemaTable] = []
    catalog_dialog_open: bool = False
    schema_dialog_open: bool = False

    # notebook state
    cells: List[Cell] = [Cell()]
    kernel_type: str = "sql"
    kernel: BaseKernel = None
    namespace: dict = {}
    file_manager: FileManager = FileManager(base_directory=".")
    directory_structure: FileNode = FileNode(name="Root", is_dir=True)
    sidebar_width: str = "250px"
    is_sidebar_open: bool = True
    notebook_filename: str = "notebook.ipynb"

    def set_catalog_name(self, catalog_name: str):
        if catalog_name == "custom":
            return rx.redirect("/datasource")
        if not self.current_catalog_name or self.current_catalog_name != catalog_name:
            self.current_catalog_name = catalog_name
            self.schema_dialog_open = True
            self.schemas = self.current_catalog.schemas

            datasource = self._connect_datasource(self.current_catalog.datasource)
            self.kernel.set_datasource(datasource)

    def _connect_datasource(self, datasource_name: str) -> DataSource:
        return DataSourceState.connect(datasource_name)

    def toggle_catalog_dialog(self, is_open: bool):
        self.catalog_dialog_open = is_open

    def toggle_schema_dialog(self, is_open: bool):
        self.schema_dialog_open = is_open

    @rx.var
    def current_catalog(self) -> Optional[CatalogTable]:
        if not self.current_catalog_name:
            return None
        res = next(
            (
                catalog
                for catalog in self.catalogs
                if catalog.catalog_name == self.current_catalog_name
            ),
            None,
        )
        return res

    def set_current_schema_name(self, schema_name: str):
        self.current_schema_name = schema_name

    def toggle_sidebar(self):
        self.is_sidebar_open = not self.is_sidebar_open
        if self.is_sidebar_open:
            self.sidebar_width = "250px"
        else:
            self.sidebar_width = "60px"

    @rx.var
    def file_list(self) -> List[FileNode]:
        return self.file_manager.list_directory()

    def is_dataframe(self, item: CellOutput) -> bool:
        return item.data & item.output_type == "dataframe"

    def data_contains_html(self, item: CellOutput) -> bool:
        return item.data & item.data.contains("text/html")

    def get_html_content(self, item: CellOutput) -> str:
        return (
            item.data["text/html"]
            if item.data & item.data.contains("text/html")
            else ""
        )

    def data_contains_image(self, item: CellOutput) -> bool:
        return item.data & item.data.contains("image/png")

    def get_image_content(self, item: CellOutput) -> str:
        return (
            item.data["image/png"]
            if item.data & item.data.contains("image/png")
            else ""
        )

    def get_plain_text_content(self, item: CellOutput) -> str:
        if item.data & item.data.contains("text/plain"):
            return str(item.data["text/plain"])
        return ""

    def get_ipython_shell(self):
        shell = InteractiveShell.instance()
        shell.display_pub = NotebookDisplayPublisher(self)
        return shell

    def add_tool_cell(
        self,
        tool: Tool,
        execute_function: Callable[[str, str], Coroutine[Any, Any, None]],
        update_function: Callable[[str, str], None],
    ):
        cell_content = f"# Tool: {tool.name}\n"
        for arg in tool.args:
            cell_content += f"{arg.name} = {arg.value}\n"

        new_cell = Cell(
            cell_type="code",
            content=cell_content,
            tool_id=tool.id,
            execute_function=execute_function,
            update_function=update_function,
        )
        self.cells.append(new_cell)

    @rx.background
    async def execute_cell(self, cell_index: int):
        if 0 <= cell_index < len(self.cells):
            async with self:
                result = await self.kernel.execute_code(self.cells[cell_index].content)
                logging.info(result)
                self.cells[cell_index].output = [CellOutput(**result)]

    def clear_all_outputs(self):
        for cell in self.cells:
            cell.output = []

    def restart_kernel(self):
        self.clear_all_outputs()
        self.namespace = {}

    def set_kernel_type(self, kernel_type: str):
        if kernel_type not in ["python", "sql"]:
            raise ValueError(f"Unsupported kernel type: {kernel_type}")
        self.kernel_type = kernel_type
        self._create_kernel()

    def add_cell(self):
        self.cells.append(Cell())

    def add_cell_at(self, index: int, position: str):
        if position == "before":
            self.cells.insert(index, Cell())
        elif position == "after":
            self.cells.insert(index + 1, Cell())
        elif position == "only":
            self.cells = [Cell()]

    @rx.background
    async def update_cell_content(self, cell_index: int, content: str):
        async with self:
            if 0 <= cell_index < len(self.cells):
                self.cells[cell_index].content = content

    def set_cell_type(self, index: int, cell_type: str):
        if cell_type not in ["code", "markdown"]:
            raise ValueError(f"Unsupported cell type: {cell_type}")
        self.cells[index].cell_type = cell_type

    def run_all_cells(self):
        for index in range(len(self.cells)):
            self.execute_cell(index)

    def delete_cell(self, index: int):
        if 0 <= index < len(self.cells):
            self.cells.pop(index)

    def save_notebook(self):
        if self.notebook_filename:
            cells_data = [cell.dict() for cell in self.cells]
            self.file_manager.save_notebook(self.notebook_filename, cells_data)

    def load_notebook(self):
        if self.notebook_filename:
            cells_data = self.file_manager.load_notebook(self.notebook_filename)
            self.cells = [Cell(**cell_data) for cell_data in cells_data]

    def set_notebook_filename(self, filename: str):
        self.notebook_filename = filename

    def open_file_or_directory(self, file: FileNode):
        if file["is_dir"]:
            self.directory_structure = file
        else:
            self.notebook_filename = file["name"]
            self.load_notebook()

    @rx.background
    async def execute_cell(self, cell_index: int):
        if 0 <= cell_index < len(self.cells):
            async with self:
                result = await self.kernel.execute_code(self.cells[cell_index].content)
                logging.info(result)
                self.cells[cell_index].output = [CellOutput(**result)]

    @rx.background
    async def update_cell_content(self, cell_index: int, content: str):
        async with self:
            if 0 <= cell_index < len(self.cells):
                self.cells[cell_index].content = content

    def _create_kernel(self, **kwargs):
        if self.current_catalog:
            datasource = DataSourceState.connect(self.current_catalog.datasource_name)
        else:
            datasource = None
        self.kernel = KernelFactory.create_kernel(
            self.kernel_type, datasource, **kwargs
        )

    def load_workspaces(self):
        with CatalogService() as catalog_service:
            self.catalogs = catalog_service.load_catalogs()
        if not self.cells:
            self.add_cell_at(0, "only")

    def on_load(self) -> None:
        self.load_workspaces()


class NotebookDisplayPublisher(DisplayPublisher):
    def __init__(self, state):
        super().__init__()
        self.state = state

    def publish(self, data, metadata=None, source=None):
        current_cell = self.state.cells[-1]
        current_cell.output.append(CellOutput(output_type="display_data", data=data))
        self.state.cells[-1] = current_cell

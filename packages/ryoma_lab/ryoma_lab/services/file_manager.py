import os
from typing import Any, Dict, List, Optional

import nbformat
import reflex as rx
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook


class FileNode(rx.Base):
    name: str
    is_dir: bool


class FileManager(rx.Base):
    base_directory: str

    def __init__(
        self,
        base_directory: str,
    ):
        super().__init__(base_directory=base_directory)
        self.base_directory = os.path.abspath(base_directory)

    def change_directory(self, directory: str):
        self.base_directory = os.path.join(self.base_directory, directory)

    def list_directory(self, prefix: str = "") -> List[FileNode]:
        items = []
        for item in os.listdir(self.base_directory):
            item_path = os.path.join(self.base_directory, item)
            is_dir = os.path.isdir(item_path)
            if prefix and not item.startswith(prefix):
                continue
            items.append(FileNode(name=item, is_dir=is_dir))
        return items

    def read_file(self, filename: str) -> List[Dict[str, Any]]:
        full_path = os.path.join(self.base_directory, filename)
        if not os.path.exists(full_path) or not os.path.isfile(full_path):
            raise FileNotFoundError(f"File not found: {filename}")
        if filename.endswith(".ipynb"):
            return self.read_notebook(full_path)
        elif filename.endswith(".py"):
            return self.read_python_file(full_path)
        else:
            raise ValueError(f"Unsupported file type: {filename}")

    def save_notebook(self, filename: str, cells: List[Dict[str, Any]]):
        nb = new_notebook()
        for cell in cells:
            if cell["cell_type"] == "code":
                nb_cell = new_code_cell(cell["content"])
                for output in cell.get("output", []):
                    if output["output_type"] == "stream":
                        nb_cell.outputs.append(
                            nbformat.v4.new_output(
                                "stream", name="stdout", text=output["text"]
                            )
                        )
                    elif output["output_type"] == "execute_result":
                        nb_cell.outputs.append(
                            nbformat.v4.new_output(
                                "execute_result", data=output["data"]
                            )
                        )
                    elif output["output_type"] == "error":
                        nb_cell.outputs.append(
                            nbformat.v4.new_output(
                                "error", ename=output["ename"], evalue=output["evalue"]
                            )
                        )
            else:
                nb_cell = new_markdown_cell(cell["content"])
            nb.cells.append(nb_cell)

        full_path = os.path.join(self.base_directory, filename)
        with open(full_path, "w") as f:
            nbformat.write(nb, f)

    @staticmethod
    def read_notebook(full_path: str) -> List[Dict[str, Any]]:
        with open(full_path) as f:
            nb = nbformat.read(f, as_version=4)

        cells = []
        for nb_cell in nb.cells:
            cell = {
                "cell_type": nb_cell.cell_type,
                "content": nb_cell.source,
                "output": [],
            }
            if nb_cell.cell_type == "code" and hasattr(nb_cell, "outputs"):
                for output in nb_cell.outputs:
                    if output.output_type == "stream":
                        cell["output"].append(
                            {"output_type": "stream", "text": output.text}
                        )
                    elif output.output_type == "execute_result":
                        cell["output"].append(
                            {"output_type": "execute_result", "data": output.data}
                        )
                    elif output.output_type == "error":
                        cell["output"].append(
                            {
                                "output_type": "error",
                                "ename": output.ename,
                                "evalue": output.evalue,
                            }
                        )
            cells.append(cell)
        return cells

    @staticmethod
    def read_python_file(full_path: str) -> List[Dict[str, Any]]:
        with open(full_path) as f:
            file_content = f.read()
        return [
            {
                "cell_type": "code",
                "content": file_content,
            }
        ]

    def get_directory_structure(self) -> List[Dict[str, Any]]:
        structure = []
        for root, dirs, files in os.walk(self.base_directory):
            rel_path = os.path.relpath(root, self.base_directory)
            if rel_path == ".":
                structure.extend([{"directory": d, "files": []} for d in dirs])
                structure.append({"directory": "Root", "files": files})
            else:
                for item in structure:
                    if item["directory"] == os.path.dirname(rel_path):
                        item["files"].extend(files)
                        break
        return structure

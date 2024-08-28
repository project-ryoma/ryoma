import os
from typing import Any, Dict, List

import reflex as rx


class FileNode(rx.Base):
    name: str
    is_dir: bool


class FileManager(rx.Base):
    base_directory: str

    def __init__(self, base_directory: str):
        super().__init__(base_directory=base_directory)
        self.base_directory = os.path.abspath(base_directory)

    def list_directory(self, path: str = "") -> List[FileNode]:
        full_path = os.path.join(self.base_directory, path)
        if not os.path.exists(full_path) or not os.path.isdir(full_path):
            return []

        items = []
        for item in os.listdir(full_path):
            item_path = os.path.join(full_path, item)
            is_dir = os.path.isdir(item_path)
            items.append(FileNode(name=item, is_dir=is_dir))

        return items

    def read_file(self, filename: str) -> str:
        full_path = os.path.join(self.base_directory, filename)
        if not os.path.exists(full_path) or not os.path.isfile(full_path):
            return ""

        with open(full_path, "r") as f:
            return f.read()

    def save_file(self, filename: str, content: str):
        full_path = os.path.join(self.base_directory, filename)
        with open(full_path, "w") as f:
            f.write(content)

    def delete_file(self, filename: str):
        full_path = os.path.join(self.base_directory, filename)
        if os.path.exists(full_path) and os.path.isfile(full_path):
            os.remove(full_path)

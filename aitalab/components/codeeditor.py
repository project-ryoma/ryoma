from typing import Optional

import reflex as rx


class CodeEditor(rx.Component):
    library = "@uiw/react-codemirror"

    lib_dependencies: list[str] = ["@codemirror/language"]

    tag = "CodeEditor"

    is_default = True

    value: rx.Var[str]

    extension: rx.Var[dict]
    on_change: rx.EventHandler[lambda value: [value]]


code_editor = CodeEditor.create

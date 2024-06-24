import reflex as rx


class CodeEditor(rx.Component):
    library = "@uiw/react-codemirror"

    lib_dependencies: list[str] = ["@uiw/codemirror-extensions-langs"]

    tag = "CodeEditor"

    is_default = True

    value: rx.Var[str]

    height: rx.Var[str]

    extension: rx.Var[dict]
    on_change: rx.EventHandler[lambda value: [value]]


code_editor = CodeEditor.create

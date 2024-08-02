import reflex as rx


class CodeEditor(rx.Component):
    library = "@uiw/react-codemirror"

    lib_dependencies: list[str] = ["@uiw/codemirror-extensions-langs"]

    tag = "CodeEditor"

    is_default = True

    value: rx.Var[str]

    height: rx.Var[str]

    minHeight: rx.Var[str]

    width: rx.Var[str]

    minWidth: rx.Var[str]

    theme: rx.Var[str]

    extensions: rx.Var[str] = rx.Var.create('[loadLanguage("sql"), loadLanguage("python")]', _var_is_local=False),
    on_change: rx.EventHandler[lambda value: [value]]

    def add_imports(self):
        return {"@uiw/codemirror-extensions-langs": "loadLanguage"}


code_editor = CodeEditor.create

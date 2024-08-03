import reflex as rx


class ReactCodeEditor(rx.Component):
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

    extensions: rx.Var[str]
    on_change: rx.EventHandler[lambda value: [value]]

    def add_imports(self):
        return {"@uiw/codemirror-extensions-langs": "loadLanguage"}


react_code_editor = ReactCodeEditor.create


class CodeEditor(rx.ComponentState):
    value: str = ""
    height: str = "100%"
    min_height: str = "20em"
    width: str = "100%"
    min_width: str = "100%"
    theme: str = "light"
    extensions: str = (
        rx.Var.create(
            '[loadLanguage("sql"), loadLanguage("python")]',
            _var_is_string=True,
            _var_is_local=False,
        ),
    )

    @classmethod
    def get_component(cls, **props) -> "Component":
        value = props.pop("value", cls.value)
        height = props.pop("height", cls.height)
        min_height = props.pop("min_height", cls.min_height)
        width = props.pop("width", cls.width)
        min_width = props.pop("min_width", cls.min_width)
        theme = props.pop("theme", cls.theme)
        extensions = props.pop("extensions", cls.extensions)
        on_change = props.pop("on_change", cls.set_value)

        return react_code_editor(
            value=value,
            height=height,
            minHeight=min_height,
            width=width,
            minWidth=min_width,
            theme=theme,
            extensions=extensions,
            on_change=on_change,
        )


codeeditor = CodeEditor.create

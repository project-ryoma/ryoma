import inspect

from aita import tool


def get_tool_classes() -> list:
    return inspect.getmembers(tool, inspect.isclass)

from aita import tool

import inspect


def get_tool_classes() -> list:
    return inspect.getmembers(tool, inspect.isclass)


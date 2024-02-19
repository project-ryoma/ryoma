from typing import Any, Callable, Dict

from functools import wraps

from pydantic import validate_arguments


def _remove_a_key(d: Dict[Any, Any], remove_key: Any) -> None:
    """Remove a key from a dictionary recursively"""
    for key in list(d.keys()):
        if key == remove_key:
            del d[key]
        elif isinstance(d[key], dict):
            _remove_a_key(d[key], remove_key)


class openai_function:
    """
    Decorator to convert a function into an OpenAI function.

    This decorator will convert a function into an OpenAI function. The
    function will be validated using pydantic and the schema will be
    generated from the function signature.

    Example:
        ```python
        @openai_function
        def sum(a: int, b: int) -> int:
            return a + b

        completion = openai.ChatCompletion.create(
            ...
            messages=[{
                "content": "What is 1 + 1?",
                "role": "user"
            }]
        )
        sum.from_response(completion)
        # 2
        ```
    """

    def __init__(self, func: Callable[..., Any]) -> None:
        self.func = func
        self.validate_func = validate_arguments(func)
        parameters = self.validate_func.model.model_json_schema()
        parameters["properties"] = {
            k: v
            for k, v in parameters["properties"].items()
            if k not in ("v__duplicate_kwargs", "args", "kwargs")
        }
        parameters["required"] = sorted(
            k for k, v in parameters["properties"].items() if not "default" in v
        )
        _remove_a_key(parameters, "additionalProperties")
        _remove_a_key(parameters, "title")
        self.openai_schema = {
            "name": self.func.__name__,
            "description": self.func.__doc__,
            "parameters": parameters,
        }
        self.model = self.validate_func.model

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        @wraps(self.func)
        def wrapper(*args, **kwargs):
            return self.validate_func(*args, **kwargs)

        return wrapper(*args, **kwargs)

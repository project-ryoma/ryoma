import inspect
from typing import Any

from langchain_core.pydantic_v1 import BaseModel


def get_model_classes(model: Any) -> list:
    return inspect.getmembers(model, inspect.isclass)


def get_model_fields(model: BaseModel, field_name: str) -> BaseModel:
    return model.__fields__[field_name].default


def get_model_fields_as_dict(model: BaseModel) -> dict:
    d = {}
    for field, value in model.__fields__.items():
        d[field] = {
            "name": field,
            "required": value.required,
            "description": value.field_info.description,
        }
    return d

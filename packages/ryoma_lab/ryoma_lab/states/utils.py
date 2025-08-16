import inspect
from typing import Any

from langchain_core.pydantic_v1 import BaseModel


def get_model_classes(model: Any) -> list:
    return inspect.getmembers(model, inspect.isclass)


def get_model_fields(model: BaseModel, field_name: str) -> BaseModel:
    return model.__fields__[field_name].default


def get_model_fields_as_dict(model: BaseModel) -> dict:
    d = {}
    for field, value in model.model_fields.items():
        # In Pydantic v1, check if the field is required by checking if default is ... (Ellipsis)
        is_required = value.default is ... if hasattr(value, 'default') else True
        description = value.field_info.description if hasattr(value, 'field_info') and value.field_info else None
        
        d[field] = {
            "name": field,
            "required": is_required,
            "description": description,
        }
    return d

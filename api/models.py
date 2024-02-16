from typing import Union

from pydantic import BaseModel


class Prompt(BaseModel):
    prompt: str


class ConnectionParams(BaseModel):
    host: str
    port: Union[int, None] = None
    user: str
    password: str
    schema: Union[str, None] = None
    database: Union[str, None] = None
    warehouse: Union[str, None] = None
    role: Union[str, None] = None

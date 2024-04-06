from typing import Optional

from pydantic import BaseModel


class DataBase(BaseModel):
    name: str
    description: Optional[str] = None
    connected: bool = True
    connection_url: Optional[str]

    class Config:
        orm_mode = True


class DataBaseCreate(DataBase):
    connection_string: str


class DataBaseUpdate(DataBase):
    connection_string: str


class DataBaseInDBBase(DataBase):
    id: Optional[int] = None

    class Config:
        from_attributes = True


# Additional properties to return via API
class DataBaseResponse(DataBaseInDBBase):
    pass


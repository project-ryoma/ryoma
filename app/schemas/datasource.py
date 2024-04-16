from typing import Optional

from pydantic import BaseModel


class DataSource(BaseModel):
    name: str
    description: Optional[str] = None
    connected: bool = True
    connection_url: Optional[str]

    class Config:
        orm_mode = True


class DataSourceCreate(DataSource):
    connection_string: str


class DataSourceUpdate(DataSource):
    connection_string: str


class DataSourceInDBBase(DataSource):
    id: Optional[int] = None

    class Config:
        from_attributes = True


# Additional properties to return via API
class DataSourceResponse(DataSourceInDBBase):
    pass


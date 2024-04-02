from typing import Optional

from pydantic import BaseModel


class DataSourceBase(BaseModel):
    name: str
    description: Optional[str] = None
    enabled: bool = True
    connection_url: str

    class Config:
        orm_mode = True


class DataSourceConnect(DataSourceBase):
    name: str
    connected: bool = True


class DataSourceDisconnect(DataSourceBase):
    name: str
    connected: bool = False


class DataSourceCreate(DataSourceBase):
    connection_string: Optional[str]


class DataSourceUpdate(DataSourceBase):
    connection_string: Optional[str]


class DataSourceConfig(BaseModel):
    datasource_id: str


class DataSourceConnectResponse(BaseModel):
    status: str
    message: str


class ConnectionParams(BaseModel):
    datasource: str
    host: str
    port: Optional[int]
    user: str
    password: str
    schema: Optional[str]
    database: Optional[str]
    warehouse: Optional[str]
    role: Optional[str]


class DataSourceInDBBase(DataSourceBase):
    id: Optional[int] = None

    class Config:
        from_attributes = True


# Additional properties to return via API
class DataSource(DataSourceInDBBase):
    pass


# Additional properties stored in DB
class DataSourceInDB(DataSourceInDBBase):
    hashed_password: str
from pydantic import BaseModel

class DataSourceBase(BaseModel):
    name: str
    description: Optional[str] = None
    enabled: bool = True

    class Config:
        orm_mode = True


class DataSourceConnect(DataSourceBase):
    name: str
    connection_string: str
    connected: bool = False

  
class DataSourceDisconnect(DataSourceBase):
    name: str
    connected: bool = False
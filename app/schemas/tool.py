from pydantic import BaseModel


class ToolUseRequest(BaseModel):
    name: str
    arguments: dict


class ToolUseResponse(BaseModel):
    status: str
    message: str

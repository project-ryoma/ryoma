from typing import Optional, Dict
from enum import Enum
from pydantic import BaseModel


class ChatRequest(BaseModel):
    prompt: str
    allow_function_calls: bool = False
    agent: str
    model: str
    temperature: float
    datasource_id: Optional[str]


class ChatResponseStatus(Enum):
    success = 'Success'
    error = 'Error'


class AdditionalInfo(BaseModel):
    name: str
    arguments: Dict


class ChatResponse(BaseModel):
    message: str
    status: ChatResponseStatus
    additional_info: Optional[AdditionalInfo] = None


class RunToolRequest(BaseModel):
    agent: str
    name: str
    model: str
    temperature: float
    arguments: Dict


class RunToolResponse(BaseModel):
    message: str
    status: ChatResponseStatus
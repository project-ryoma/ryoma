from typing import Optional
from enum import Enum
from pydantic import BaseModel


class ChatRequest(BaseModel):
    prompt: str
    allow_function_calls: bool = False
    agent: str
    model: str
    temperature: float
    database_id: Optional[str]


class ChatResponseStatus(Enum):
    success = 'Success'
    error = 'Error'


class ChatResponse(BaseModel):
    message: str
    status: ChatResponseStatus
    additional_info: Optional[str] = None

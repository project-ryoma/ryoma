from enum import Enum
from typing import Union, Dict

from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import relationship


class Prompt(BaseModel):
    prompt: str


class ConnectionParams(BaseModel):
    datasource: str
    host: str
    port: Union[int, None] = None
    user: str
    password: str
    schema: Union[str, None] = None
    database: Union[str, None] = None
    warehouse: Union[str, None] = None
    role: Union[str, None] = None


# Shared properties
class UserBase(BaseModel):
    email: EmailStr = Field(unique=True, index=True)
    is_active: bool = True
    is_superuser: bool = False
    full_name: Union[str, None] = None


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str


class UserCreateOpen(BaseModel):
    email: EmailStr
    password: str
    full_name: Union[str, None] = None


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: Union[EmailStr, None] = None
    password: Union[str, None] = None


class UserUpdateMe(BaseModel):
    password: Union[str, None] = None
    full_name: Union[str, None] = None
    email: Union[EmailStr, None] = None


# Database model, database table inferred from class name
class User(UserBase):
    id: Union[int, None] = Field(default=None, primary_key=True)
    hashed_password: str
    items: list["Item"] = relationship("Item", back_populates="owner")


# Properties to return via API, id is always required
class UserOut(UserBase):
    id: int


# Shared properties
class ItemBase(BaseModel):
    title: str
    description: Union[str, None] = None


# Properties to receive on item creation
class ItemCreate(ItemBase):
    title: str


# Properties to receive on item update
class ItemUpdate(ItemBase):
    title: Union[str, None] = None


# Database model, database table inferred from class name
class Item(ItemBase):
    id: Union[int, None] = Field(default=None, primary_key=True)
    title: str
    owner_id: Union[int, None] = Field(default=None, foreign_key="user.id", nullable=False)
    owner: Union[User, None] = relationship("User", back_populates="items")


# Properties to return via API, id is always required
class ItemOut(ItemBase):
    id: int


# Generic message
class Message(BaseModel):
    message: str


# JSON payload containing access token
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(BaseModel):
    sub: Union[int, None] = None


class NewPassword(BaseModel):
    token: str
    new_password: str


class ChatRequest(BaseModel):
    prompt: str
    allow_function_calls: bool = False


class ChatResponseStatus(str, Enum):
    success = 'Success'
    error = 'Error'


class ChatResponse(BaseModel):
    message: str
    status: ChatResponseStatus
    additional_info: Union[Dict, None] = None


class ConnectionResponse(BaseModel):
    pass


class HealthResponse(BaseModel):
    message: str


class ToolUseRequest(BaseModel):
    name: str
    arguments: dict


class ToolUseResponse(BaseModel):
    status: str
    message: str

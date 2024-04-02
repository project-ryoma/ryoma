from typing import Optional

from pydantic import BaseModel


class TokenType(str):
    email = "email"
    oauth = "oauth"


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    sub: Optional[int] = None

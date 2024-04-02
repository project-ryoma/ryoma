from pydantic import BaseModel


class NewPassword(BaseModel):
    token: str
    new_password: str

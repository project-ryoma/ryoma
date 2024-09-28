import reflex as rx
from ryoma_lab.states.base import User


class UserService:

    def __init__(self):
        self.session = rx.session()

    def create_user(
        self, username: str, email: str, hashed_password: str, permissions: dict
    ):
        user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            permissions=permissions,
        )
        self.session.add(user)
        self.session.commit()

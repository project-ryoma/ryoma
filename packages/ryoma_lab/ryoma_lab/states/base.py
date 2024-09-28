"""Base state for the app."""

from typing import List, Optional

import reflex as rx
from fastapi_users.db import (
    SQLAlchemyBaseOAuthAccountTableUUID,
    SQLAlchemyBaseUserTableUUID,
)
from sqlalchemy import JSON, Column
from sqlmodel import Field, Relationship, select


class OAuthAccount(SQLAlchemyBaseOAuthAccountTableUUID, rx.Model, table=True):
    id: Optional[str] = Field(default=None, primary_key=True)

    user_id: Optional[str] = Field(default=None, foreign_key="user.id")
    user: "User" = Relationship(back_populates="oauth_accounts")


class User(SQLAlchemyBaseUserTableUUID, rx.Model, table=True):
    id: Optional[str] = Field(default=None, primary_key=True)
    anonymous: bool = Field(default=True)
    username: str = Field(nullable=False, unique=True)
    name: str = Field(default="")
    display_name: str = Field(default="")
    initials: str = Field(nullable=True)
    color: str = Field(nullable=True)
    avatar_url: str = Field(nullable=True)
    workspace: str = Field(default="{}", nullable=False)
    settings: str = Field(default="{}", nullable=False)
    permissions: str = Field(sa_column=Column(JSON), default={})
    oauth_accounts: List[OAuthAccount] = Relationship(back_populates="user")


class BaseState(rx.State):
    """State for the app."""

    user: Optional[User] = None

    sidebar_displayed: bool = False

    @rx.var
    def origin_url(self) -> str:
        """Get the url of the current page.

        Returns:
            str: The url of the current page.
        """
        return self.router_data.get("asPath", "")

    def toggle_sidebar_displayed(self) -> None:
        """Toggle the sidebar_chat_history displayed."""
        self.sidebar_displayed = not self.sidebar_displayed

    def load_user(self) -> None:
        """Load the user."""
        with rx.session() as session:
            self.user = session.exec(
                select(User).where(User.username == "admin")
            ).first()

    def on_load(self) -> None:
        """Load the state."""
        self.load_user()

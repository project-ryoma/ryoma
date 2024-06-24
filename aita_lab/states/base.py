"""Base state for the app."""

from typing import Optional

import reflex as rx


class User(rx.Model, table=True):
    """User Model"""

    name: str
    created_at: Optional[str]
    updated_at: Optional[str]


class BaseState(rx.State):
    """State for the app."""

    user: User = User(name="User")

    sidebar_displayed: bool = True

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
            self.user = session.exec(rx.select(User).where(User.name == "User")).first()

    def on_load(self) -> None:
        """Load the state."""
        self.load_user()

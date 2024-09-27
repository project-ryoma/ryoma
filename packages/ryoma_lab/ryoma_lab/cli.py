import uuid

import reflex as rx
from reflex.reflex import cli

from ryoma_lab.states.base import User


@cli.command(
    name="init-user",
    help="Initialize the admin user catalog.",
)
def init_user():
    with rx.session() as session:
        user = User(
            id=str(uuid.uuid4()),
            username="admin",
            email="admin@ryoma_ai.com",
            hashed_password="admin",
            permissions={"admin": ["read", "write"]},
        )

        session.add(user)
        session.commit()


def main():
    cli()


if __name__ == "__main__":
    main()

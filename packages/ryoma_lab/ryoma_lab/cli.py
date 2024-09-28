import uuid

import reflex as rx
from reflex.reflex import cli
from ryoma_lab.services.user import UserService
from ryoma_lab.services.vector_store import VectorStoreService


@cli.command(
    name="bootstrap",
    help="Bootstrap the application with initial data",
)
def bootstrap():
    with UserService() as user_service:
        user_service.create_user(
            username="admin",
            email="admin@ryoma_ai.com",
            hashed_password="admin",
            permissions={"admin": ["read", "write"]},
        )

    with VectorStoreService() as vector_store_service:
        vector_store_service.create_store(
            project_name="default",
            online_store="sqlite",
            online_store_configs={
                "type": "sqlite",
                "path": f"sqlite:///data/default.db",
                "vector_enabled": True,
            },
            offline_store="",
            offline_store_configs={},
        )


def main():
    cli()


if __name__ == "__main__":
    main()

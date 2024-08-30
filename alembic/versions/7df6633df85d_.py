"""empty message

Revision ID: 7df6633df85d
Revises: 
Create Date: 2024-08-29 17:13:15.490739

"""
from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7df6633df85d"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "agent",
        sa.Column("id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("description", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column(
            "type",
            sa.Enum(
                "ryoma", "base", "embedding", "workflow", "custom", name="agenttype"
            ),
            nullable=True,
        ),
        sa.Column("workflow", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "catalog",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("datasource", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("database", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "chat",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("user", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("question", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("answer", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("description", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("created_at", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("updated_at", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "datasource",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("datasource", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("connection_url", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("attributes", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("catalog_id", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "kernel",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tool", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("output", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "prompttemplate",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("prompt_repr", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("k_shot", sa.Integer(), nullable=False),
        sa.Column("example_format", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("selector_type", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column(
            "prompt_template_name", sqlmodel.sql.sqltypes.AutoString(), nullable=False
        ),
        sa.Column("prompt_lines", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column(
            "prompt_template_type", sqlmodel.sql.sqltypes.AutoString(), nullable=True
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "user",
        sa.Column("id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("anonymous", sa.Boolean(), nullable=False),
        sa.Column("username", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("display_name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("initials", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("color", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("avatar_url", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("workspace", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("settings", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("permissions", sa.JSON(), nullable=True),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("hashed_password", sa.String(length=1024), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_superuser", sa.Boolean(), nullable=False),
        sa.Column("is_verified", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
    )
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_user_email"), ["email"], unique=True)

    op.create_table(
        "vectorstore",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("project_name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("online_store", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("offline_store", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column(
            "online_store_configs", sqlmodel.sql.sqltypes.AutoString(), nullable=True
        ),
        sa.Column(
            "offline_store_configs", sqlmodel.sql.sqltypes.AutoString(), nullable=True
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "oauth_account",
        sa.Column("id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("user_id", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("oauth_name", sa.String(length=100), nullable=False),
        sa.Column("access_token", sa.String(length=1024), nullable=False),
        sa.Column("expires_at", sa.Integer(), nullable=True),
        sa.Column("refresh_token", sa.String(length=1024), nullable=True),
        sa.Column("account_id", sa.String(length=320), nullable=False),
        sa.Column("account_email", sa.String(length=320), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("oauth_account", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_oauth_account_account_id"), ["account_id"], unique=False
        )
        batch_op.create_index(
            batch_op.f("ix_oauth_account_oauth_name"), ["oauth_name"], unique=False
        )

    op.create_table(
        "schema",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("catalog_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["catalog_id"],
            ["catalog.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "table",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("description", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("is_view", sa.Boolean(), nullable=True),
        sa.Column("attrs", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("schema_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["schema_id"],
            ["schema.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "column",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("type", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("description", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("table_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["table_id"],
            ["table.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("column")
    op.drop_table("table")
    op.drop_table("schema")
    with op.batch_alter_table("oauth_account", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_oauth_account_oauth_name"))
        batch_op.drop_index(batch_op.f("ix_oauth_account_account_id"))

    op.drop_table("oauth_account")
    op.drop_table("vectorstore")
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_user_email"))

    op.drop_table("user")
    op.drop_table("prompttemplate")
    op.drop_table("kernel")
    op.drop_table("datasource")
    op.drop_table("chat")
    op.drop_table("catalog")
    op.drop_table("agent")
    # ### end Alembic commands ###

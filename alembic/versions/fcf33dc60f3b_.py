"""empty message

Revision ID: fcf33dc60f3b
Revises: 6e8845294076
Create Date: 2024-05-22 23:29:34.355290

"""
from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'fcf33dc60f3b'
down_revision: Union[str, None] = '6e8845294076'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('datasource', schema=None) as batch_op:
        batch_op.add_column(sa.Column('datasource_type', sqlmodel.sql.sqltypes.AutoString(), nullable=False))
        batch_op.alter_column('connection_url',
               existing_type=sa.VARCHAR(),
               nullable=False)

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('datasource', schema=None) as batch_op:
        batch_op.alter_column('connection_url',
               existing_type=sa.VARCHAR(),
               nullable=True)
        batch_op.drop_column('datasource_type')

    # ### end Alembic commands ###

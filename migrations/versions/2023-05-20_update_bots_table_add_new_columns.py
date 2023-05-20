"""update_bots_table_add_new_columns

Revision ID: 7375f7f0306b
Revises: 021e6a1e6e4c
Create Date: 2023-05-20 20:52:49.395420

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7375f7f0306b'
down_revision = '021e6a1e6e4c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('bots', sa.Column('side', sa.SmallInteger(), nullable=True))
    op.add_column('bots', sa.Column('secret', sa.String(length=255), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###

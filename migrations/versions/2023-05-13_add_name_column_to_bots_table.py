"""add name column to bots table

Revision ID: 357dbc07c4e8
Revises: 7ba821169888
Create Date: 2023-05-13 12:48:38.217234

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '357dbc07c4e8'
down_revision = '7ba821169888'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('bots', sa.Column('name', sa.String(255), nullable=True))
    # ### end Alembic commands ###

def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
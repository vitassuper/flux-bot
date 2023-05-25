"""update_exchanges_table_add_deleted_at

Revision ID: 900e1be8f4c6
Revises: 8608a0933e2d
Create Date: 2023-05-25 19:52:16.411889

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '900e1be8f4c6'
down_revision = '8608a0933e2d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('exchanges', sa.Column('deleted_at', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###

"""update_bots_table_add_deleted_at

Revision ID: 021e6a1e6e4c
Revises: 8fa1375930a6
Create Date: 2023-05-19 21:59:34.469273

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '021e6a1e6e4c'
down_revision = '8fa1375930a6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('bots', sa.Column('deleted_at', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###

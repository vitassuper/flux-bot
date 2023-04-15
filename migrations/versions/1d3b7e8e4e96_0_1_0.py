"""0.1.0

Revision ID: 1d3b7e8e4e96
Revises: a0a1f308e54a
Create Date: 2023-03-19 16:24:17.422181

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '1d3b7e8e4e96'
down_revision = 'a0a1f308e54a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_deal_id', table_name='deals')
    op.drop_index('ix_orders_id', table_name='orders')
    op.drop_constraint('orders_deal_id_fkey', 'orders', type_='foreignkey')
    op.create_foreign_key(None, 'orders', 'deals', ['deal_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###

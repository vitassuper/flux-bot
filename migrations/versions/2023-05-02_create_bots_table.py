"""create_bots_table

Revision ID: 7ba821169888
Revises: 7e438348d5aa
Create Date: 2023-05-02 18:22:48.756192

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '7ba821169888'
down_revision = '7e438348d5aa'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('bots',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('enabled', sa.Boolean(), nullable=False, default=False),
    sa.Column('api_key', sa.String(length=255), nullable=False),
    sa.Column('api_secret', sa.String(length=255), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('bots')
    # ### end Alembic commands ###

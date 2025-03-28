"""Create initial tables

Revision ID: 3c961213a92c
Revises: 
Create Date: 2025-03-15 16:55:07.313708

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3c961213a92c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('payer_groups',
    sa.Column('group_id', sa.String(length=50), nullable=False),
    sa.Column('group_name', sa.String(length=100), nullable=False),
    sa.PrimaryKeyConstraint('group_id')
    )
    op.create_table('payers',
    sa.Column('payer_id', sa.String(length=50), nullable=False),
    sa.Column('payer_name', sa.String(length=100), nullable=False),
    sa.Column('pretty_name', sa.String(length=100), nullable=True),
    sa.Column('group_id', sa.String(length=50), nullable=True),
    sa.ForeignKeyConstraint(['group_id'], ['payer_groups.group_id'], ),
    sa.PrimaryKeyConstraint('payer_id')
    )
    op.create_table('payer_details',
    sa.Column('detail_id', sa.Integer(), nullable=False),
    sa.Column('payer_name', sa.String(length=100), nullable=True),
    sa.Column('payer_id', sa.String(length=50), nullable=True),
    sa.Column('source', sa.String(length=50), nullable=True),
    sa.Column('state', sa.String(length=50), nullable=True),
    sa.ForeignKeyConstraint(['payer_id'], ['payers.payer_id'], ),
    sa.PrimaryKeyConstraint('detail_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('payer_details')
    op.drop_table('payers')
    op.drop_table('payer_groups')
    # ### end Alembic commands ###

"""data_resource_column_index

Revision ID: 7a1352b6b97f
Revises: 
Create Date: 2022-05-20 10:08:12.920497

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7a1352b6b97f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'data_resource_column_index',
        sa.Column('id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('resource_id', sa.UnicodeText(), sa.ForeignKey('resource.id'), nullable=False),
        sa.Column('columns_names', sa.UnicodeText(), nullable=False)
    )


def downgrade():
    op.drop_table('data_resource_column_index')

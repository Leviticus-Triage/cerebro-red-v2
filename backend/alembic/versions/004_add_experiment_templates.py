"""Add experiment templates table

Revision ID: 004_templates
Revises: 003_add_performance_indexes
Create Date: 2025-12-29 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '004_templates'
down_revision: Union[str, None] = '003_add_performance_indexes'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create experiment_templates table
    op.create_table(
        'experiment_templates',
        sa.Column('template_id', sa.String(36), nullable=False, server_default=sa.text("lower(hex(randomblob(16)))")),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.String(length=1000), nullable=True),
        sa.Column('config_json', sa.Text(), nullable=False),
        sa.Column('tags', sa.JSON(), nullable=False),
        sa.Column('is_public', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('usage_count', sa.Integer(), nullable=False, server_default='0'),
        sa.PrimaryKeyConstraint('template_id')
    )
    
    # Create indexes for performance
    op.create_index('idx_templates_created_at', 'experiment_templates', ['created_at'])
    op.create_index('idx_templates_name', 'experiment_templates', ['name'])
    op.create_index('idx_templates_is_public', 'experiment_templates', ['is_public'])


def downgrade() -> None:
    op.drop_index('idx_templates_is_public', table_name='experiment_templates')
    op.drop_index('idx_templates_name', table_name='experiment_templates')
    op.drop_index('idx_templates_created_at', table_name='experiment_templates')
    op.drop_table('experiment_templates')

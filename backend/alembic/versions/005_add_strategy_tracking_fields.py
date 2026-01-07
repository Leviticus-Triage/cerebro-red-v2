"""Add strategy tracking fields

Revision ID: 005_strategy_tracking
Revises: 004_templates
Create Date: 2026-01-06 13:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '005_strategy_tracking'
down_revision: Union[str, None] = '004_templates'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new fields to attack_iterations table
    op.add_column(
        'attack_iterations',
        sa.Column('intended_strategy', sa.String(50), nullable=True, comment='Originally selected strategy before any fallbacks')
    )
    op.add_column(
        'attack_iterations',
        sa.Column('strategy_fallback_occurred', sa.Boolean(), nullable=False, server_default='0', comment='True if executed_strategy differs from intended_strategy')
    )
    op.add_column(
        'attack_iterations',
        sa.Column('fallback_reason', sa.Text(), nullable=True, comment='Exception message or reason for strategy fallback')
    )


def downgrade() -> None:
    op.drop_column('attack_iterations', 'fallback_reason')
    op.drop_column('attack_iterations', 'strategy_fallback_occurred')
    op.drop_column('attack_iterations', 'intended_strategy')

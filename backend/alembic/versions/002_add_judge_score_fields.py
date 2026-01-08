"""Add missing judge score fields

Revision ID: 002_add_judge_score_fields
Revises: 001_initial
Create Date: 2024-12-23 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002_add_judge_score_fields'
down_revision: Union[str, None] = '001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new judge score fields to judge_scores table
    op.add_column('judge_scores', sa.Column('hallucination_score', sa.Float(), nullable=False, server_default='0.0'))
    op.add_column('judge_scores', sa.Column('bias_score', sa.Float(), nullable=False, server_default='0.0'))
    op.add_column('judge_scores', sa.Column('logical_consistency_score', sa.Float(), nullable=False, server_default='0.0'))
    op.add_column('judge_scores', sa.Column('sycophancy_score', sa.Float(), nullable=False, server_default='0.0'))


def downgrade() -> None:
    # Remove new judge score fields
    op.drop_column('judge_scores', 'sycophancy_score')
    op.drop_column('judge_scores', 'logical_consistency_score')
    op.drop_column('judge_scores', 'bias_score')
    op.drop_column('judge_scores', 'hallucination_score')


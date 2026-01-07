"""Add performance indexes for experiments and attack_iterations

Revision ID: 003_add_performance_indexes
Revises: 002_add_judge_score_fields
Create Date: 2024-12-23 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '003_add_performance_indexes'
down_revision: Union[str, None] = '002_add_judge_score_fields'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Composite index on experiments(status, created_at) for filtering by status and sorting by date
    op.create_index(
        'idx_experiments_status_created_at',
        'experiments',
        ['status', 'created_at'],
        unique=False
    )
    
    # Composite index on attack_iterations(experiment_id, timestamp) for efficient lookups
    op.create_index(
        'idx_attack_iterations_experiment_timestamp',
        'attack_iterations',
        ['experiment_id', 'timestamp'],
        unique=False
    )


def downgrade() -> None:
    # Drop indexes in reverse order
    op.drop_index('idx_attack_iterations_experiment_timestamp', table_name='attack_iterations')
    op.drop_index('idx_experiments_status_created_at', table_name='experiments')


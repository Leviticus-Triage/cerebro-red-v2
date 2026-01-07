"""Initial schema: experiments, iterations, vulnerabilities

Revision ID: 001_initial
Revises: 
Create Date: 2024-12-23 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
# SQLite doesn't have native UUID type, use String(36) instead
# UUIDs will be stored as strings in SQLite

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create experiments table
    op.create_table(
        'experiments',
        sa.Column('experiment_id', sa.String(36), nullable=False, server_default=sa.text("lower(hex(randomblob(16)))")),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('target_model_provider', sa.String(length=50), nullable=False),
        sa.Column('target_model_name', sa.String(length=200), nullable=False),
        sa.Column('attacker_model_provider', sa.String(length=50), nullable=False),
        sa.Column('attacker_model_name', sa.String(length=200), nullable=False),
        sa.Column('judge_model_provider', sa.String(length=50), nullable=False),
        sa.Column('judge_model_name', sa.String(length=200), nullable=False),
        sa.Column('initial_prompts', sa.JSON(), nullable=False),
        sa.Column('strategies', sa.JSON(), nullable=False),
        sa.Column('max_iterations', sa.Integer(), nullable=False),
        sa.Column('max_concurrent_attacks', sa.Integer(), nullable=False),
        sa.Column('success_threshold', sa.Float(), nullable=False),
        sa.Column('timeout_seconds', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint('experiment_id')
    )
    op.create_index('idx_experiments_created_at', 'experiments', ['created_at'])
    
    # Create attack_iterations table
    op.create_table(
        'attack_iterations',
        sa.Column('iteration_id', sa.String(36), nullable=False, server_default=sa.text("lower(hex(randomblob(16)))")),
        sa.Column('experiment_id', sa.String(36), nullable=False),
        sa.Column('iteration_number', sa.Integer(), nullable=False),
        sa.Column('strategy_used', sa.String(length=50), nullable=False),
        sa.Column('original_prompt', sa.Text(), nullable=False),
        sa.Column('mutated_prompt', sa.Text(), nullable=False),
        sa.Column('target_response', sa.Text(), nullable=False),
        sa.Column('judge_score', sa.Float(), nullable=False),
        sa.Column('judge_reasoning', sa.Text(), nullable=False),
        sa.Column('success', sa.Boolean(), nullable=False),
        sa.Column('latency_ms', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('attacker_feedback', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('iteration_id'),
        sa.ForeignKeyConstraint(['experiment_id'], ['experiments.experiment_id'], ondelete='CASCADE')
    )
    op.create_index('idx_attack_iterations_experiment_number', 'attack_iterations', ['experiment_id', 'iteration_number'])
    
    # Create prompt_mutations table
    op.create_table(
        'prompt_mutations',
        sa.Column('mutation_id', sa.String(36), nullable=False, server_default=sa.text("lower(hex(randomblob(16)))")),
        sa.Column('iteration_id', sa.String(36), nullable=False),
        sa.Column('strategy', sa.String(length=50), nullable=False),
        sa.Column('input_prompt', sa.Text(), nullable=False),
        sa.Column('output_prompt', sa.Text(), nullable=False),
        sa.Column('mutation_params', sa.JSON(), nullable=False),
        sa.Column('prompt_hash', sa.String(length=64), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('mutation_id'),
        sa.ForeignKeyConstraint(['iteration_id'], ['attack_iterations.iteration_id'], ondelete='CASCADE')
    )
    op.create_index('idx_prompt_mutations_hash', 'prompt_mutations', ['prompt_hash'])
    
    # Create judge_scores table
    op.create_table(
        'judge_scores',
        sa.Column('score_id', sa.String(36), nullable=False, server_default=sa.text("lower(hex(randomblob(16)))")),
        sa.Column('iteration_id', sa.String(36), nullable=False),
        sa.Column('overall_score', sa.Float(), nullable=False),
        sa.Column('jailbreak_success_score', sa.Float(), nullable=False),
        sa.Column('harmful_content_score', sa.Float(), nullable=False),
        sa.Column('policy_violation_score', sa.Float(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('reasoning', sa.Text(), nullable=False),
        sa.Column('fallback_used', sa.Boolean(), nullable=False),
        sa.Column('judge_model', sa.String(length=200), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('score_id'),
        sa.ForeignKeyConstraint(['iteration_id'], ['attack_iterations.iteration_id'], ondelete='CASCADE')
    )
    op.create_index('idx_judge_scores_overall', 'judge_scores', ['overall_score'])
    
    # Create vulnerabilities table
    op.create_table(
        'vulnerabilities',
        sa.Column('vulnerability_id', sa.String(36), nullable=False, server_default=sa.text("lower(hex(randomblob(16)))")),
        sa.Column('experiment_id', sa.String(36), nullable=False),
        sa.Column('severity', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('successful_prompt', sa.Text(), nullable=False),
        sa.Column('target_response', sa.Text(), nullable=False),
        sa.Column('attack_strategy', sa.String(length=50), nullable=False),
        sa.Column('iteration_number', sa.Integer(), nullable=False),
        sa.Column('judge_score', sa.Float(), nullable=False),
        sa.Column('reproducible', sa.Boolean(), nullable=False),
        sa.Column('cve_references', sa.JSON(), nullable=False),
        sa.Column('mitigation_suggestions', sa.JSON(), nullable=False),
        sa.Column('discovered_at', sa.DateTime(), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint('vulnerability_id'),
        sa.ForeignKeyConstraint(['experiment_id'], ['experiments.experiment_id'], ondelete='CASCADE')
    )
    op.create_index('idx_vulnerabilities_severity', 'vulnerabilities', ['severity'])
    op.create_index('idx_vulnerabilities_discovered_at', 'vulnerabilities', ['discovered_at'])
    
    # Create model_configs table
    op.create_table(
        'model_configs',
        sa.Column('config_id', sa.String(36), nullable=False, server_default=sa.text("lower(hex(randomblob(16)))")),
        sa.Column('provider', sa.String(length=50), nullable=False),
        sa.Column('model_name', sa.String(length=200), nullable=False),
        sa.Column('api_base', sa.String(length=500), nullable=True),
        sa.Column('api_key_env_var', sa.String(length=100), nullable=True),
        sa.Column('temperature', sa.Float(), nullable=False),
        sa.Column('max_tokens', sa.Integer(), nullable=True),
        sa.Column('timeout', sa.Integer(), nullable=False),
        sa.Column('additional_params', sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint('config_id'),
        sa.UniqueConstraint('provider', 'model_name', name='uq_model_config_provider_model')
    )


def downgrade() -> None:
    op.drop_table('model_configs')
    op.drop_table('vulnerabilities')
    op.drop_table('judge_scores')
    op.drop_table('prompt_mutations')
    op.drop_table('attack_iterations')
    op.drop_table('experiments')


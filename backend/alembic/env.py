"""
Alembic environment configuration for async SQLAlchemy migrations.

This file configures Alembic to work with async SQLAlchemy and our
database models for CEREBRO-RED v2.
"""

from logging.config import fileConfig
import asyncio
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context

# Import Base and all models
from core.database import Base
from core.database import (
    ExperimentDB,
    AttackIterationDB,
    PromptMutationDB,
    JudgeScoreDB,
    VulnerabilityDB,
    ModelConfigDB,
)

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    if not url:
        # Fallback to settings if not in alembic.ini
        from utils.config import get_settings
        settings = get_settings()
        url = settings.database.url
    
    # Ensure database directory exists for SQLite
    if url and url.startswith("sqlite"):
        import os
        import re
        match = re.search(r'sqlite\+aiosqlite:///(.+)', url)
        if match:
            db_path = match.group(1)
            if db_path.startswith('./'):
                db_path = db_path[2:]
            db_dir = os.path.dirname(db_path)
            if db_dir:
                os.makedirs(db_dir, exist_ok=True)
    
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in async mode."""
    # Get database URL from config or environment
    database_url = config.get_main_option("sqlalchemy.url")
    if not database_url:
        # Fallback to settings if not in alembic.ini
        from utils.config import get_settings
        settings = get_settings()
        database_url = settings.database.url
    
    # Ensure database directory exists for SQLite
    if database_url.startswith("sqlite"):
        import os
        import re
        # Extract path from SQLite URL (sqlite+aiosqlite:///./path/to/db.db)
        match = re.search(r'sqlite\+aiosqlite:///(.+)', database_url)
        if match:
            db_path = match.group(1)
            # Remove leading ./ if present
            if db_path.startswith('./'):
                db_path = db_path[2:]
            # Get directory path
            db_dir = os.path.dirname(db_path)
            if db_dir:
                os.makedirs(db_dir, exist_ok=True)
    
    connectable = create_async_engine(
        database_url,
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()


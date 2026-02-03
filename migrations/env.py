"""Alembic migrations environment configuration.

This file configures Alembic to work with SQLModel and our project's models.
"""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlmodel import SQLModel, create_engine

from src.core.config import settings

# Import all models for autogenerate support
from src.modules.missions._models import (  # noqa: F401
    MissionProgress,
    MissionStep,
    MissionStepProgress,
    MissionTemplate,
)
from src.modules.phrases._models import Phrase, PhraseStepMapping  # noqa: F401
from src.modules.profiles import Profile  # noqa: F401
from src.modules.routes._models import RouteHistory  # noqa: F401
from src.modules.translations import Translation  # noqa: F401
from src.modules.translations._models import (  # noqa: F401
    TranslationCategoryMapping,
    TranslationContextPrompt,
    TranslationPrimaryCategory,
    TranslationSubCategory,
    TranslationThread,
)

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set the database URL from settings
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# SQLModel's metadata
target_metadata = SQLModel.metadata


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
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    connectable = create_engine(
        settings.DATABASE_URL,
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

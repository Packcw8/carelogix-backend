import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# Alembic Config object
config = context.config

# ✅ Pull DATABASE_URL from environment if available
database_url = os.getenv("DATABASE_URL")
if database_url:
    config.set_main_option("sqlalchemy.url", database_url)

# Set up loggers
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ✅ Import models and Base metadata
from app.database import Base
from app.models.forms import FormSubmission  # Ensure model is imported
from app.models.infield_note import InfieldNote  # Add all your models if needed

target_metadata = Base.metadata

# --- OFFLINE MODE ---
def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

# --- ONLINE MODE ---
def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

# Choose the mode
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

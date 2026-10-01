import os
from logging.config import fileConfig

from alembic import context
from flask import current_app

from app.extensions import db

config = context.config

if (
    config.config_file_name is not None
    and os.path.exists(config.config_file_name)
):
    fileConfig(config.config_file_name)

target_metadata = db.metadata


def get_database_url():
    return current_app.config[
        "SQLALCHEMY_DATABASE_URI"
    ]


def run_migrations_offline():
    url = get_database_url()

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={
            "paramstyle": "named"
        },
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    with current_app.app_context():
        connectable = db.engine

        with connectable.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=target_metadata,
                compare_type=True,
            )

            with context.begin_transaction():
                context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

from typing import Any

import sqlalchemy as sa
from alembic import context

import mealie.db.models._all_models  # noqa: F401
from mealie.core.config import get_app_settings
from mealie.db.models._model_base import SqlAlchemyBase

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = SqlAlchemyBase.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

# Set DB url from config
settings = get_app_settings()

if not settings.DB_URL:
    raise Exception("DB URL not set in config")

config.set_main_option("sqlalchemy.url", settings.DB_URL.replace("%", "%%"))


def include_object(object: Any, name: str, type_: str, reflected: bool, compare_to: Any):
    # skip dropping food/unit unique constraints; they are defined manually so alembic doesn't see them
    # see: revision dded3119c1fe
    if type_ == "unique_constraint" and name == "ingredient_foods_name_group_id_key" and compare_to is None:
        return False
    if type_ == "unique_constraint" and name == "ingredient_units_name_group_id_key" and compare_to is None:
        return False

    # skip changing the quantity column in recipes_ingredients; it's a float on postgres, but an integer on sqlite
    # see: revision 263dd6707191
    if (
        type_ == "column"
        and name == "quantity"
        and object.table.name == "recipes_ingredients"
        and hasattr(compare_to, "type")
        and isinstance(compare_to.type, sa.Integer)
    ):
        return False

    return True


def run_migrations_offline():
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


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = sa.engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=sa.pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            user_module_prefix="mealie.db.migration_types.",
            render_as_batch=True,
            include_object=include_object,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

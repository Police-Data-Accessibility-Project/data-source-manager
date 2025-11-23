from alembic import command
from alembic.config import Config

from src.util.helper_functions import get_from_env


def apply_migrations():
    print("Applying migrations...")
    alembic_config = Config("alembic.ini")
    connection_string = (
        f"postgresql://{get_from_env('POSTGRES_USER')}:{get_from_env('POSTGRES_PASSWORD')}" +
        f"@{get_from_env('POSTGRES_HOST')}:{get_from_env('POSTGRES_PORT')}/{get_from_env('POSTGRES_DB')}")

    alembic_config.set_main_option(
        "sqlalchemy.url",
        connection_string
    )
    command.upgrade(alembic_config, "head")
    print("Migrations applied.")

if __name__ == "__main__":
    apply_migrations()
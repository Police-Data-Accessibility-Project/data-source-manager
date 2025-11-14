from sqlalchemy import create_engine, Engine

from src.db.models.templates_.base import Base


def wipe_database(engine: Engine) -> None:
    """Wipe all data from database."""
    with engine.connect() as connection:
        for table in reversed(Base.metadata.sorted_tables):
            if table.info == "view":
                continue
            connection.execute(table.delete())
        connection.commit()

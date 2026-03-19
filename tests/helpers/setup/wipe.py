from sqlalchemy import Engine

from src.db.models.templates_.base import Base

PRESERVED_TABLES = {
    "batch_strategies",
}


def wipe_database(engine: Engine) -> None:
    """Wipe all data from database."""
    with engine.connect() as connection:
        for table in reversed(Base.metadata.sorted_tables):
            if table.info == "view":
                continue
            if table.name in PRESERVED_TABLES:
                continue
            connection.execute(table.delete())
        connection.commit()

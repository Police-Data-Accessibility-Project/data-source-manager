from sqlalchemy import String, Column

from src.db.models.helpers import county_column
from src.db.models.templates_.with_id import WithIDBase


class Locality(
    WithIDBase,
):

    __tablename__ = "localities"

    name = Column(String(255), nullable=False)
    county_id = county_column(nullable=False)

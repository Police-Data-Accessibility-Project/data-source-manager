from sqlalchemy import String, Column
from sqlalchemy.orm import Mapped

from src.db.models.helpers import county_column
from src.db.models.templates_.with_id import WithIDBase


class Locality(
    WithIDBase,
):

    __tablename__ = "localities"

    name = Column(String(255), nullable=False)
    county_id: Mapped[int] = county_column(nullable=False)

from sqlalchemy import String, Column, Float, Integer
from sqlalchemy.orm import Mapped

from src.db.models.helpers import us_state_column
from src.db.models.templates_.with_id import WithIDBase


class County(
    WithIDBase,
):
    __tablename__ = "counties"

    name: Mapped[str]
    state_id: Mapped[int] = us_state_column()
    fips: Mapped[str] = Column(String(5), nullable=True)
    lat: Mapped[float] = Column(Float, nullable=True)
    lng: Mapped[float] = Column(Float, nullable=True)
    population: Mapped[int] = Column(Integer, nullable=True)
from sqlalchemy.orm import Mapped

from src.db.models.templates_.with_id import WithIDBase


class USState(
    WithIDBase,
):
    __tablename__ = "us_states"

    state_name: Mapped[str]
    state_iso: Mapped[str]
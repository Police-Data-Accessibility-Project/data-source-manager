from sqlalchemy import PrimaryKeyConstraint
from sqlalchemy.orm import Mapped

from src.db.models.helpers import enum_column
from src.db.models.impl.flag.url_validated.enums import URLType
from src.db.models.mixins import URLDependentMixin, CreatedAtMixin, UpdatedAtMixin
from src.db.models.templates_.base import Base


class FlagURLValidated(
    URLDependentMixin,
    CreatedAtMixin,
    UpdatedAtMixin,
    Base,
):
    __tablename__ = "flag_url_validated"
    __table_args__ = (
        PrimaryKeyConstraint(
            'url_id',
        ),
    )

    type: Mapped[URLType] = enum_column(
        enum_type=URLType,
        name="url_type",
    )

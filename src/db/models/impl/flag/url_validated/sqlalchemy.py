from sqlalchemy import PrimaryKeyConstraint

from src.db.models.helpers import enum_column
from src.db.models.impl.flag.url_validated.enums import ValidatedURLType
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

    type = enum_column(
        enum_type=ValidatedURLType,
        name="validated_url_type",
    )

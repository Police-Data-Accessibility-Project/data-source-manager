from sqlalchemy.orm import Mapped

from src.core.enums import RecordType
from src.db.models.helpers import url_id_primary_key_constraint, enum_column
from src.db.models.mixins import URLDependentMixin, CreatedAtMixin
from src.db.models.templates_.base import Base


class URLRecordType(
    Base,
    CreatedAtMixin,
    URLDependentMixin
):
    __tablename__ = "url_record_type"
    __table_args__ = (url_id_primary_key_constraint(),)

    record_type: Mapped[RecordType] = enum_column(RecordType, name="record_type", nullable=False)
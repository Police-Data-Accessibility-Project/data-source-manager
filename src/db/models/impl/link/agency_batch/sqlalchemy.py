from sqlalchemy import PrimaryKeyConstraint

from src.db.models.mixins import CreatedAtMixin, LocationDependentMixin, AgencyDependentMixin, BatchDependentMixin
from src.db.models.templates_.base import Base


class LinkAgencyBatch(
    Base,
    CreatedAtMixin,
    BatchDependentMixin,
    AgencyDependentMixin,
):
    __tablename__ = "link_agency_batches"
    __table_args__ = (
        PrimaryKeyConstraint(
            'batch_id',
            'agency_id',
            name='link_agency_batches_pk'
        ),
    )

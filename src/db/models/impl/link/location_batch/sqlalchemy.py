from sqlalchemy import PrimaryKeyConstraint

from src.db.models.mixins import LocationDependentMixin, BatchDependentMixin, CreatedAtMixin
from src.db.models.templates_.base import Base


class LinkLocationBatch(
    Base,
    LocationDependentMixin,
    BatchDependentMixin,
    CreatedAtMixin
):

    __tablename__ = "link_batches__locations"
    __table_args__ = (
        PrimaryKeyConstraint(
            'batch_id',
            'location_id',
            name='link_location_batches_pk'
        ),
    )
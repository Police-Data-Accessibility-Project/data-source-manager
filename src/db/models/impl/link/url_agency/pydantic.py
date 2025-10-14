from pydantic import ConfigDict

from src.db.models.impl.link.url_agency.sqlalchemy import LinkURLAgency
from src.db.templates.markers.bulk.delete import BulkDeletableModel
from src.db.templates.markers.bulk.insert import BulkInsertableModel


class LinkURLAgencyPydantic(
    BulkDeletableModel,
    BulkInsertableModel
):
    model_config = ConfigDict(frozen=True)

    url_id: int
    agency_id: int

    @classmethod
    def sa_model(cls) -> type[LinkURLAgency]:
        return LinkURLAgency
from src.db.models.impl.link.batch_url.sqlalchemy import LinkBatchURL
from src.db.templates.markers.bulk.insert import BulkInsertableModel


class LinkBatchURLPydantic(BulkInsertableModel):
    batch_id: int
    url_id: int

    @classmethod
    def sa_model(cls) -> type[LinkBatchURL]:
        return LinkBatchURL
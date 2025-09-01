from src.db.templates.markers.bulk.delete import BulkDeletableModel
from src.db.templates.markers.bulk.insert import BulkInsertableModel


class LinkAgencyIDSubtaskAgenciesPydantic(
    BulkInsertableModel,
    BulkDeletableModel,
):
    subtask_id: int
    agency_id: int
    confidence: int

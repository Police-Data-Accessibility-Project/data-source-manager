from src.db.templates.markers.bulk.insert import BulkInsertableModel


class AgencyIDSubtaskSuggestionPydantic(
    BulkInsertableModel,
):
    subtask_id: int
    agency_id: int
    confidence: int

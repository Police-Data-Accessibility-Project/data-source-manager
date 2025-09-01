from src.core.tasks.url.operators.agency_identification.dtos.suggestion import URLAgencySuggestionInfo
from src.core.tasks.url.operators.agency_identification.subtasks.templates.subtask import AgencyIdentificationSubtaskBase
from src.db.client.async_ import AsyncDatabaseClient


class HomepageMatchSubtask(AgencyIdentificationSubtaskBase):

    def __init__(self, db_client: AsyncDatabaseClient):
        self.db_client = db_client

    async def run(
        self,
        url_id: int,
        collector_metadata: dict | None = None
    ) -> URLAgencySuggestionInfo:
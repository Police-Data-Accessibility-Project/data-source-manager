from src.core.tasks.url.operators.agency_identification.subtasks.queries.survey.queries.core import \
    AgencyIDSubtaskSurveyQueryBuilder
from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.url.suggestion.agency.subtask.enum import AutoAgencyIDSubtaskType


class AgencyIDSubtaskPlanner:

    def __init__(
        self,
        adb_client: AsyncDatabaseClient,
    ) -> None:
        self.adb_client = adb_client

    async def plan_next_subtask(self) -> AutoAgencyIDSubtaskType | None:

        next_subtask: AutoAgencyIDSubtaskType | None = \
            await self.adb_client.run_query_builder(
                AgencyIDSubtaskSurveyQueryBuilder()
            )
        return next_subtask


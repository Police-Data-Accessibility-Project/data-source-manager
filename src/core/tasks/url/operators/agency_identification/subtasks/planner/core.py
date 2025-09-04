from src.core.tasks.url.operators.agency_identification.subtasks.planner.queries.core import \
    AgencyIDSubtaskSurveyQueryBuilder
from src.core.tasks.url.operators.agency_identification.subtasks.planner.reconcile import reconcile_tiebreakers
from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.url.suggestion.agency.subtask.enum import AutoAgencyIDSubtaskType


class AgencyIDSubtaskPlanner:

    def __init__(
        self,
        adb_client: AsyncDatabaseClient,
    ) -> None:
        self.adb_client = adb_client

    # TODO: Add test to confirm properly returns one, multiple, or None
    async def plan_next_subtask(self) -> AutoAgencyIDSubtaskType | None:

        applicable_subtasks: list[AutoAgencyIDSubtaskType] = \
            await self.adb_client.run_query_builder(
                AgencyIDSubtaskSurveyQueryBuilder()
            )

        # Reconcile tiebreakers
        if len(applicable_subtasks) == 0:
            return None
        if len(applicable_subtasks) > 1:
            return await reconcile_tiebreakers(applicable_subtasks)
        return applicable_subtasks[0]


from src.core.tasks.mixins.link_urls import LinkURLsMixin
from src.core.tasks.url.operators.base import URLTaskOperatorBase
from src.core.tasks.url.operators.location_id.subtasks.loader import LocationIdentificationSubtaskLoader
from src.core.tasks.url.operators.location_id.subtasks.queries.survey.queries.core import LocationIDSurveyQueryBuilder
from src.db.client.async_ import AsyncDatabaseClient
from src.db.enums import TaskType
from src.db.models.impl.url.suggestion.location.auto.subtask.enums import LocationIDSubtaskType


class LocationIdentificationTaskOperator(
    URLTaskOperatorBase,
    LinkURLsMixin,
):

    def __init__(
        self,
        adb_client: AsyncDatabaseClient,
        loader: LocationIdentificationSubtaskLoader,
    ):
        super().__init__(adb_client)
        self.loader = loader

    @property
    def task_type(self) -> TaskType:
        return TaskType.LOCATION_ID

    async def meets_task_prerequisites(self) -> bool:
        """
        Modifies:
        - self._subtask
        """
        flagger = SubtaskFlagger()
        allowed_subtasks: list[LocationIDSubtaskType] = flagger.get_allowed_subtasks()

        next_subtask: LocationIDSubtaskType | None = \
            await self.adb_client.run_query_builder(
                LocationIDSurveyQueryBuilder(
                    allowed_subtasks=allowed_subtasks
                )
            )
        self._subtask = next_subtask
        if next_subtask is None:
            return False
        return True

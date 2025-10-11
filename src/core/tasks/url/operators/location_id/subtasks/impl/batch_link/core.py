from src.core.tasks.url.operators.location_id.subtasks.impl.batch_link.inputs import LocationBatchLinkInput
from src.core.tasks.url.operators.location_id.subtasks.impl.batch_link.query import GetLocationBatchLinkQueryBuilder
from src.core.tasks.url.operators.location_id.subtasks.impl.nlp_location_freq.constants import ITERATIONS_PER_SUBTASK
from src.core.tasks.url.operators.location_id.subtasks.models.subtask import AutoLocationIDSubtaskData
from src.core.tasks.url.operators.location_id.subtasks.models.suggestion import LocationSuggestion
from src.core.tasks.url.operators.location_id.subtasks.templates.subtask import LocationIDSubtaskOperatorBase
from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.url.suggestion.location.auto.subtask.enums import LocationIDSubtaskType
from src.db.models.impl.url.suggestion.location.auto.subtask.pydantic import AutoLocationIDSubtaskPydantic


class LocationBatchLinkSubtaskOperator(LocationIDSubtaskOperatorBase):

    def __init__(
        self,
        task_id: int,
        adb_client: AsyncDatabaseClient,
    ):
        super().__init__(adb_client=adb_client, task_id=task_id)

    async def inner_logic(self) -> None:
        for iteration in range(ITERATIONS_PER_SUBTASK):
            inputs: list[LocationBatchLinkInput] = await self._get_from_db()
            if len(inputs) == 0:
                break
            await self.run_subtask_iteration(inputs)

    async def run_subtask_iteration(
        self,
        inputs: list[LocationBatchLinkInput]
    ) -> None:
        self.linked_urls.extend([input_.url_id for input_ in inputs])
        subtask_data_list: list[AutoLocationIDSubtaskData] = []
        for input_ in inputs:
            subtask_data_list.append(
                AutoLocationIDSubtaskData(
                    pydantic_model=AutoLocationIDSubtaskPydantic(
                        url_id=input_.url_id,
                        task_id=self.task_id,
                        locations_found=True,
                        type=LocationIDSubtaskType.BATCH_LINK,
                    ),
                    suggestions=[
                        LocationSuggestion(
                            location_id=input_.location_id,
                            confidence=80,
                        )
                    ]
                )
            )

        await self._upload_subtask_data(subtask_data_list)

    async def _get_from_db(self) -> list[LocationBatchLinkInput]:
        query = GetLocationBatchLinkQueryBuilder()
        return await self.adb_client.run_query_builder(query)
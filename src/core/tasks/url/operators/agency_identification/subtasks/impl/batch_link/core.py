from src.core.tasks.url.operators.agency_identification.subtasks.impl.batch_link.params import \
    AgencyBatchLinkSubtaskParams
from src.core.tasks.url.operators.agency_identification.subtasks.impl.batch_link.query import \
    GetLocationBatchLinkSubtaskParamsQueryBuilder
from src.core.tasks.url.operators.agency_identification.subtasks.models.subtask import AutoAgencyIDSubtaskData
from src.core.tasks.url.operators.agency_identification.subtasks.models.suggestion import AgencySuggestion
from src.core.tasks.url.operators.agency_identification.subtasks.templates.subtask import AgencyIDSubtaskOperatorBase
from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.annotation.agency.auto.subtask.enum import AutoAgencyIDSubtaskType
from src.db.models.impl.annotation.agency.auto.subtask.pydantic import URLAutoAgencyIDSubtaskPydantic


class AgencyBatchLinkSubtaskOperator(AgencyIDSubtaskOperatorBase):

    def __init__(
        self,
        adb_client: AsyncDatabaseClient,
        task_id: int
    ):
        super().__init__(adb_client=adb_client, task_id=task_id)

    async def inner_logic(self) -> None:
        params: list[AgencyBatchLinkSubtaskParams] = await self._get_params()
        self.linked_urls = [param.url_id for param in params]
        subtask_data_list: list[AutoAgencyIDSubtaskData] = []
        for param in params:
            subtask_data: AutoAgencyIDSubtaskData = AutoAgencyIDSubtaskData(
                pydantic_model=URLAutoAgencyIDSubtaskPydantic(
                    task_id=self.task_id,
                    url_id=param.url_id,
                    type=AutoAgencyIDSubtaskType.BATCH_LINK,
                    agencies_found=True,
                ),
                suggestions=[
                    AgencySuggestion(
                        agency_id=param.agency_id,
                        confidence=80,
                    )
                ],
            )
            subtask_data_list.append(subtask_data)

        await self._upload_subtask_data(subtask_data_list)

    async def _get_params(self) -> list[AgencyBatchLinkSubtaskParams]:
        return await self.adb_client.run_query_builder(
            GetLocationBatchLinkSubtaskParamsQueryBuilder()
        )
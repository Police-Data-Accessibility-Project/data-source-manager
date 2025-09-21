from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.convert import \
    convert_location_agency_mappings_to_subtask_data_list
from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.models.input import \
    NLPLocationMatchSubtaskInput
from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.query_.query import \
    GetAgenciesLinkedToAnnotatedLocationsQueryBuilder
from src.core.tasks.url.operators.agency_identification.subtasks.models.subtask import AutoAgencyIDSubtaskData
from src.core.tasks.url.operators.agency_identification.subtasks.templates.subtask import AgencyIDSubtaskOperatorBase
from src.db.client.async_ import AsyncDatabaseClient


class NLPLocationMatchSubtaskOperator(AgencyIDSubtaskOperatorBase):

    def __init__(
        self,
        adb_client: AsyncDatabaseClient,
        task_id: int,
    ) -> None:
        super().__init__(adb_client, task_id=task_id)

    async def inner_logic(self) -> None:
        inputs: list[NLPLocationMatchSubtaskInput] = await self._get_from_db()
        await self.run_subtask_iteration(inputs)

    async def run_subtask_iteration(self, inputs: list[NLPLocationMatchSubtaskInput]) -> None:
        self.linked_urls.extend([input_.url_id for input_ in inputs])
        subtask_data_list: list[AutoAgencyIDSubtaskData] = convert_location_agency_mappings_to_subtask_data_list(
            task_id=self.task_id,
            inputs=inputs,
        )
        await self._upload_subtask_data(subtask_data_list)

    async def _get_from_db(self) -> list[NLPLocationMatchSubtaskInput]:
        return await self.adb_client.run_query_builder(
            GetAgenciesLinkedToAnnotatedLocationsQueryBuilder(),
        )

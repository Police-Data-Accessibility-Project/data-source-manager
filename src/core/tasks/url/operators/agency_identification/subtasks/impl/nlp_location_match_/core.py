from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.constants import \
    ITERATIONS_PER_SUBTASK
from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.models.input import \
    NLPLocationMatchSubtaskInput
from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.processor.core import \
    AgencyIDSubtaskInternalProcessor
from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.processor.nlp.core import \
    NLPProcessor
from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.query import \
    GetNLPLocationMatchSubtaskInputQueryBuilder
from src.core.tasks.url.operators.agency_identification.subtasks.models.subtask import AutoAgencyIDSubtaskData
from src.core.tasks.url.operators.agency_identification.subtasks.templates.subtask import AgencyIDSubtaskOperatorBase
from src.db.client.async_ import AsyncDatabaseClient
from src.external.pdap.client import PDAPClient


class NLPLocationMatchSubtaskOperator(AgencyIDSubtaskOperatorBase):

    def __init__(
        self,
        adb_client: AsyncDatabaseClient,
        task_id: int,
        pdap_client: PDAPClient,
        processor: NLPProcessor
    ) -> None:
        super().__init__(adb_client, task_id=task_id)
        self.processor = AgencyIDSubtaskInternalProcessor(
            nlp_processor=processor,
            pdap_client=pdap_client,
            task_id=task_id,
        )

    async def inner_logic(self) -> None:
        for iteration in range(ITERATIONS_PER_SUBTASK):
            inputs: list[NLPLocationMatchSubtaskInput] = await self._get_from_db()
            if len(inputs) == 0:
                break
            await self.run_subtask_iteration(inputs)

    async def run_subtask_iteration(self, inputs: list[NLPLocationMatchSubtaskInput]) -> None:
        subtask_data_list: list[AutoAgencyIDSubtaskData] = await self._process_inputs(inputs)

        await self._upload_subtask_data(subtask_data_list)

    async def _process_inputs(
        self,
        inputs: list[NLPLocationMatchSubtaskInput]
    ) -> list[AutoAgencyIDSubtaskData]:
        return await self.processor.process(
            inputs=inputs,
        )

    async def _get_from_db(self) -> list[NLPLocationMatchSubtaskInput]:
        return await self.adb_client.run_query_builder(
            query_builder=GetNLPLocationMatchSubtaskInputQueryBuilder(),
        )

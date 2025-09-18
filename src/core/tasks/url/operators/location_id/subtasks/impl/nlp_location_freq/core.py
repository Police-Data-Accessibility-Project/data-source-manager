from src.core.tasks.url.operators.location_id.subtasks.impl.nlp_location_freq.constants import ITERATIONS_PER_SUBTASK
from src.core.tasks.url.operators.location_id.subtasks.impl.nlp_location_freq.models.input import \
    NLPLocationMatchSubtaskInput
from src.core.tasks.url.operators.location_id.subtasks.impl.nlp_location_freq.processor.core import \
    NLPLocationFrequencySubtaskInternalProcessor
from src.core.tasks.url.operators.location_id.subtasks.impl.nlp_location_freq.processor.nlp.core import NLPProcessor
from src.core.tasks.url.operators.location_id.subtasks.impl.nlp_location_freq.query import \
    GetNLPLocationMatchSubtaskInputQueryBuilder
from src.core.tasks.url.operators.location_id.subtasks.models.subtask import AutoLocationIDSubtaskData
from src.core.tasks.url.operators.location_id.subtasks.templates.subtask import LocationIDSubtaskOperatorBase
from src.db.client.async_ import AsyncDatabaseClient


class NLPLocationFrequencySubtaskOperator(LocationIDSubtaskOperatorBase):

    def __init__(
        self,
        task_id: int,
        adb_client: AsyncDatabaseClient,
        nlp_processor: NLPProcessor,
    ):
        super().__init__(adb_client=adb_client, task_id=task_id)
        self._nlp_processor: NLPProcessor = nlp_processor
        self.processor = NLPLocationFrequencySubtaskInternalProcessor(
            nlp_processor=nlp_processor,
            adb_client=adb_client,
            task_id=task_id,
        )


    async def inner_logic(self) -> None:
        for iteration in range(ITERATIONS_PER_SUBTASK):
            inputs: list[NLPLocationMatchSubtaskInput] = await self._get_from_db()
            if len(inputs) == 0:
                break
            await self.run_subtask_iteration(inputs)

    async def run_subtask_iteration(self, inputs: list[NLPLocationMatchSubtaskInput]) -> None:
        self.linked_urls.extend([input_.url_id for input_ in inputs])
        subtask_data_list: list[AutoLocationIDSubtaskData] = await self._process_inputs(inputs)

        await self._upload_subtask_data(subtask_data_list)

    async def _process_inputs(
        self,
        inputs: list[NLPLocationMatchSubtaskInput]
    ) -> list[AutoLocationIDSubtaskData]:
        return await self.processor.process(
            inputs=inputs,
        )


    async def _get_from_db(self) -> list[NLPLocationMatchSubtaskInput]:
        return await self.adb_client.run_query_builder(
            GetNLPLocationMatchSubtaskInputQueryBuilder(),
        )

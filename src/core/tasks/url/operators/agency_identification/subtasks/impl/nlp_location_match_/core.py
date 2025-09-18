from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.constants import \
    ITERATIONS_PER_SUBTASK
from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.processor.core import \
    AgencyIDSubtaskInternalProcessor
from src.core.tasks.url.operators.agency_identification.subtasks.models.subtask import AutoAgencyIDSubtaskData
from src.core.tasks.url.operators.agency_identification.subtasks.templates.subtask import AgencyIDSubtaskOperatorBase
from src.core.tasks.url.operators.location_id.subtasks.impl.nlp_location_freq.models.input import \
    NLPLocationMatchSubtaskInput
from src.core.tasks.url.operators.location_id.subtasks.impl.nlp_location_freq.query import \
    GetNLPLocationMatchSubtaskInputQueryBuilder
from src.db.client.async_ import AsyncDatabaseClient


class NLPLocationMatchSubtaskOperator(AgencyIDSubtaskOperatorBase):

    def __init__(
        self,
        adb_client: AsyncDatabaseClient,
        task_id: int,
    ) -> None:
        super().__init__(adb_client, task_id=task_id)

    async def inner_logic(self) -> None:
        for iteration in range(ITERATIONS_PER_SUBTASK):
            inputs: list[NLPLocationMatchSubtaskInput] = await self._get_from_db()
            if len(inputs) == 0:
                break
            await self.run_subtask_iteration(inputs)

    async def run_subtask_iteration(self, inputs: list[NLPLocationMatchSubtaskInput]) -> None:
        self.linked_urls.extend([input_.url_id for input_ in inputs])
        subtask_data_list: list[AutoAgencyIDSubtaskData] = []

        # TODO: Get NLP Annotations

        # TODO: Process and Convert NLP Annotations

        # TODO: Resubmit NLP Annotations

        # TODO: For locations with no associated agencies, convert to subtask data with empty agencies
        subtask_data_no_agency_list: list[AutoAgencyIDSubtaskData] = \
            convert_empty_location_agency_mappings_to_subtask_data_list(
                mappings=nlp_response_subsets.invalid,
                task_id=self._task_id,
            )
        subtask_data_list.extend(subtask_data_no_agency_list)

        # For locations with agency mappings, convert to data with suggestions
        subtask_data_list_agency_list: list[AutoAgencyIDSubtaskData] = \
            convert_location_agency_mappings_to_subtask_data_list(
                mappings=response_mappings,
                task_id=self._task_id,
            )

        subtask_data_list.extend(subtask_data_list_agency_list)

        return subtask_data_list

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
            GetNLPLocationMatchSubtaskInputQueryBuilder(),
        )

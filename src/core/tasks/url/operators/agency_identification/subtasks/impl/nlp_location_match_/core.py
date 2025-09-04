from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.constants import \
    ITERATIONS_PER_SUBTASK
from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.convert import \
    convert_nlp_response_to_search_agency_by_location_params, convert_search_agency_responses_to_subtask_data_list
from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.models.input import \
    NLPLocationMatchSubtaskInput
from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.processor_.core import NLPProcessor
from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.processor_.models.response import \
    NLPLocationMatchResponse
from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.query import \
    GetNLPLocationMatchSubtaskInputQueryBuilder
from src.core.tasks.url.operators.agency_identification.subtasks.models.subtask import AutoAgencyIDSubtaskData
from src.core.tasks.url.operators.agency_identification.subtasks.templates.subtask import AgencyIDSubtaskOperatorBase
from src.db.client.async_ import AsyncDatabaseClient
from src.external.pdap.client import PDAPClient
from src.external.pdap.dtos.search_agency_by_location.params import SearchAgencyByLocationParams
from src.external.pdap.dtos.search_agency_by_location.response import SearchAgencyByLocationResponse


class NLPLocationMatchSubtaskOperator(AgencyIDSubtaskOperatorBase):

    def __init__(
        self,
        adb_client: AsyncDatabaseClient,
        task_id: int,
        pdap_client: PDAPClient,
        processor: NLPProcessor
    ) -> None:
        super().__init__(adb_client, task_id)
        self.processor = processor
        self.pdap_client = pdap_client

    async def inner_logic(self) -> None:
        for iteration in range(ITERATIONS_PER_SUBTASK):
            inputs: list[NLPLocationMatchSubtaskInput] = await self._get_from_db()
            if len(inputs) == 0:
                break
            await self.run_subtask_iteration(inputs)

    async def run_subtask_iteration(self, inputs: list[NLPLocationMatchSubtaskInput]) -> None:
        search_params: list[SearchAgencyByLocationParams] = []
        for input_ in inputs:
            nlp_response: NLPLocationMatchResponse = await self._get_location_match(input_.html)
            search_param: SearchAgencyByLocationParams = \
                convert_nlp_response_to_search_agency_by_location_params(
                    url_id=input_.url_id,
                    nlp_response=nlp_response,
                )
            search_params.append(search_param)

        search_responses: list[SearchAgencyByLocationResponse] = \
            await self._get_pdap_info(search_params)

        subtask_data_list: list[AutoAgencyIDSubtaskData] = \
            convert_search_agency_responses_to_subtask_data_list(
                responses=search_responses,
                task_id=self.task_id,
            )

        await self._upload_subtask_data(subtask_data_list)

    async def _get_from_db(self) -> list[NLPLocationMatchSubtaskInput]:
        return await self.adb_client.run_query_builder(
            query_builder=GetNLPLocationMatchSubtaskInputQueryBuilder(),
        )

    async def _get_pdap_info(
        self,
        params: list[SearchAgencyByLocationParams]
    ) -> list[SearchAgencyByLocationResponse]:
        return await self.pdap_client.search_agency_by_location(params)

    async def _get_location_match(
        self,
        html: str
    ) -> NLPLocationMatchResponse:
        return self.processor.parse_for_locations(html)

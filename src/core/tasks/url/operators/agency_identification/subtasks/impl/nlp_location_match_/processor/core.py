from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.processor.convert import \
    convert_nlp_response_to_search_agency_by_location_params, convert_search_agency_responses_to_subtask_data_list
from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.processor.counter import RequestCounter
from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.processor.mapper import \
    URLRequestIDMapper
from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.models.input import \
    NLPLocationMatchSubtaskInput
from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.processor.nlp.core import \
    NLPProcessor
from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.processor.nlp.models.response import \
    NLPLocationMatchResponse
from src.core.tasks.url.operators.agency_identification.subtasks.models.subtask import AutoAgencyIDSubtaskData
from src.external.pdap.client import PDAPClient
from src.external.pdap.dtos.search_agency_by_location.params import SearchAgencyByLocationParams
from src.external.pdap.dtos.search_agency_by_location.response import SearchAgencyByLocationResponse


class AgencyIDSubtaskInternalProcessor:

    def __init__(
        self,
        nlp_processor: NLPProcessor,
        pdap_client: PDAPClient,
        task_id: int,
    ):
        self._nlp_processor = nlp_processor
        self._pdap_client = pdap_client
        self._counter = RequestCounter()
        self._mapper = URLRequestIDMapper()
        self._task_id = task_id

    async def process(
        self, 
        inputs: list[NLPLocationMatchSubtaskInput]
    ) -> list[AutoAgencyIDSubtaskData]:
        
        search_params: list[SearchAgencyByLocationParams] = self._extract_search_params(
            inputs=inputs
        )

        search_responses: list[SearchAgencyByLocationResponse] = \
            await self._get_pdap_info(search_params)

        subtask_data_list: list[AutoAgencyIDSubtaskData] = \
            convert_search_agency_responses_to_subtask_data_list(
                responses=search_responses,
                task_id=self._task_id,
                mapper=self._mapper,
            )

        return subtask_data_list

    def _extract_search_params(
        self,
        inputs: list[NLPLocationMatchSubtaskInput]
    ) -> list[SearchAgencyByLocationParams]:
        """
        Modifies:
            - self._mapper
            - self._counter
        """
        all_search_params: list[SearchAgencyByLocationParams] = []
        for input_ in inputs:
            nlp_response: NLPLocationMatchResponse = self._get_location_match(input_.html)
            search_params: list[
                SearchAgencyByLocationParams] = convert_nlp_response_to_search_agency_by_location_params(
                counter=self._counter,
                nlp_response=nlp_response,
            )
            for search_param in search_params:
                self._mapper.add_mapping(
                    request_id=search_param.request_id,
                    url_id=input_.url_id,
                )
                search_params.append(search_param)
            all_search_params.extend(search_params)
        return all_search_params

    def _get_location_match(
        self,
        html: str
    ) -> NLPLocationMatchResponse:
        return self._nlp_processor.parse_for_locations(html)

    async def _get_pdap_info(
        self,
        params: list[SearchAgencyByLocationParams]
    ) -> list[SearchAgencyByLocationResponse]:
        return await self._pdap_client.search_agency_by_location(params)

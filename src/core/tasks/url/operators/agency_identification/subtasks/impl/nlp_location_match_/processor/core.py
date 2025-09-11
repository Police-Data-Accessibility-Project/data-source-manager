from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.processor.convert import \
    convert_nlp_response_to_search_agency_by_location_params, convert_search_agency_responses_to_subtask_data_list
from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.processor.counter import RequestCounter
from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.processor.extract import \
    _extract_all_search_params
from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.processor.mapper import \
    URLRequestIDMapper
from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.models.input import \
    NLPLocationMatchSubtaskInput
from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.processor.models.mappings.url_id_nlp_response import \
    URLToNLPResponseMapping
from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.processor.models.mappings.url_id_search_params import \
    URLToSearchParamsMapping
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
        
        url_search_param_mappings: list[URLToSearchParamsMapping] = self._extract_search_params(
            inputs=inputs
        )

        # Filter out empty params
        url_search_param_mappings_empty: list[URLToSearchParamsMapping] = \
            [mapping for mapping in url_search_param_mappings if mapping.is_empty]

        # Convert empty params to subtask data with empty agencies
        subtask_data_no_agency_list: list[AutoAgencyIDSubtaskData] = \
            convert_empty_url_search_param_mappings_to_subtask_data_list(
                responses=[],
                task_id=self._task_id,
                mapper=self._mapper,
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
    ) -> list[URLToSearchParamsMapping]:
        """
        Modifies:
            - self._mapper
            - self._counter
        """

        url_to_nlp_mappings: list[URLToNLPResponseMapping] = \
            self._match_urls_to_nlp_responses(inputs)

        url_to_search_params_mappings: list[URLToSearchParamsMapping] = \
            self._match_urls_to_search_params(url_to_nlp_mappings)

        return url_to_search_params_mappings

    def _add_all_url_search_param_mappings(
        self,
        url_to_search_params_mappings: list[URLToSearchParamsMapping]
    ) -> None:
        """
        Modifies:
            - self._mapper
        """
        for mapping in url_to_search_params_mappings:
            for search_param in mapping.search_params:
                self._mapper.add_mapping(
                    request_id=search_param.request_id,
                    url_id=mapping.url_id,
                )

    def _match_urls_to_search_params(
        self,
        url_to_nlp_mappings: list[URLToNLPResponseMapping]
    ) -> list[URLToSearchParamsMapping]:
        """
        Modifies:
            - self._counter
        """
        url_to_search_params_mappings: list[URLToSearchParamsMapping] = []
        for mapping in url_to_nlp_mappings:
            search_params: list[SearchAgencyByLocationParams] = \
                convert_nlp_response_to_search_agency_by_location_params(
                    counter=self._counter,
                    nlp_response=mapping.nlp_response,
                )
            mapping = URLToSearchParamsMapping(
                url_id=mapping.url_id,
                search_params=search_params,
            )
            url_to_search_params_mappings.append(mapping)
        return url_to_search_params_mappings

    def _match_urls_to_nlp_responses(
        self,
        inputs: list[NLPLocationMatchSubtaskInput]
    ) -> list[URLToNLPResponseMapping]:
        url_to_nlp_mappings: list[URLToNLPResponseMapping] = []
        for input_ in inputs:
            nlp_response: NLPLocationMatchResponse = self._get_location_match(input_.html)
            mapping = URLToNLPResponseMapping(
                url_id=input_.url_id,
                nlp_response=nlp_response,
            )
            url_to_nlp_mappings.append(mapping)
        return url_to_nlp_mappings

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

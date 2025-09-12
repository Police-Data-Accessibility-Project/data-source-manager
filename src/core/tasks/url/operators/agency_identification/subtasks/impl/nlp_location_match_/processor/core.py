from collections import defaultdict

from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.models.input import \
    NLPLocationMatchSubtaskInput
from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.processor.convert import \
    convert_search_agency_responses_to_subtask_data_list, \
    convert_invalid_url_nlp_mappings_to_subtask_data_list, convert_urls_to_search_params
from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.processor.filter import \
    filter_valid_and_invalid_nlp_responses, filter_top_n_suggestions
from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.processor.mapper import \
    URLRequestIDMapper
from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.processor.models.mappings.url_id_nlp_response import \
    URLToNLPResponseMapping
from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.processor.models.mappings.url_id_search_params import \
    URLToSearchParamsMapping
from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.processor.models.mappings.url_id_search_response import \
    URLToSearchResponseMapping
from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.processor.models.subsets.nlp_responses import \
    NLPResponseSubsets
from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.processor.nlp.core import \
    NLPProcessor
from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.processor.nlp.models.response import \
    NLPLocationMatchResponse
from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.processor.nlp.preprocess import \
    preprocess_html
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
        self._task_id = task_id

    async def process(
        self, 
        inputs: list[NLPLocationMatchSubtaskInput]
    ) -> list[AutoAgencyIDSubtaskData]:
        subtask_data_list: list[AutoAgencyIDSubtaskData] = []

        url_to_nlp_mappings: list[URLToNLPResponseMapping] = \
            self._match_urls_to_nlp_responses(inputs)

        # Filter out valid and invalid NLP responses
        nlp_response_subsets: NLPResponseSubsets = \
            filter_valid_and_invalid_nlp_responses(url_to_nlp_mappings)

        # For invalid responses, convert to subtask data with empty agencies
        subtask_data_no_agency_list: list[AutoAgencyIDSubtaskData] = \
            convert_invalid_url_nlp_mappings_to_subtask_data_list(
                mappings=nlp_response_subsets.invalid,
                task_id=self._task_id,
            )
        subtask_data_list.extend(subtask_data_no_agency_list)

        # For valid responses, convert to search param mappings
        url_to_search_params_mappings: list[URLToSearchParamsMapping] = \
            convert_urls_to_search_params(nlp_response_subsets.valid)


        response_mappings: list[URLToSearchResponseMapping] = \
            await self._get_pdap_info(url_to_search_params_mappings)

        subtask_data_list_agency_list: list[AutoAgencyIDSubtaskData] = \
            convert_search_agency_responses_to_subtask_data_list(
                mappings=response_mappings,
                task_id=self._task_id,
            )

        filter_top_n_suggestions(subtask_data_list_agency_list)

        subtask_data_list.extend(subtask_data_list_agency_list)

        return subtask_data_list

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
        preprocessed_html: str = preprocess_html(html)
        return self._nlp_processor.parse_for_locations(preprocessed_html)

    async def _get_pdap_info(
        self,
        mappings: list[URLToSearchParamsMapping]
    ) -> list[URLToSearchResponseMapping]:
        if len(mappings) == 0:
            return []
        params: list[SearchAgencyByLocationParams] = []
        # Map request IDs to URL IDs for later use
        mapper = URLRequestIDMapper()
        for mapping in mappings:
            for search_param in mapping.search_params:
                mapper.add_mapping(
                    request_id=search_param.request_id,
                    url_id=mapping.url_id,
                )
                params.append(search_param)

        url_id_to_search_responses: dict[int, list[SearchAgencyByLocationResponse]] = defaultdict(list)

        responses: list[SearchAgencyByLocationResponse] = await self._pdap_client.search_agency_by_location(params)
        # Map responses to URL IDs via request IDs
        for response in responses:
            request_id: int = response.request_id
            url_id: int = mapper.get_url_id_by_request_id(request_id)
            url_id_to_search_responses[url_id].append(response)

        # Reconcile URL IDs to search responses
        response_mappings: list[URLToSearchResponseMapping] = []
        for url_id, responses in url_id_to_search_responses.items():
            mapping = URLToSearchResponseMapping(
                url_id=url_id,
                search_responses=responses,
            )
            response_mappings.append(mapping)

        return response_mappings



from math import ceil

from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.processor.constants import \
    MAX_NLP_CONFIDENCE
from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.processor.counter import \
    RequestCounter
from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.processor.models.mappings.url_id_nlp_response import \
    URLToNLPResponseMapping
from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.processor.models.mappings.url_id_search_params import \
    URLToSearchParamsMapping
from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.processor.models.mappings.url_id_search_response import \
    URLToSearchResponseMapping
from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.processor.nlp.models.response import \
    NLPLocationMatchResponse
from src.core.tasks.url.operators.agency_identification.subtasks.models.subtask import AutoAgencyIDSubtaskData
from src.core.tasks.url.operators.agency_identification.subtasks.models.suggestion import AgencySuggestion
from src.db.models.impl.url.suggestion.agency.subtask.enum import AutoAgencyIDSubtaskType
from src.db.models.impl.url.suggestion.agency.subtask.pydantic import URLAutoAgencyIDSubtaskPydantic
from src.external.pdap.dtos.search_agency_by_location.params import SearchAgencyByLocationParams
from src.external.pdap.dtos.search_agency_by_location.response import SearchAgencyByLocationResponse


def convert_nlp_response_to_search_agency_by_location_params(
    nlp_response: NLPLocationMatchResponse,
    counter: RequestCounter
) -> list[SearchAgencyByLocationParams]:
    params: list[SearchAgencyByLocationParams] = []
    for location in nlp_response.locations:
        if nlp_response.us_state is None:
            raise ValueError("US State is None; cannot convert NLP response to search agency by location params")
        request_id: int = counter.next()
        param = SearchAgencyByLocationParams(
            request_id=request_id,
            query=location,
            iso=nlp_response.us_state.iso,
        )
        params.append(param)

    return params



def convert_search_agency_responses_to_subtask_data_list(
    mappings: list[URLToSearchResponseMapping],
    task_id: int
) -> list[AutoAgencyIDSubtaskData]:
    subtask_data_list: list[AutoAgencyIDSubtaskData] = []

    # First, extract agency suggestions for URL
    for mapping in mappings:
        url_id: int = mapping.url_id
        search_responses: list[SearchAgencyByLocationResponse] = mapping.search_responses
        suggestions: list[AgencySuggestion] = _convert_search_agency_response_to_agency_suggestions(
            search_responses
        )
        pydantic_model: URLAutoAgencyIDSubtaskPydantic = convert_search_agency_response_to_subtask_pydantic(
            url_id=url_id,
            task_id=task_id
        )
        subtask_data = AutoAgencyIDSubtaskData(
            pydantic_model=pydantic_model,
            suggestions=suggestions
        )
        subtask_data_list.append(subtask_data)

    return subtask_data_list


def _convert_search_agency_response_to_agency_suggestions(
    responses: list[SearchAgencyByLocationResponse],
) -> list[AgencySuggestion]:
    suggestions: list[AgencySuggestion] = []
    for response in responses:
        for result in response.results:
            agency_id: int = result.agency_id
            similarity: float = result.similarity
            confidence: int = min(ceil(similarity * 100), MAX_NLP_CONFIDENCE)
            suggestion: AgencySuggestion = AgencySuggestion(
                agency_id=agency_id,
                confidence=confidence,
            )
            suggestions.append(suggestion)
    return suggestions

def convert_url_ids_to_empty_subtask_data_list(
    url_ids: list[int],
    task_id: int
) -> list[AutoAgencyIDSubtaskData]:
    results: list[AutoAgencyIDSubtaskData] = []
    for url_id in url_ids:
        subtask_data = AutoAgencyIDSubtaskData(
            pydantic_model=URLAutoAgencyIDSubtaskPydantic(
                task_id=task_id,
                url_id=url_id,
                type=AutoAgencyIDSubtaskType.NLP_LOCATION_MATCH,
                agencies_found=False
            ),
            suggestions=[]
        )
        results.append(subtask_data)

    return results



def convert_empty_url_search_param_mappings_to_subtask_data_list(
    mappings: list[URLToSearchParamsMapping],
    task_id: int
) -> list[AutoAgencyIDSubtaskData]:
    url_ids: list[int] = []
    for mapping in mappings:
        url_ids.append(mapping.url_id)

    return convert_url_ids_to_empty_subtask_data_list(
        url_ids=url_ids,
        task_id=task_id
    )

def convert_invalid_url_nlp_mappings_to_subtask_data_list(
    mappings: list[URLToNLPResponseMapping],
    task_id: int
) -> list[AutoAgencyIDSubtaskData]:
    url_ids: list[int] = []
    for mapping in mappings:
        url_ids.append(mapping.url_id)

    return convert_url_ids_to_empty_subtask_data_list(
        url_ids=url_ids,
        task_id=task_id
    )


def convert_search_agency_response_to_subtask_pydantic(
    url_id: int,
    task_id: int
) -> URLAutoAgencyIDSubtaskPydantic:

    return URLAutoAgencyIDSubtaskPydantic(
        task_id=task_id,
        url_id=url_id,
        type=AutoAgencyIDSubtaskType.NLP_LOCATION_MATCH,
        agencies_found=True
    )


def convert_urls_to_search_params(
    url_to_nlp_mappings: list[URLToNLPResponseMapping]
) -> list[URLToSearchParamsMapping]:
    url_to_search_params_mappings: list[URLToSearchParamsMapping] = []
    counter = RequestCounter()
    for mapping in url_to_nlp_mappings:
        search_params: list[SearchAgencyByLocationParams] = \
            convert_nlp_response_to_search_agency_by_location_params(
                counter=counter,
                nlp_response=mapping.nlp_response,
            )
        mapping = URLToSearchParamsMapping(
            url_id=mapping.url_id,
            search_params=search_params,
        )
        url_to_search_params_mappings.append(mapping)
    return url_to_search_params_mappings

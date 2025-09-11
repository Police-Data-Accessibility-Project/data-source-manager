from collections import defaultdict
from math import ceil

from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.processor.counter import RequestCounter
from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.processor.mapper import \
    URLRequestIDMapper
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
        if nlp_response.us_state is not None:
            query: str = f"{location}, {nlp_response.us_state.name}"
        else:
            query: str = location
        request_id: int = counter.next()
        param = SearchAgencyByLocationParams(
            request_id=request_id,
            query=query
        )
        params.append(param)

    return params



def convert_search_agency_responses_to_subtask_data_list(
    mapper: URLRequestIDMapper,
    responses: list[SearchAgencyByLocationResponse],
    task_id: int
) -> list[AutoAgencyIDSubtaskData]:
    subtask_data_list: list[AutoAgencyIDSubtaskData] = []
    url_id_to_suggestions: dict[int, list[AgencySuggestion]] = defaultdict(list)

    # First, extract agency suggestions for URL
    for response in responses:
        suggestions: list[AgencySuggestion] = _convert_search_agency_response_to_agency_suggestions(response)
        url_id: int = mapper.get_url_id_by_request_id(response.request_id)
        url_id_to_suggestions[url_id].extend(suggestions)

    # Then, construct subtask data and
    for url_id, suggestions in url_id_to_suggestions.items():
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
    response: SearchAgencyByLocationResponse,
) -> list[AgencySuggestion]:
    suggestions: list[AgencySuggestion] = []
    for result in response.results:
        agency_id: int = result.agency_id
        similarity: float = result.similarity
        confidence: int = ceil(similarity * 100)
        suggestion: AgencySuggestion = AgencySuggestion(
            agency_id=agency_id,
            confidence=confidence,
        )
        suggestions.append(suggestion)
    return suggestions



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

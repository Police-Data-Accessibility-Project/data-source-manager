from math import ceil

from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.processor_.models.response import \
    NLPLocationMatchResponse
from src.core.tasks.url.operators.agency_identification.subtasks.models.subtask import AutoAgencyIDSubtaskData
from src.core.tasks.url.operators.agency_identification.subtasks.models.suggestion import AgencySuggestion
from src.db.models.impl.url.suggestion.agency.subtask.enum import AutoAgencyIDSubtaskType
from src.db.models.impl.url.suggestion.agency.subtask.pydantic import URLAutoAgencyIDSubtaskPydantic
from src.external.pdap.dtos.search_agency_by_location.params import SearchAgencyByLocationParams
from src.external.pdap.dtos.search_agency_by_location.response import SearchAgencyByLocationResponse


def convert_nlp_response_to_search_agency_by_location_params(
    url_id: int,
    nlp_response: NLPLocationMatchResponse,
) -> SearchAgencyByLocationParams:
    return SearchAgencyByLocationParams(
        request_id=url_id,
        locations=nlp_response.locations,
        state_iso=nlp_response.us_state.iso,
    )

def convert_search_agency_responses_to_subtask_data_list(
    responses: list[SearchAgencyByLocationResponse],
    task_id: int
) -> list[AutoAgencyIDSubtaskData]:
    subtask_data_list: list[AutoAgencyIDSubtaskData] = []
    for response in responses:
        subtask_data: AutoAgencyIDSubtaskData = \
            convert_search_agency_response_to_subtask_data(
                response=response,
                task_id=task_id,
            )
        subtask_data_list.append(subtask_data)
    return subtask_data_list

def convert_search_agency_response_to_subtask_data(
    response: SearchAgencyByLocationResponse,
    task_id: int
) -> AutoAgencyIDSubtaskData:
    suggestions: list[AgencySuggestion] = []
    url_id: int = response.request_id
    for result in response.results:
        agency_id: int = result.agency_id
        similarity: float = result.similarity
        confidence: int = ceil(similarity * 100)
        suggestion: AgencySuggestion = AgencySuggestion(
            agency_id=agency_id,
            confidence=confidence,
        )
        suggestions.append(suggestion)

    pydantic_model = URLAutoAgencyIDSubtaskPydantic(
        task_id=task_id,
        url_id=url_id,
        subtask=AutoAgencyIDSubtaskType.NLP_LOCATION_MATCH,
        agencies_found=len(suggestions) > 0
    )
    return AutoAgencyIDSubtaskData(
        pydantic_model=pydantic_model,
        suggestions=suggestions
    )
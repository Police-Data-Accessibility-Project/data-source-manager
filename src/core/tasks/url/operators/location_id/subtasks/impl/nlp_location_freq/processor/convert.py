from math import ceil

from src.core.tasks.url.operators.location_id.subtasks.impl.nlp_location_freq.models.mappings.url_id_nlp_response import \
    URLToNLPResponseMapping
from src.core.tasks.url.operators.location_id.subtasks.impl.nlp_location_freq.models.mappings.url_id_search_response import \
    URLToSearchResponseMapping
from src.core.tasks.url.operators.location_id.subtasks.impl.nlp_location_freq.processor.constants import \
    MAX_NLP_CONFIDENCE
from src.core.tasks.url.operators.location_id.subtasks.impl.nlp_location_freq.processor.counter import RequestCounter
from src.core.tasks.url.operators.location_id.subtasks.impl.nlp_location_freq.processor.models.url_id_search_params import \
    URLToSearchParamsMapping
from src.core.tasks.url.operators.location_id.subtasks.impl.nlp_location_freq.processor.nlp.models.response import \
    NLPLocationMatchResponse
from src.core.tasks.url.operators.location_id.subtasks.impl.nlp_location_freq.processor.query_.models.params import \
    SearchSimilarLocationsParams
from src.core.tasks.url.operators.location_id.subtasks.impl.nlp_location_freq.processor.query_.models.response import \
    SearchSimilarLocationsResponse
from src.core.tasks.url.operators.location_id.subtasks.models.subtask import AutoLocationIDSubtaskData
from src.core.tasks.url.operators.location_id.subtasks.models.suggestion import LocationSuggestion
from src.db.models.impl.url.suggestion.location.auto.subtask.enums import LocationIDSubtaskType
from src.db.models.impl.url.suggestion.location.auto.subtask.pydantic import AutoLocationIDSubtaskPydantic


def convert_invalid_url_nlp_mappings_to_subtask_data_list(
    mappings: list[URLToNLPResponseMapping],
    task_id: int
) -> list[AutoLocationIDSubtaskData]:
    url_ids: list[int] = []
    for mapping in mappings:
        url_ids.append(mapping.url_id)

    return convert_url_ids_to_empty_subtask_data_list(
        url_ids=url_ids,
        task_id=task_id
    )

def convert_url_ids_to_empty_subtask_data_list(
    url_ids: list[int],
    task_id: int
) -> list[AutoLocationIDSubtaskData]:
    results: list[AutoLocationIDSubtaskData] = []
    for url_id in url_ids:
        subtask_data = AutoLocationIDSubtaskData(
            pydantic_model=AutoLocationIDSubtaskPydantic(
                task_id=task_id,
                url_id=url_id,
                type=LocationIDSubtaskType.NLP_LOCATION_FREQUENCY,
                locations_found=False
            ),
            suggestions=[]
        )
        results.append(subtask_data)

    return results

def convert_search_location_responses_to_subtask_data_list(
    mappings: list[URLToSearchResponseMapping],
    task_id: int
) -> list[AutoLocationIDSubtaskData]:
    subtask_data_list: list[AutoLocationIDSubtaskData] = []

    # First, extract agency suggestions for URL
    for mapping in mappings:
        url_id: int = mapping.url_id
        search_responses: list[SearchSimilarLocationsResponse] = mapping.search_responses
        suggestions: list[LocationSuggestion] = _convert_search_agency_response_to_agency_suggestions(
            search_responses
        )
        pydantic_model: AutoLocationIDSubtaskPydantic = convert_search_agency_response_to_subtask_pydantic(
            url_id=url_id,
            task_id=task_id,
            suggestions=suggestions
        )
        subtask_data = AutoLocationIDSubtaskData(
            pydantic_model=pydantic_model,
            suggestions=suggestions
        )
        subtask_data_list.append(subtask_data)

    return subtask_data_list

def convert_search_agency_response_to_subtask_pydantic(
    url_id: int,
    task_id: int,
    suggestions: list[LocationSuggestion]
) -> AutoLocationIDSubtaskPydantic:

    return AutoLocationIDSubtaskPydantic(
        task_id=task_id,
        url_id=url_id,
        type=LocationIDSubtaskType.NLP_LOCATION_FREQUENCY,
        locations_found=len(suggestions) > 0,
    )

def _convert_search_agency_response_to_agency_suggestions(
    responses: list[SearchSimilarLocationsResponse],
) -> list[LocationSuggestion]:
    suggestions: list[LocationSuggestion] = []
    for response in responses:
        for result in response.results:
            location_id: int = result.location_id
            similarity: float = result.similarity
            confidence: int = min(ceil(similarity * 100), MAX_NLP_CONFIDENCE)
            suggestion: LocationSuggestion = LocationSuggestion(
                location_id=location_id,
                confidence=confidence,
            )
            suggestions.append(suggestion)
    return suggestions



def convert_urls_to_search_params(
    url_to_nlp_mappings: list[URLToNLPResponseMapping]
) -> list[URLToSearchParamsMapping]:
    url_to_search_params_mappings: list[URLToSearchParamsMapping] = []
    counter = RequestCounter()
    for mapping in url_to_nlp_mappings:
        search_params: list[SearchSimilarLocationsParams] = \
            convert_nlp_response_to_search_similar_location_params(
                counter=counter,
                nlp_response=mapping.nlp_response,
            )
        mapping = URLToSearchParamsMapping(
            url_id=mapping.url_id,
            search_params=search_params,
        )
        url_to_search_params_mappings.append(mapping)
    return url_to_search_params_mappings


def convert_nlp_response_to_search_similar_location_params(
    nlp_response: NLPLocationMatchResponse,
    counter: RequestCounter
) -> list[SearchSimilarLocationsParams]:
    params: list[SearchSimilarLocationsParams] = []
    for location in nlp_response.locations:
        if nlp_response.us_state is None:
            raise ValueError("US State is None; cannot convert NLP response to search agency by location params")
        request_id: int = counter.next()
        param = SearchSimilarLocationsParams(
            request_id=request_id,
            query=location,
            iso=nlp_response.us_state.iso,
        )
        params.append(param)

    return params


from src.core.tasks.url.operators.agency_identification.subtasks.impl.homepage_match_.models.entry import \
    GetHomepageMatchParams
from src.core.tasks.url.operators.agency_identification.subtasks.impl.homepage_match_.models.mapping import \
    SubtaskURLMapping
from src.db.models.impl.url.suggestion.agency.subtask.enum import SubtaskDetailCode, AutoAgencyIDSubtaskType
from src.db.models.impl.url.suggestion.agency.subtask.pydantic import URLAutoAgencyIDSubtaskPydantic
from src.db.models.impl.url.suggestion.agency.suggestion.pydantic import AgencyIDSubtaskSuggestionPydantic


def convert_params_to_subtask_entries(
    params: list[GetHomepageMatchParams],
    task_id: int
) -> list[URLAutoAgencyIDSubtaskPydantic]:
    url_id_to_detail_code: dict[int, SubtaskDetailCode] = {}
    for param in params:
        url_id_to_detail_code[param.url_id] = param.detail_code

    results: list[URLAutoAgencyIDSubtaskPydantic] = []
    for url_id, detail_code in url_id_to_detail_code.items():
        result = URLAutoAgencyIDSubtaskPydantic(
            task_id=task_id,
            url_id=url_id,
            type=AutoAgencyIDSubtaskType.HOMEPAGE_MATCH,
            agencies_found=True,
            detail=detail_code,
        )
        results.append(result)
    return results

def convert_subtask_mappings_and_params_to_suggestions(
    mappings: list[SubtaskURLMapping],
    params: list[GetHomepageMatchParams]
) -> list[AgencyIDSubtaskSuggestionPydantic]:
    url_id_to_subtask_id: dict[int, int] = {
        mapping.url_id: mapping.subtask_id
        for mapping in mappings
    }
    suggestions: list[AgencyIDSubtaskSuggestionPydantic] = []
    for param in params:
        subtask_id = url_id_to_subtask_id.get(param.url_id)
        suggestion = AgencyIDSubtaskSuggestionPydantic(
            subtask_id=subtask_id,
            agency_id=param.agency_id,
            confidence=param.confidence,
        )
        suggestions.append(suggestion)
    return suggestions
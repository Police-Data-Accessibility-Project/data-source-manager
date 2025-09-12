from src.core.tasks.url.operators.agency_identification.subtasks.models.subtask import AutoAgencyIDSubtaskData
from src.core.tasks.url.operators.agency_identification.subtasks.models.suggestion import AgencySuggestion
from src.db.models.impl.url.suggestion.agency.subtask.enum import AutoAgencyIDSubtaskType
from src.db.models.impl.url.suggestion.agency.subtask.pydantic import URLAutoAgencyIDSubtaskPydantic
from src.external.pdap.dtos.match_agency.post import MatchAgencyInfo
from src.external.pdap.dtos.match_agency.response import MatchAgencyResponse
from src.external.pdap.enums import MatchAgencyResponseStatus

def convert_match_agency_response_to_subtask_data(
    url_id: int,
    response: MatchAgencyResponse,
    subtask_type: AutoAgencyIDSubtaskType,
    task_id: int
):
    suggestions: list[AgencySuggestion] = \
        _convert_match_agency_response_to_suggestions(
            response
        )
    agencies_found: bool = len(suggestions) > 0
    subtask_pydantic = URLAutoAgencyIDSubtaskPydantic(
        url_id=url_id,
        type=subtask_type,
        agencies_found=agencies_found,
        task_id=task_id
    )
    return AutoAgencyIDSubtaskData(
        pydantic_model=subtask_pydantic,
        suggestions=suggestions
    )

def _convert_match_agency_response_to_suggestions(
    match_response: MatchAgencyResponse,
) -> list[AgencySuggestion]:
    if match_response.status == MatchAgencyResponseStatus.EXACT_MATCH:
        match_info: MatchAgencyInfo = match_response.matches[0]
        return [
            AgencySuggestion(
                agency_id=int(match_info.id),
                confidence=100
            )
        ]
    if match_response.status == MatchAgencyResponseStatus.NO_MATCH:
        return []
    if match_response.status != MatchAgencyResponseStatus.PARTIAL_MATCH:
        raise ValueError(f"Unknown Match Agency Response Status: {match_response.status}")
    total_confidence: int = 100
    confidence_per_match: int = total_confidence // len(match_response.matches)
    return [
        AgencySuggestion(
            agency_id=int(match_info.id),
            confidence=confidence_per_match
        )
        for match_info in match_response.matches
    ]
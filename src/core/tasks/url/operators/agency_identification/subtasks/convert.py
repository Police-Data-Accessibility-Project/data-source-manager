from src.core.tasks.url.operators.agency_identification.subtasks.models.subtask import AutoAgencyIDSubtaskData
from src.core.tasks.url.operators.agency_identification.subtasks.models.suggestion import AgencySuggestion
from src.db.models.impl.url.suggestion.agency.subtask.enum import AutoAgencyIDSubtaskType
from src.db.models.impl.url.suggestion.agency.subtask.pydantic import URLAutoAgencyIDSubtaskPydantic


def convert_agency_suggestions_to_subtask_data(
    url_id: int,
    agency_suggestions: list[AgencySuggestion],
    subtask_type: AutoAgencyIDSubtaskType,
    task_id: int,
) -> AutoAgencyIDSubtaskData:
    agencies_found: bool = len(agency_suggestions) > 0
    subtask_pydantic = URLAutoAgencyIDSubtaskPydantic(
        url_id=url_id,
        type=subtask_type,
        agencies_found=agencies_found,
        task_id=task_id
    )
    return AutoAgencyIDSubtaskData(
        pydantic_model=subtask_pydantic,
        suggestions=agency_suggestions
    )


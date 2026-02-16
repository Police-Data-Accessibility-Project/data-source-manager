from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.models.input import \
    NLPLocationMatchSubtaskInput
from src.core.tasks.url.operators.agency_identification.subtasks.models.subtask import AutoAgencyIDSubtaskData
from src.core.tasks.url.operators.agency_identification.subtasks.models.suggestion import AgencySuggestion
from src.db.models.impl.annotation.agency.auto.subtask.enum import AutoAgencyIDSubtaskType
from src.db.models.impl.annotation.agency.auto.subtask.pydantic import URLAutoAgencyIDSubtaskPydantic


def convert_location_agency_mappings_to_subtask_data_list(
    task_id: int,
    inputs: list[NLPLocationMatchSubtaskInput]
) -> list[AutoAgencyIDSubtaskData]:
    results: list[AutoAgencyIDSubtaskData] = []
    for input_ in inputs:
        suggestions: list[AgencySuggestion] = []
        if not input_.has_locations_with_agencies:
            agencies_found: bool = False
        else:
            agencies_found: bool = True
            for mapping in input_.mappings:
                agency_ids: list[int] = mapping.agency_ids
                confidence_per_agency: int = _calculate_confidence_per_agency(
                    agency_ids,
                    confidence=mapping.location_annotation.confidence
                )
                for agency_id in agency_ids:
                    suggestion = AgencySuggestion(
                        agency_id=agency_id,
                        confidence=confidence_per_agency,
                    )
                    suggestions.append(suggestion)
        data = AutoAgencyIDSubtaskData(
            pydantic_model=URLAutoAgencyIDSubtaskPydantic(
                url_id=input_.url_id,
                type=AutoAgencyIDSubtaskType.NLP_LOCATION_MATCH,
                agencies_found=agencies_found,
                task_id=task_id,
            ),
            suggestions=suggestions,
        )
        results.append(data)
    return results


def _calculate_confidence_per_agency(agency_ids: list[int], confidence: int):
    num_agencies: int = len(agency_ids)
    confidence_per_agency: int = confidence // num_agencies
    return confidence_per_agency


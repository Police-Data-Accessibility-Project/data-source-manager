from src.db.models.impl.url.suggestion.agency.subtask.enum import AutoAgencyIDSubtaskType

# Determines priority of subtasks, all else being equal.
SUBTASK_HIERARCHY: list[AutoAgencyIDSubtaskType] = [
    AutoAgencyIDSubtaskType.CKAN,
    AutoAgencyIDSubtaskType.MUCKROCK,
    AutoAgencyIDSubtaskType.HOMEPAGE_MATCH,
    AutoAgencyIDSubtaskType.NLP_LOCATION_MATCH
]

SUBTASK_HIERARCHY_MAPPING: dict[AutoAgencyIDSubtaskType, int] = {
    subtask: idx
    for idx, subtask in enumerate(SUBTASK_HIERARCHY)
}
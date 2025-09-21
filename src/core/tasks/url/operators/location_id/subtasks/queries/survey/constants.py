# Determines priority of subtasks, all else being equal.
from src.db.models.impl.url.suggestion.location.auto.subtask.enums import LocationIDSubtaskType

SUBTASK_HIERARCHY: list[LocationIDSubtaskType] = [
    LocationIDSubtaskType.NLP_LOCATION_FREQUENCY,
]

SUBTASK_HIERARCHY_MAPPING: dict[LocationIDSubtaskType, int] = {
    subtask: idx
    for idx, subtask in enumerate(SUBTASK_HIERARCHY)
}
from src.core.tasks.url.operators.agency_identification.subtasks.planner.constants import SUBTASK_HIERARCHY
from src.db.models.impl.url.suggestion.agency.subtask.enum import AutoAgencyIDSubtaskType

# TODO: Add test to confirm expected behavior
async def reconcile_tiebreakers(
    subtasks: list[AutoAgencyIDSubtaskType]
) -> AutoAgencyIDSubtaskType:
    """In the case of multiple subtasks being applicable,
    determine which one to run based on priority."""

    # TODO: Figure out why type hints are mismatched with this
    rank: dict[AutoAgencyIDSubtaskType, int] = {
        subtask: rank
        for rank, subtask in enumerate(SUBTASK_HIERARCHY)
    }

    def key(subtask: AutoAgencyIDSubtaskType) -> tuple[int, str]:
        r = rank.get(subtask, None)
        if r is None:
            raise ValueError(f"Subtask {subtask} not found in hierarchy")
        return r, subtask.value

    return min(subtasks, key=key)

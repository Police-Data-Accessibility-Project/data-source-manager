from environs import Env

from src.core.tasks.url.operators.location_id.subtasks.flags.mappings import SUBTASK_TO_ENV_FLAG
from src.db.models.impl.url.suggestion.location.auto.subtask.enums import LocationIDSubtaskType


class SubtaskFlagger:
    """
    Manages flags allowing and disallowing subtasks
    """
    def __init__(self):
        self.env = Env()

    def _get_subtask_flag(self, subtask_type: LocationIDSubtaskType) -> bool:
        return self.env.bool(
            SUBTASK_TO_ENV_FLAG[subtask_type],
            default=True
        )

    def get_allowed_subtasks(self) -> list[LocationIDSubtaskType]:
        return [
            subtask_type
            for subtask_type, flag in SUBTASK_TO_ENV_FLAG.items()
            if self._get_subtask_flag(subtask_type)
        ]
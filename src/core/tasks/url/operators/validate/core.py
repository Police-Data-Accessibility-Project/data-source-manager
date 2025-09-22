from src.core.tasks.url.operators.base import URLTaskOperatorBase
from src.db.enums import TaskType


class AutoValidateURLTaskOperator(URLTaskOperatorBase):

    @property
    def task_type(self) -> TaskType:
        return TaskType.AUTO_VALIDATE

    async def meets_task_prerequisites(self) -> bool:
        raise NotImplementedError

    async def inner_task_logic(self) -> None:
        # TODO (SM422): Implement

        # Get URLs for auto validation

        # TODO: Sort URLs according to URL type, and apply appropriate validations

        # Link

        # Add Validation Objects (Flag and ValidationType)

        raise NotImplementedError
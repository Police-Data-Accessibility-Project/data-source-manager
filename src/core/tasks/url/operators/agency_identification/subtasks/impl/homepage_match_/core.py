from src.core.tasks.url.operators.agency_identification.subtasks.templates.subtask import AgencyIDSubtaskOperatorBase


class HomepageMatchSubtaskOperator(AgencyIDSubtaskOperatorBase):

    async def inner_logic(self) -> None:
        raise NotImplementedError()
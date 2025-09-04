from src.core.tasks.url.operators.agency_identification.exceptions import SubtaskError
from src.core.tasks.url.operators.agency_identification.subtasks.loader import AgencyIdentificationSubtaskLoader
from src.core.tasks.url.operators.agency_identification.subtasks.models.run_info import AgencyIDSubtaskRunInfo
from src.core.tasks.url.operators.agency_identification.subtasks.planner.core import AgencyIDSubtaskPlanner
from src.core.tasks.url.operators.agency_identification.subtasks.templates.subtask import AgencyIDSubtaskOperatorBase
from src.core.tasks.url.operators.base import URLTaskOperatorBase
from src.db.client.async_ import AsyncDatabaseClient
from src.db.enums import TaskType
from src.db.models.impl.url.suggestion.agency.subtask.enum import AutoAgencyIDSubtaskType


class AgencyIdentificationTaskOperator(URLTaskOperatorBase):

    def __init__(
            self,
            adb_client: AsyncDatabaseClient,
            loader: AgencyIdentificationSubtaskLoader,
            planner: AgencyIDSubtaskPlanner,
    ):
        super().__init__(adb_client)
        self.loader = loader
        self._subtask: AutoAgencyIDSubtaskType | None = None
        self.planner = planner

    @property
    def task_type(self) -> TaskType:
        return TaskType.AGENCY_IDENTIFICATION

    async def meets_task_prerequisites(self) -> bool:
        """
        Modifies:
        - self._subtask
        """
        subtask_type: AutoAgencyIDSubtaskType | None = await self.planner.plan_next_subtask()
        if subtask_type is None:
            return False
        self._subtask = subtask_type
        return True


    async def load_subtask(
        self,
        subtask_type: AutoAgencyIDSubtaskType
    ) -> AgencyIDSubtaskOperatorBase:
        """Get subtask based on collector type."""
        return await self.loader.load_subtask(subtask_type)

    async def plan_next_subtask(self) -> AutoAgencyIDSubtaskType | None:
        return await self.planner.plan_next_subtask()

    @staticmethod
    async def run_subtask(
        subtask_operator: AgencyIDSubtaskOperatorBase,
    ) -> AgencyIDSubtaskRunInfo:
        return await subtask_operator.run()

    async def inner_task_logic(self) -> None:
        subtask_operator: AgencyIDSubtaskOperatorBase = await self.load_subtask(self._subtask)
        run_info: AgencyIDSubtaskRunInfo = await self.run_subtask(subtask_operator)
        if not run_info.is_success:
            raise SubtaskError(run_info.error)



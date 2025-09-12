from src.core.tasks.mixins.link_urls import LinkURLsMixin
from src.core.tasks.url.operators.agency_identification.exceptions import SubtaskError
from src.core.tasks.url.operators.agency_identification.subtasks.flags.core import SubtaskFlagger
from src.core.tasks.url.operators.agency_identification.subtasks.loader import AgencyIdentificationSubtaskLoader
from src.core.tasks.url.operators.agency_identification.subtasks.models.run_info import AgencyIDSubtaskRunInfo
from src.core.tasks.url.operators.agency_identification.subtasks.queries.survey.queries.core import \
    AgencyIDSubtaskSurveyQueryBuilder
from src.core.tasks.url.operators.agency_identification.subtasks.templates.subtask import AgencyIDSubtaskOperatorBase
from src.core.tasks.url.operators.base import URLTaskOperatorBase
from src.db.client.async_ import AsyncDatabaseClient
from src.db.enums import TaskType
from src.db.models.impl.url.suggestion.agency.subtask.enum import AutoAgencyIDSubtaskType


class AgencyIdentificationTaskOperator(
    URLTaskOperatorBase,
    LinkURLsMixin
):

    def __init__(
            self,
            adb_client: AsyncDatabaseClient,
            loader: AgencyIdentificationSubtaskLoader,
    ):
        super().__init__(adb_client)
        self.loader = loader
        self._subtask: AutoAgencyIDSubtaskType | None = None

    @property
    def task_type(self) -> TaskType:
        return TaskType.AGENCY_IDENTIFICATION

    async def meets_task_prerequisites(self) -> bool:
        """
        Modifies:
        - self._subtask
        """
        flagger = SubtaskFlagger()
        allowed_subtasks: list[AutoAgencyIDSubtaskType] = flagger.get_allowed_subtasks()

        next_subtask: AutoAgencyIDSubtaskType | None = \
            await self.adb_client.run_query_builder(
                AgencyIDSubtaskSurveyQueryBuilder(
                    allowed_subtasks=allowed_subtasks
                )
            )
        self._subtask = next_subtask
        if next_subtask is None:
            return False
        return True


    async def load_subtask(
        self,
        subtask_type: AutoAgencyIDSubtaskType
    ) -> AgencyIDSubtaskOperatorBase:
        """Get subtask based on collector type."""
        return await self.loader.load_subtask(subtask_type, task_id=self.task_id)

    @staticmethod
    async def run_subtask(
        subtask_operator: AgencyIDSubtaskOperatorBase,
    ) -> AgencyIDSubtaskRunInfo:
        return await subtask_operator.run()

    async def inner_task_logic(self) -> None:
        subtask_operator: AgencyIDSubtaskOperatorBase = await self.load_subtask(self._subtask)
        print(f"Running Subtask: {self._subtask.value}")
        run_info: AgencyIDSubtaskRunInfo = await self.run_subtask(subtask_operator)
        await self.link_urls_to_task(run_info.linked_url_ids)
        if not run_info.is_success:
            raise SubtaskError(run_info.error)



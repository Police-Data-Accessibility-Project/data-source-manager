from itertools import count

from src.core.tasks.mixins.prereq import HasPrerequisitesMixin
from src.core.tasks.scheduled.impl.huggingface.queries.prereq.core import CheckValidURLsUpdatedQueryBuilder
from src.core.tasks.scheduled.impl.huggingface.queries.get.core import GetForLoadingToHuggingFaceQueryBuilder
from src.core.tasks.scheduled.impl.huggingface.queries.get.model import GetForLoadingToHuggingFaceOutput
from src.core.tasks.scheduled.templates.operator import ScheduledTaskOperatorBase
from src.db.client.async_ import AsyncDatabaseClient
from src.db.enums import TaskType
from src.external.huggingface.hub.client import HuggingFaceHubClient


class PushToHuggingFaceTaskOperator(
    ScheduledTaskOperatorBase,
    HasPrerequisitesMixin
):

    @property
    def task_type(self) -> TaskType:
        return TaskType.PUSH_TO_HUGGINGFACE

    def __init__(
        self,
        adb_client: AsyncDatabaseClient,
        hf_client: HuggingFaceHubClient
    ):
        super().__init__(adb_client)
        self.hf_client = hf_client

    async def meets_task_prerequisites(self) -> bool:
        return await self.adb_client.run_query_builder(
            CheckValidURLsUpdatedQueryBuilder()
        )

    async def inner_task_logic(self):
        """Push raw data sources to huggingface."""
        run_dt = await self.adb_client.get_current_database_time()
        for idx in count(start=1):
            outputs: list[GetForLoadingToHuggingFaceOutput] = await self._get_data_sources_raw_for_huggingface(page=idx)
            if len(outputs) == 0:
                break
            self.hf_client.push_data_sources_raw_to_hub(outputs, idx=idx)

        await self.adb_client.set_hugging_face_upload_state(run_dt.replace(tzinfo=None))

    async def _get_data_sources_raw_for_huggingface(self, page: int) -> list[GetForLoadingToHuggingFaceOutput]:
        return await self.adb_client.run_query_builder(
            GetForLoadingToHuggingFaceQueryBuilder(page)
        )

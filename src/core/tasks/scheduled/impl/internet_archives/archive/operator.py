from src.core.tasks.mixins.link_urls import LinkURLsMixin
from src.core.tasks.mixins.prereq import HasPrerequisitesMixin
from src.core.tasks.scheduled.templates.operator import ScheduledTaskOperatorBase
from src.db.client.async_ import AsyncDatabaseClient
from src.db.enums import TaskType
from src.external.internet_archives.client import InternetArchivesClient


class InternetArchivesArchiveTaskOperator(
    ScheduledTaskOperatorBase,
    HasPrerequisitesMixin,
    LinkURLsMixin
):

    def __init__(
        self,
        adb_client: AsyncDatabaseClient,
        ia_client: InternetArchivesClient
    ):
        super().__init__(adb_client)
        self.ia_client = ia_client

    async def meets_task_prerequisites(self) -> bool:
        raise NotImplementedError

    @property
    def task_type(self) -> TaskType:
        return TaskType.IA_ARCHIVE

    async def inner_task_logic(self) -> None:
        raise NotImplementedError

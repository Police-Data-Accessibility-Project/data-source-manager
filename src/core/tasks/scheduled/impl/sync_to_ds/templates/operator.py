from abc import ABC

from src.core.tasks.base.operator import TaskOperatorBase
from src.core.tasks.mixins.prereq import HasPrerequisitesMixin
from src.core.tasks.url.enums import TaskOperatorOutcome
from src.db.client.async_ import AsyncDatabaseClient
from src.external.pdap.client import PDAPClient


class DSSyncTaskOperatorBase(
    TaskOperatorBase,
    HasPrerequisitesMixin,
    ABC
):

    def __init__(
        self,
        adb_client: AsyncDatabaseClient,
        pdap_client: PDAPClient
    ):
        super().__init__(adb_client)
        self.pdap_client = pdap_client

    async def conclude_task(self):
        return await self.run_info(
            outcome=TaskOperatorOutcome.SUCCESS,
            message="Task completed successfully"
        )

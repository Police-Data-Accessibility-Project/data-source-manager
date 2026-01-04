from abc import ABC

from src.core.tasks.mixins.prereq import HasPrerequisitesMixin
from src.core.tasks.scheduled.templates.operator import ScheduledTaskOperatorBase
from src.db.client.async_ import AsyncDatabaseClient
from src.external.pdap.client import PDAPClient


class DSSyncTaskOperatorBase(
    ScheduledTaskOperatorBase,
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

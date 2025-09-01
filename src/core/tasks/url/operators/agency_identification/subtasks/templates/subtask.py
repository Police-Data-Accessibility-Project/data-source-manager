import abc
from abc import ABC
from typing import Optional

from src.core.tasks.url.operators.agency_identification.dtos.suggestion import URLAgencySuggestionInfo
from src.core.tasks.url.operators.agency_identification.subtasks.models.run_info import AgencyIDSubtaskRunInfo
from src.db.client.async_ import AsyncDatabaseClient


class AgencyIdentificationSubtaskBase(ABC):

    def __init__(
        self,
        adb_client: AsyncDatabaseClient,
    ) -> None:
        self.adb_client = adb_client

    @abc.abstractmethod
    async def meets_prerequisites(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    async def run(self) -> AgencyIDSubtaskRunInfo:
        raise NotImplementedError

    @abc.abstractmethod
    async def blacklist(self) -> None:
        """Blacklist all invalid URLs
        so they will not be picked up by this job in the future."""

from abc import ABC, abstractmethod

from src.core.tasks.url.operators.agency_identification.subtasks.templates.output import AgencyIDSubtaskOutputBase
from src.db.client.async_ import AsyncDatabaseClient


class SubtaskPostprocessorBase(ABC):
    """
    An optional class which takes
    the output of the subtask along with the subtask id
    and adds additional information to the database.
    """

    def __init__(
        self,
        subtask_id: int,
        subtask_output: AgencyIDSubtaskOutputBase,
        adb_client: AsyncDatabaseClient
    ):
        self.subtask_id = subtask_id
        self.subtask_output = subtask_output
        self.adb_client = adb_client

    @abstractmethod
    async def run(self) -> None:
        raise NotImplementedError
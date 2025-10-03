import traceback
from abc import ABC, abstractmethod

from src.core.enums import BatchStatus
from src.core.tasks.base.run_info import TaskOperatorRunInfo
from src.core.tasks.url.enums import TaskOperatorOutcome
from src.db.client.async_ import AsyncDatabaseClient
from src.db.enums import TaskType
from src.db.models.impl.task.enums import TaskStatus


class TaskOperatorBase(ABC):
    def __init__(self, adb_client: AsyncDatabaseClient):
        self._adb_client = adb_client
        self._task_id: int | None = None

    @property
    def task_id(self) -> int:
        if self._task_id is None:
            raise AttributeError("Task id is not set. Call initiate_task_in_db() first.")
        return self._task_id

    @property
    def adb_client(self) -> AsyncDatabaseClient:
        return self._adb_client

    @property
    @abstractmethod
    def task_type(self) -> TaskType:
        raise NotImplementedError

    async def initiate_task_in_db(self) -> int:
        task_id = await self.adb_client.initiate_task(
            task_type=self.task_type
        )
        return task_id

    @abstractmethod
    async def conclude_task(self):
        raise NotImplementedError

    async def run_task(self) -> TaskOperatorRunInfo:
        self._task_id = await self.initiate_task_in_db()
        try:
            await self.inner_task_logic()
            return await self.conclude_task()
        except Exception as e:
            stack_trace = traceback.format_exc()
            return await self.run_info(
                outcome=TaskOperatorOutcome.ERROR,
                message=str(e) + "\n" + stack_trace
            )

    @abstractmethod
    async def run_info(self, outcome: TaskOperatorOutcome, message: str) -> TaskOperatorRunInfo:
        raise NotImplementedError


    @abstractmethod
    async def inner_task_logic(self) -> None:
        raise NotImplementedError

    async def handle_task_error(self, e):
        await self.adb_client.update_task_status(task_id=self.task_id, status=TaskStatus.ERROR)
        await self.adb_client.add_task_error(
            task_id=self.task_id,
            error=str(e)
        )

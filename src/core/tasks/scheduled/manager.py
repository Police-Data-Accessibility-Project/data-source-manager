from datetime import datetime

from src.core.tasks.base.run_info import TaskOperatorRunInfo
from src.core.tasks.handler import TaskHandler
from src.core.tasks.mixins.link_urls import LinkURLsMixin
from src.core.tasks.mixins.prereq import HasPrerequisitesMixin
from src.core.tasks.scheduled.loader import ScheduledTaskOperatorLoader
from src.core.tasks.scheduled.models.entry import ScheduledTaskEntry
from src.core.tasks.scheduled.registry.core import ScheduledJobRegistry
from src.core.tasks.scheduled.registry.format import format_job_datetime
from src.core.tasks.scheduled.templates.operator import ScheduledTaskOperatorBase


class AsyncScheduledTaskManager:

    def __init__(
        self,
        handler: TaskHandler,
        loader: ScheduledTaskOperatorLoader,
        registry: ScheduledJobRegistry
    ):

        # Dependencies
        self._handler = handler
        self._loader = loader
        self._registry = registry


    async def setup(self):
        self._registry.start_scheduler()
        await self.add_scheduled_tasks()
        await self._registry.report_next_scheduled_task()



    async def add_scheduled_tasks(self):
        """
        Modifies:
            self._registry
        """
        entries: list[ScheduledTaskEntry] = await self._loader.load_entries()
        enabled_entries: list[ScheduledTaskEntry] = []
        for entry in entries:
            if not entry.enabled:
                print(f"{entry.operator.task_type.value} is disabled. Skipping add to scheduler.")
                continue
            enabled_entries.append(entry)

        initial_lag: int = 1

        print("Adding the following scheduled tasks:")
        print(f"TASK_NAME                | TASK_INTERVAL")
        for idx, entry in enumerate(enabled_entries):
            next_run_time: datetime = await self._registry.add_job(
                func=self.run_task,
                entry=entry,
                minute_lag=idx + initial_lag
            )
            run_time_str: str = format_job_datetime(next_run_time)
            print(f"{entry.operator.task_type.value:<25}| {run_time_str}")

    def shutdown(self):
        self._registry.shutdown_scheduler()

    async def run_task(self, operator: ScheduledTaskOperatorBase):
        print(f"Running {operator.task_type.value} Task")
        if issubclass(operator.__class__, HasPrerequisitesMixin):
            operator: HasPrerequisitesMixin
            if not await operator.meets_task_prerequisites():
                operator: ScheduledTaskOperatorBase
                print(f"Prerequisites not met for {operator.task_type.value} Task. Skipping.")
                return
        run_info: TaskOperatorRunInfo = await operator.run_task()
        if issubclass(operator.__class__, LinkURLsMixin):
            operator: LinkURLsMixin
            if not operator.urls_linked:
                operator: ScheduledTaskOperatorBase
                raise Exception(f"Task {operator.task_type.value} has not been linked to any URLs but is designated as a link task")
        await self._handler.handle_outcome(run_info)
        await self._registry.report_next_scheduled_task()

from datetime import datetime, timedelta
from typing import Callable

from apscheduler.job import Job
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from src.core.tasks.scheduled.models.entry import ScheduledTaskEntry
from src.core.tasks.scheduled.registry.format import format_job_datetime
from src.db.enums import TaskType


class ScheduledJobRegistry:


    def __init__(self):
        # Main objects
        self.scheduler = AsyncIOScheduler()

        # Jobs
        self._jobs: dict[TaskType, Job] = {}

    async def add_job(
        self,
        func: Callable,
        entry: ScheduledTaskEntry,
        minute_lag: int
    ) -> None:
        """
        Modifies:
            self._jobs
        """
        job: Job = self.scheduler.add_job(
            id=entry.operator.task_type.value,
            func=func,
            trigger=IntervalTrigger(
                minutes=entry.interval_minutes,
                start_date=datetime.now() + timedelta(minutes=minute_lag)
            ),
            misfire_grace_time=60,
            kwargs={"operator": entry.operator}
        )
        run_time_str: str = format_job_datetime(job.next_run_time)
        print(f"Adding {job.id} task to scheduler. " +
              f"First run at {run_time_str}")
        self._jobs[entry.operator.task_type] = job

    def start_scheduler(self) -> None:
        """
        Modifies:
            self.scheduler
        """
        self.scheduler.start()

    def shutdown_scheduler(self) -> None:
        if self.scheduler.running:
            self.scheduler.shutdown()

    async def report_next_scheduled_task(self):
        jobs: list[Job] = self.scheduler.get_jobs()
        if len(jobs) == 0:
            print("No scheduled tasks found.")
            return

        jobs_sorted: list[Job] = sorted(jobs, key=lambda job: job.next_run_time)
        next_job: Job = jobs_sorted[0]

        run_time_str: str = format_job_datetime(next_job.next_run_time)
        print(f"Next scheduled task: {run_time_str} ({next_job.id})")
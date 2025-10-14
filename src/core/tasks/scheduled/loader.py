from environs import Env

from src.core.core import AsyncCore
from src.core.tasks.scheduled.enums import IntervalEnum
from src.core.tasks.scheduled.impl.backlog.operator import PopulateBacklogSnapshotTaskOperator
from src.core.tasks.scheduled.impl.delete_logs.operator import DeleteOldLogsTaskOperator
from src.core.tasks.scheduled.impl.delete_stale_screenshots.operator import DeleteStaleScreenshotsTaskOperator
from src.core.tasks.scheduled.impl.huggingface.operator import PushToHuggingFaceTaskOperator
from src.core.tasks.scheduled.impl.internet_archives.probe.operator import InternetArchivesProbeTaskOperator
from src.core.tasks.scheduled.impl.internet_archives.save.operator import InternetArchivesSaveTaskOperator
from src.core.tasks.scheduled.impl.mark_never_completed.operator import MarkTaskNeverCompletedOperator
from src.core.tasks.scheduled.impl.mark_never_completed.query import MarkTaskNeverCompletedQueryBuilder
from src.core.tasks.scheduled.impl.refresh_materialized_views.operator import RefreshMaterializedViewsOperator
from src.core.tasks.scheduled.impl.run_url_tasks.operator import RunURLTasksTaskOperator
from src.core.tasks.scheduled.impl.task_cleanup.operator import TaskCleanupOperator
from src.core.tasks.scheduled.models.entry import ScheduledTaskEntry
from src.db.client.async_ import AsyncDatabaseClient
from src.external.huggingface.hub.client import HuggingFaceHubClient
from src.external.internet_archives.client import InternetArchivesClient
from src.external.pdap.client import PDAPClient


class ScheduledTaskOperatorLoader:

    def __init__(
            self,
            async_core: AsyncCore,
            adb_client: AsyncDatabaseClient,
            pdap_client: PDAPClient,
            hf_client: HuggingFaceHubClient,
            ia_client: InternetArchivesClient
    ):
        # Dependencies
        self.async_core = async_core
        self.adb_client = adb_client
        self.pdap_client = pdap_client

        # External Interfaces
        self.hf_client = hf_client
        self.ia_client = ia_client

        self.env = Env()
        self.env.read_env()

    def setup_flag(self, name: str) -> bool:
        return self.env.bool(name, default=True)


    async def load_entries(self) -> list[ScheduledTaskEntry]:
        scheduled_task_flag = self.env.bool("SCHEDULED_TASKS_FLAG", default=True)
        if not scheduled_task_flag:
            print("Scheduled tasks are disabled.")
            return []


        return [
            ScheduledTaskEntry(
                operator=InternetArchivesProbeTaskOperator(
                    adb_client=self.adb_client,
                    ia_client=self.ia_client
                ),
                interval_minutes=IntervalEnum.TEN_MINUTES.value,
                enabled=self.setup_flag("IA_PROBE_TASK_FLAG"),
            ),
            ScheduledTaskEntry(
                operator=InternetArchivesSaveTaskOperator(
                    adb_client=self.adb_client,
                    ia_client=self.ia_client
                ),
                interval_minutes=IntervalEnum.TEN_MINUTES.value,
                enabled=self.setup_flag("IA_SAVE_TASK_FLAG"),
            ),
            ScheduledTaskEntry(
                operator=DeleteOldLogsTaskOperator(adb_client=self.adb_client),
                interval_minutes=IntervalEnum.DAILY.value,
                enabled=self.setup_flag("DELETE_OLD_LOGS_TASK_FLAG")
            ),
            ScheduledTaskEntry(
                operator=RunURLTasksTaskOperator(async_core=self.async_core),
                interval_minutes=self.env.int(
                    "URL_TASKS_FREQUENCY_MINUTES",
                    default=IntervalEnum.HOURLY.value
                ),
                enabled=self.setup_flag("RUN_URL_TASKS_TASK_FLAG")
            ),
            ScheduledTaskEntry(
                operator=PopulateBacklogSnapshotTaskOperator(adb_client=self.async_core.adb_client),
                interval_minutes=IntervalEnum.DAILY.value,
                enabled=self.setup_flag("POPULATE_BACKLOG_SNAPSHOT_TASK_FLAG")
            ),
            ScheduledTaskEntry(
                operator=PushToHuggingFaceTaskOperator(
                    adb_client=self.async_core.adb_client,
                    hf_client=self.hf_client
                ),
                interval_minutes=IntervalEnum.DAILY.value,
                enabled=self.setup_flag("PUSH_TO_HUGGING_FACE_TASK_FLAG")
            ),
            ScheduledTaskEntry(
                operator=MarkTaskNeverCompletedOperator(adb_client=self.adb_client),
                interval_minutes=IntervalEnum.DAILY.value,
                enabled=self.setup_flag("MARK_TASK_NEVER_COMPLETED_TASK_FLAG")
            ),
            ScheduledTaskEntry(
                operator=DeleteStaleScreenshotsTaskOperator(adb_client=self.adb_client),
                interval_minutes=IntervalEnum.DAILY.value,
                enabled=self.setup_flag("DELETE_STALE_SCREENSHOTS_TASK_FLAG")
            ),
            ScheduledTaskEntry(
                operator=TaskCleanupOperator(adb_client=self.adb_client),
                interval_minutes=IntervalEnum.DAILY.value,
                enabled=self.setup_flag("TASK_CLEANUP_TASK_FLAG")
            ),
            ScheduledTaskEntry(
                operator=RefreshMaterializedViewsOperator(adb_client=self.adb_client),
                interval_minutes=IntervalEnum.DAILY.value,
                enabled=self.setup_flag("REFRESH_MATERIALIZED_VIEWS_TASK_FLAG")
            )
        ]

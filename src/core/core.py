from http import HTTPStatus

from fastapi import HTTPException
from pydantic import BaseModel

from src.api.endpoints.batch.dtos.get.logs import GetBatchLogsResponse
from src.api.endpoints.batch.dtos.get.summaries.response import GetBatchSummariesResponse
from src.api.endpoints.batch.dtos.get.summaries.summary import BatchSummary
from src.api.shared.models.message_response import MessageResponse
from src.api.endpoints.batch.duplicates.dto import GetDuplicatesByBatchResponse
from src.api.endpoints.batch.urls.dto import GetURLsByBatchResponse
from src.api.endpoints.collector.dtos.collector_start import CollectorStartInfo
from src.api.endpoints.collector.dtos.manual_batch.post import ManualBatchInputDTO
from src.api.endpoints.collector.dtos.manual_batch.response import ManualBatchResponseDTO
from src.api.endpoints.metrics.batches.aggregated.dto import GetMetricsBatchesAggregatedResponseDTO
from src.api.endpoints.metrics.batches.breakdown.dto import GetMetricsBatchesBreakdownResponseDTO
from src.api.endpoints.metrics.dtos.get.backlog import GetMetricsBacklogResponseDTO
from src.api.endpoints.metrics.dtos.get.urls.aggregated.core import GetMetricsURLsAggregatedResponseDTO
from src.api.endpoints.metrics.dtos.get.urls.aggregated.pending import GetMetricsURLsAggregatedPendingResponseDTO
from src.api.endpoints.metrics.dtos.get.urls.breakdown.pending import GetMetricsURLsBreakdownPendingResponseDTO
from src.api.endpoints.metrics.dtos.get.urls.breakdown.submitted import GetMetricsURLsBreakdownSubmittedResponseDTO
from src.api.endpoints.search.dtos.response import SearchURLResponse
from src.api.endpoints.task.by_id.dto import TaskInfo
from src.api.endpoints.task.dtos.get.task_status import GetTaskStatusResponseInfo
from src.api.endpoints.task.dtos.get.tasks import GetTasksResponse
from src.api.endpoints.url.get.dto import GetURLsResponseInfo
from src.collectors.enums import CollectorType
from src.collectors.manager import AsyncCollectorManager
from src.core.enums import BatchStatus
from src.core.tasks.url.manager import TaskManager
from src.db.client.async_ import AsyncDatabaseClient
from src.db.enums import TaskType
from src.db.models.impl.batch.pydantic.info import BatchInfo
from src.db.models.materialized_views.batch_url_status.enums import BatchURLStatusViewEnum


class AsyncCore:
    task_manager: TaskManager | None = None
    adb_client: AsyncDatabaseClient | None = None
    collector_manager: AsyncCollectorManager | None = None

    def __init__(
            self,
            adb_client: AsyncDatabaseClient,
            collector_manager: AsyncCollectorManager,
            task_manager: TaskManager
    ):
        self.task_manager = task_manager
        self.adb_client = adb_client
        self.collector_manager = collector_manager


    async def get_urls(self, page: int, errors: bool) -> GetURLsResponseInfo:
        return await self.adb_client.get_urls(page=page, errors=errors)

    async def shutdown(self):
        await self.collector_manager.shutdown_all_collectors()

    #region Batch
    async def get_batch_info(self, batch_id: int) -> BatchSummary:
        result = await self.adb_client.get_batch_by_id(batch_id)
        if result is None:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=f"Batch {batch_id} does not exist"
            )
        return result

    async def get_urls_by_batch(self, batch_id: int, page: int = 1) -> GetURLsByBatchResponse:
        url_infos = await self.adb_client.get_urls_by_batch(batch_id, page)
        return GetURLsByBatchResponse(urls=url_infos)

    async def abort_batch(self, batch_id: int) -> MessageResponse:
        await self.collector_manager.abort_collector_async(cid=batch_id)
        return MessageResponse(message=f"Batch aborted.")

    async def get_duplicate_urls_by_batch(self, batch_id: int, page: int = 1) -> GetDuplicatesByBatchResponse:
        dup_infos = await self.adb_client.get_duplicates_by_batch_id(batch_id, page=page)
        return GetDuplicatesByBatchResponse(duplicates=dup_infos)

    async def get_batch_statuses(
            self,
            collector_type: CollectorType | None,
            status: BatchURLStatusViewEnum | None,
            page: int
    ) -> GetBatchSummariesResponse:
        results = await self.adb_client.get_batch_summaries(
            collector_type=collector_type,
            status=status,
            page=page,
        )
        return results

    async def get_batch_logs(self, batch_id: int) -> GetBatchLogsResponse:
        logs = await self.adb_client.get_logs_by_batch_id(batch_id)
        return GetBatchLogsResponse(logs=logs)

    #endregion

    # region Collector
    async def initiate_collector(
        self,
        collector_type: CollectorType,
        user_id: int,
        dto: BaseModel | None = None,
    ) -> CollectorStartInfo:
        """
        Reserves a batch ID from the database
        and starts the requisite collector
        """

        batch_info = BatchInfo(
            strategy=collector_type.value,
            status=BatchStatus.IN_PROCESS,
            parameters=dto.model_dump(),
            user_id=user_id
        )

        batch_id = await self.adb_client.insert_batch(batch_info)
        await self.collector_manager.start_async_collector(
            collector_type=collector_type,
            batch_id=batch_id,
            dto=dto
        )
        return CollectorStartInfo(
            batch_id=batch_id,
            message=f"Started {collector_type.value} collector."
        )

    # endregion
    async def get_current_task_status(self) -> GetTaskStatusResponseInfo:
        return GetTaskStatusResponseInfo(status=self.task_manager.manager_status)

    async def run_tasks(self):
        await self.task_manager.trigger_task_run()

    async def get_tasks(
            self,
            page: int,
            task_type: TaskType,
            task_status: BatchStatus
    ) -> GetTasksResponse:
        return await self.adb_client.get_tasks(
            page=page,
            task_type=task_type,
            task_status=task_status
        )

    async def get_task_info(self, task_id: int) -> TaskInfo:
        return await self.adb_client.get_task_info(task_id=task_id)

    async def upload_manual_batch(
            self,
            dto: ManualBatchInputDTO,
            user_id: int
    ) -> ManualBatchResponseDTO:
        return await self.adb_client.upload_manual_batch(
            user_id=user_id,
            dto=dto
        )

    async def search_for_url(self, url: str) -> SearchURLResponse:
        return await self.adb_client.search_for_url(url)

    async def get_batches_aggregated_metrics(self) -> GetMetricsBatchesAggregatedResponseDTO:
        return await self.adb_client.get_batches_aggregated_metrics()

    async def get_batches_breakdown_metrics(self, page: int) -> GetMetricsBatchesBreakdownResponseDTO:
        return await self.adb_client.get_batches_breakdown_metrics(page=page)

    async def get_urls_breakdown_submitted_metrics(self) -> GetMetricsURLsBreakdownSubmittedResponseDTO:
        return await self.adb_client.get_urls_breakdown_submitted_metrics()

    async def get_urls_aggregated_metrics(self) -> GetMetricsURLsAggregatedResponseDTO:
        return await self.adb_client.get_urls_aggregated_metrics()

    async def get_urls_breakdown_pending_metrics(self) -> GetMetricsURLsBreakdownPendingResponseDTO:
        return await self.adb_client.get_urls_breakdown_pending_metrics()

    async def get_backlog_metrics(self) -> GetMetricsBacklogResponseDTO:
        return await self.adb_client.get_backlog_metrics()

    async def get_urls_aggregated_pending_metrics(self) -> GetMetricsURLsAggregatedPendingResponseDTO:
        return await self.adb_client.get_urls_aggregated_pending_metrics()
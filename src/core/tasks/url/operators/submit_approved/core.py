from src.core.tasks.url.operators.base import URLTaskOperatorBase
from src.core.tasks.url.operators.submit_approved.tdo import SubmitApprovedURLTDO, SubmittedURLInfo
from src.db.client.async_ import AsyncDatabaseClient
from src.db.enums import TaskType
from src.db.models.impl.url.task_error.pydantic_.small import URLTaskErrorSmall
from src.external.pdap.client import PDAPClient


class SubmitApprovedURLTaskOperator(URLTaskOperatorBase):

    def __init__(
            self,
            adb_client: AsyncDatabaseClient,
            pdap_client: PDAPClient
    ):
        super().__init__(adb_client)
        self.pdap_client = pdap_client

    @property
    def task_type(self):
        return TaskType.SUBMIT_APPROVED

    async def meets_task_prerequisites(self):
        return await self.adb_client.has_validated_urls()

    async def inner_task_logic(self):
        # Retrieve all URLs that are validated and not submitted
        tdos: list[SubmitApprovedURLTDO] = await self.adb_client.get_validated_urls()

        # Link URLs to this task
        await self.link_urls_to_task(url_ids=[tdo.url_id for tdo in tdos])

        # Submit each URL, recording errors if they exist
        submitted_url_infos: list[SubmittedURLInfo] = await self.pdap_client.submit_data_source_urls(tdos)

        task_errors: list[URLTaskErrorSmall] = await self.get_error_infos(submitted_url_infos)
        success_infos = await self.get_success_infos(submitted_url_infos)

        # Update the database for successful submissions
        await self.adb_client.mark_urls_as_submitted(infos=success_infos)

        # Update the database for failed submissions
        await self.add_task_errors(task_errors)

    async def get_success_infos(self, submitted_url_infos):
        success_infos = [
            response_object for response_object in submitted_url_infos
            if response_object.data_source_id is not None
        ]
        return success_infos

    async def get_error_infos(
        self,
        submitted_url_infos: list[SubmittedURLInfo]
    ) -> list[URLTaskErrorSmall]:
        task_errors: list[URLTaskErrorSmall] = []
        error_response_objects = [
            response_object for response_object in submitted_url_infos
            if response_object.request_error is not None
        ]
        for error_response_object in error_response_objects:
            error_info = URLTaskErrorSmall(
                url_id=error_response_object.url_id,
                error=error_response_object.request_error,
            )
            task_errors.append(error_info)
        return task_errors

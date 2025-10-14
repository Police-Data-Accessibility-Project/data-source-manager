from src.core.tasks.url.operators.base import URLTaskOperatorBase
from src.core.tasks.url.operators.screenshot.convert import convert_to_url_screenshot_pydantic, \
    convert_to_task_error
from src.core.tasks.url.operators.screenshot.filter import filter_success_outcomes
from src.core.tasks.url.operators.screenshot.get import get_url_screenshots
from src.core.tasks.url.operators.screenshot.models.outcome import URLScreenshotOutcome
from src.core.tasks.url.operators.screenshot.models.subsets import URLScreenshotOutcomeSubsets
from src.core.tasks.url.operators.screenshot.queries.get import GetURLsForScreenshotTaskQueryBuilder
from src.core.tasks.url.operators.screenshot.queries.prereq import URLsForScreenshotTaskPrerequisitesQueryBuilder
from src.db.client.async_ import AsyncDatabaseClient
from src.db.dtos.url.mapping import URLMapping
from src.db.enums import TaskType
from src.db.models.impl.url.screenshot.pydantic import URLScreenshotPydantic
from src.db.models.impl.url.task_error.pydantic_.small import URLTaskErrorSmall


class URLScreenshotTaskOperator(URLTaskOperatorBase):

    def __init__(
        self,
        adb_client: AsyncDatabaseClient,
    ):
        super().__init__(adb_client)

    @property
    def task_type(self) -> TaskType:
        return TaskType.SCREENSHOT

    async def meets_task_prerequisites(self) -> bool:
        return await self.adb_client.run_query_builder(
            URLsForScreenshotTaskPrerequisitesQueryBuilder()
        )

    async def get_urls_without_screenshot(self) -> list[URLMapping]:
        return await self.adb_client.run_query_builder(
            GetURLsForScreenshotTaskQueryBuilder()
        )

    async def upload_screenshots(self, outcomes: list[URLScreenshotOutcome]) -> None:
        insert_models: list[URLScreenshotPydantic] = convert_to_url_screenshot_pydantic(outcomes)
        await self.adb_client.bulk_insert(insert_models)

    async def upload_errors(self, outcomes: list[URLScreenshotOutcome]) -> None:
        insert_models: list[URLTaskErrorSmall] = convert_to_task_error(
            outcomes=outcomes,
        )
        await self.add_task_errors(insert_models)

    async def inner_task_logic(self) -> None:
        url_mappings: list[URLMapping] = await self.get_urls_without_screenshot()
        await self.link_urls_to_task(
            url_ids=[url_mapping.url_id for url_mapping in url_mappings]
        )

        outcomes: list[URLScreenshotOutcome] = await get_url_screenshots(
            mappings=url_mappings
        )

        subsets: URLScreenshotOutcomeSubsets = filter_success_outcomes(outcomes)
        await self.upload_screenshots(subsets.success)
        await self.upload_errors(subsets.failed)


from src.core.tasks.url.operators.base import URLTaskOperatorBase
from src.core.tasks.url.operators.screenshot.convert import convert_to_url_screenshot_pydantic, \
    convert_to_url_error_info
from src.core.tasks.url.operators.screenshot.filter import filter_success_outcomes
from src.core.tasks.url.operators.screenshot.models.outcome import URLScreenshotOutcome
from src.core.tasks.url.operators.screenshot.models.subsets import URLScreenshotOutcomeSubsets
from src.db.client.async_ import AsyncDatabaseClient
from src.db.dtos.url.mapping import URLMapping
from src.db.models.impl.url.error_info.pydantic import URLErrorInfoPydantic
from src.db.models.impl.url.screenshot.pydantic import URLScreenshotPydantic
from src.external.url_request.core import URLRequestInterface


class URLScreenshotTaskOperator(URLTaskOperatorBase):

    def __init__(
        self,
        adb_client: AsyncDatabaseClient,
        url_request_interface: URLRequestInterface
    ):
        super().__init__(adb_client)
        self.url_request_interface = url_request_interface


    async def meets_task_prerequisites(self) -> bool:
        raise NotImplementedError

    async def get_urls_without_screenshot(self) -> list[URLMapping]:
        raise NotImplementedError

    async def get_url_screenshots(self, urls: list[URLMapping]) -> list[URLScreenshotOutcome]:
        raise NotImplementedError

    async def upload_screenshots(self, outcomes: list[URLScreenshotOutcome]) -> None:
        insert_models: list[URLScreenshotPydantic] = convert_to_url_screenshot_pydantic(outcomes)
        await self.adb_client.bulk_insert(insert_models)

    async def upload_errors(self, outcomes: list[URLScreenshotOutcome]) -> None:
        insert_models: list[URLErrorInfoPydantic] = convert_to_url_error_info(outcomes)
        await self.adb_client.bulk_insert(insert_models)

    async def inner_task_logic(self) -> None:
        url_mappings: list[URLMapping] = await self.get_urls_without_screenshot()

        outcomes: list[URLScreenshotOutcome] = await self.get_url_screenshots(
            urls=url_mappings
        )

        subsets: URLScreenshotOutcomeSubsets = filter_success_outcomes(outcomes)
        await self.upload_screenshots(subsets.success)
        await self.upload_errors(subsets.failed)


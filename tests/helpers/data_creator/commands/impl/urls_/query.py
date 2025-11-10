from datetime import datetime

from tests.helpers.data_creator.commands.impl.urls_.tdo import SubmittedURLInfo
from src.db.dtos.url.insert import InsertURLsInfo
from src.db.models.impl.url.core.enums import URLSource
from src.db.models.impl.url.core.pydantic.info import URLInfo
from tests.helpers.batch_creation_parameters.enums import URLCreationEnum
from tests.helpers.data_creator.commands.base import DBDataCreatorCommandBase
from tests.helpers.data_creator.commands.impl.urls_.convert import convert_url_creation_enum_to_url_status
from tests.helpers.simple_test_data_functions import generate_test_urls


class URLsDBDataCreatorCommand(DBDataCreatorCommandBase):

    def __init__(
        self,
        batch_id: int | None,
        url_count: int,
        collector_metadata: dict | None = None,
        status: URLCreationEnum = URLCreationEnum.OK,
        created_at: datetime | None = None
    ):
        super().__init__()
        self.batch_id = batch_id
        self.url_count = url_count
        self.collector_metadata = collector_metadata
        self.status = status
        self.created_at = created_at

    async def run(self) -> InsertURLsInfo:
        raise NotImplementedError

    def run_sync(self) -> InsertURLsInfo:
        raw_urls = generate_test_urls(self.url_count)
        url_infos: list[URLInfo] = []
        for url in raw_urls:
            url_infos.append(
                URLInfo(
                    url=url,
                    status=convert_url_creation_enum_to_url_status(self.status),
                    name="Test Name" if self.status in (
                        URLCreationEnum.VALIDATED,
                        URLCreationEnum.SUBMITTED,
                    ) else None,
                    collector_metadata=self.collector_metadata,
                    created_at=self.created_at,
                    source=URLSource.COLLECTOR
                )
            )

        url_insert_info = self.db_client.insert_urls(
            url_infos=url_infos,
            batch_id=self.batch_id,
        )

        # If outcome is submitted, also add entry to DataSourceURL
        if self.status == URLCreationEnum.SUBMITTED:
            submitted_url_infos = []
            for url_id in url_insert_info.url_ids:
                submitted_url_info = SubmittedURLInfo(
                    url_id=url_id,
                    data_source_id=url_id, # Use same ID for convenience,
                    request_error=None,
                    submitted_at=self.created_at
                )
                submitted_url_infos.append(submitted_url_info)
            self.db_client.mark_urls_as_submitted(submitted_url_infos)


        return url_insert_info
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.enums import RecordType
from src.db.models.impl.flag.url_validated.enums import URLValidatedType
from src.db.queries.base.builder import QueryBuilderBase
from tests.automated.integration.tasks.scheduled.impl.sync.data_sources.setup.queries.url_.requester import \
    TestDataSourcesSyncURLSetupQueryRequester


class TestDataSourcesSyncURLSetupQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        record_type: RecordType,
        validated_type: URLValidatedType | None = None,
        previously_synced: bool = False,
    ):
        super().__init__()
        self.record_type = record_type
        self.validated_type = validated_type
        self.previously_synced = previously_synced

    async def run(self, session: AsyncSession) -> list[int]:
        requester = TestDataSourcesSyncURLSetupQueryRequester(session=session)

        url_ids: list[int] = await requester.insert_urls(record_type=self.record_type)

        if self.validated_type is not None:
            await requester.insert_validated_flags(url_ids=url_ids, validated_type=self.validated_type)

        if self.previously_synced:
            await requester.insert_data_source_entry(url_ids=url_ids)

        return url_ids


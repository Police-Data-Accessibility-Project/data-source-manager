from sqlalchemy.ext.asyncio import AsyncSession

from src.core.enums import RecordType
from src.db.models.impl.flag.url_validated.enums import URLType
from src.db.models.impl.flag.url_validated.pydantic import FlagURLValidatedPydantic
from src.db.models.impl.url.core.enums import URLSource
from src.db.models.impl.url.core.pydantic.insert import URLInsertModel
from src.db.models.impl.url.data_source.pydantic import URLDataSourcePydantic
from src.db.templates.requester import RequesterBase
from tests.helpers.simple_test_data_functions import generate_test_name, generate_test_url


class TestDataSourcesSyncURLSetupQueryRequester(RequesterBase):

    async def insert_urls(
        self,
        record_type: RecordType,
    ) -> list[int]:

        insert_models: list[URLInsertModel] = []
        for i in range(2):
            url = URLInsertModel(
                url=generate_test_url(i),
                name=generate_test_name(i),
                record_type=record_type,
                source=URLSource.COLLECTOR,
            )
            insert_models.append(url)

        return await self.session_helper.bulk_insert(self.session, models=insert_models, return_ids=True)

    async def insert_validated_flags(
        self,
        url_ids: list[int],
        validated_type: URLType
    ) -> None:
        to_insert: list[FlagURLValidatedPydantic] = []
        for url_id in url_ids:
            flag = FlagURLValidatedPydantic(
                url_id=url_id,
                type=validated_type,
            )
            to_insert.append(flag)

        await self.session_helper.bulk_insert(self.session, models=to_insert)

    async def insert_data_source_entry(
        self,
        url_ids: list[int],
    ):
        to_insert: list[URLDataSourcePydantic] = [
            URLDataSourcePydantic(
                url_id=url_id,
                data_source_id=url_id,
            )
            for url_id in url_ids
        ]

        await self.session_helper.bulk_insert(self.session, models=to_insert)
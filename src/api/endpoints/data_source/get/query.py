from datetime import date
from typing import Any, Sequence

from sqlalchemy import select, RowMapping, and_, Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.api.endpoints.data_source._shared.build import build_data_source_get_query
from src.api.endpoints.data_source._shared.process import process_data_source_get_mapping
from src.api.endpoints.data_source.get.response import DataSourceGetOuterResponse, DataSourceGetResponse
from src.core.enums import RecordType
from src.db.models.impl.flag.url_validated.enums import URLType
from src.db.models.impl.flag.url_validated.sqlalchemy import FlagURLValidated
from src.db.models.impl.link.batch_url.sqlalchemy import LinkBatchURL
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.optional_ds_metadata.enums import AgencyAggregationEnum, UpdateMethodEnum, \
    RetentionScheduleEnum, AccessTypeEnum
from src.db.models.impl.url.optional_ds_metadata.sqlalchemy import URLOptionalDataSourceMetadata
from src.db.models.impl.url.record_type.sqlalchemy import URLRecordType
from src.db.queries.base.builder import QueryBuilderBase


class GetDataSourcesQueryBuilder(QueryBuilderBase):

    def __init__(
            self,
            page: int,
    ):
        super().__init__()
        self.page = page

    async def run(self, session: AsyncSession) -> DataSourceGetOuterResponse:
        query: Select = build_data_source_get_query()
        query = (
            query
            .limit(100)
            .offset((self.page - 1) * 100)
        )

        mappings: Sequence[RowMapping] = await self.sh.mappings(session, query=query)
        responses: list[DataSourceGetResponse] = []

        for mapping in mappings:
            response: DataSourceGetResponse = process_data_source_get_mapping(mapping)
            responses.append(response)

        return DataSourceGetOuterResponse(
            results=responses,
        )


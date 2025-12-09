from sqlalchemy import Select, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.endpoints.data_source._shared.build import build_data_source_get_query
from src.api.endpoints.data_source._shared.process import process_data_source_get_mapping
from src.api.endpoints.data_source.get.response import DataSourceGetResponse
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.queries.base.builder import QueryBuilderBase


class GetDataSourceByIDQueryBuilder(QueryBuilderBase):
    def __init__(
            self,
            url_id: int,
    ):
        super().__init__()
        self.url_id = url_id

    async def run(self, session: AsyncSession) -> DataSourceGetResponse:
        query: Select = build_data_source_get_query()
        query = query.where(URL.id == self.url_id)

        mapping: RowMapping = await self.sh.mapping(session, query=query)
        return process_data_source_get_mapping(mapping=mapping)
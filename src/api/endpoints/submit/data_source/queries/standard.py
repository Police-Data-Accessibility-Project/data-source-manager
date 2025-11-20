from typing import Any

from sqlalchemy import select, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.endpoints.submit.data_source.models.response.standard import SubmitDataSourceURLProposalResponse
from src.api.endpoints.submit.data_source.request import DataSourceSubmissionRequest
from src.db.models.impl.flag.url_validated.sqlalchemy import FlagURLValidated
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.queries.base.builder import QueryBuilderBase


class SubmitDataSourceURLProposalStandardQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        url_id: int,
        request: DataSourceSubmissionRequest
    ):
        super().__init__()
        self.url_id = url_id
        self.request = request

    async def run(self, session: AsyncSession) -> SubmitDataSourceURLProposalResponse:

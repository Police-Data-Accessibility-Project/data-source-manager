from typing import Sequence

from sqlalchemy import select, and_, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.api.endpoints.meta_url.get.response import MetaURLGetOuterResponse, MetaURLGetResponse
from src.db.models.impl.flag.url_validated.enums import URLType
from src.db.models.impl.flag.url_validated.sqlalchemy import FlagURLValidated
from src.db.models.impl.link.batch_url.sqlalchemy import LinkBatchURL
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.queries.base.builder import QueryBuilderBase


class GetMetaURLQueryBuilder(QueryBuilderBase):

    def __init__(
            self,
            page: int,
    ):
        super().__init__()
        self.page = page

    async def run(self, session: AsyncSession) -> MetaURLGetOuterResponse:
        query = (
            select(
                URL,
                URL.id,
                URL.url,

                # Required Attributes
                URL.name,
                URL.confirmed_agencies,

                # Optional Attributes
                URL.description,
                LinkBatchURL.batch_id,
            )
            .join(
                FlagURLValidated,
                and_(
                    FlagURLValidated.url_id == URL.id,
                    FlagURLValidated.type == URLType.META_URL
                )
            )
            .outerjoin(
                LinkBatchURL,
                LinkBatchURL.url_id == URL.id
            )
            .options(
                selectinload(URL.confirmed_agencies),
            )
            .limit(100)
            .offset((self.page - 1) * 100)
        )

        mappings: Sequence[RowMapping] = await self.sh.mappings(session, query=query)
        responses: list[MetaURLGetResponse] = []

        for mapping in mappings:
            url: URL = mapping[URL]
            url_id: int = mapping[URL.id]
            url_url: str = mapping[URL.url]
            url_name: str = mapping[URL.name]
            url_agency_ids: list[int] = []
            for agency in url.confirmed_agencies:
                url_agency_ids.append(agency.agency_id)
            url_description: str | None = mapping[URL.description]
            link_batch_url_batch_id: int | None = mapping[LinkBatchURL.batch_id]
            responses.append(
                MetaURLGetResponse(
                    url_id=url_id,
                    url=url_url,
                    name=url_name,
                    agency_ids=url_agency_ids,
                    description=url_description,
                    batch_id=link_batch_url_batch_id,
                )
            )

        return MetaURLGetOuterResponse(
            results=responses,
        )
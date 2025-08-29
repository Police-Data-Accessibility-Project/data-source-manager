from sqlalchemy.ext.asyncio import AsyncSession

from src.core.enums import RecordType
from src.db.dtos.url.mapping import URLMapping
from src.db.models.impl.flag.url_validated.enums import URLValidatedType
from src.db.models.impl.flag.url_validated.pydantic import FlagURLValidatedPydantic
from src.db.models.impl.url.core.enums import URLSource
from src.db.models.impl.url.core.pydantic.insert import URLInsertModel
from src.db.queries.base.builder import QueryBuilderBase

from src.db.helpers.session import session_helper as sh

class AddMetaURLsQueryBuilder(QueryBuilderBase):

    """Add Meta URLs to DB with:
    - Record type set to CONTACT_INFO_AND_AGENCY_META
    - Validation Flag added as META_URL
    - Source set to DATA_SOURCES
    """
    def __init__(self, urls: list[str]):
        super().__init__()
        self.urls = urls

    async def run(self, session: AsyncSession) -> list[URLMapping]:
        # Add URLs
        url_inserts: list[URLInsertModel] = []
        for url in self.urls:
            url_inserts.append(
                URLInsertModel(
                    url=url,
                    record_type=RecordType.CONTACT_INFO_AND_AGENCY_META,
                    source=URLSource.DATA_SOURCES
                )
            )
        url_ids: list[int] = await sh.bulk_insert(session, models=url_inserts, return_ids=True)

        # Connect with URLs
        mappings: list[URLMapping] = [
            URLMapping(
                url=url,
                url_id=url_id,
            )
            for url, url_id in zip(self.urls, url_ids)
        ]

        # Add Validation Flags
        flag_inserts: list[FlagURLValidatedPydantic] = []
        for url_id in url_ids:
            flag_inserts.append(
                FlagURLValidatedPydantic(
                    url_id=url_id,
                    type=URLValidatedType.META_URL
                )
            )
        await sh.bulk_insert(session, models=flag_inserts)

        return mappings

from sqlalchemy import update

from src.core.enums import RecordType
from src.db.models.impl.flag.url_validated.enums import URLType
from src.db.models.impl.flag.url_validated.pydantic import FlagURLValidatedPydantic
from src.db.models.impl.flag.url_validated.sqlalchemy import FlagURLValidated
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.templates.requester import RequesterBase

from src.db.helpers.session import session_helper as sh

class UpdateMetaURLsUpdateURLAndValidationFlagsRequester(RequesterBase):

    async def update_validation_flags(self, url_ids: list[int]) -> None:
        """Set validation flag for URLs to Meta URL"""
        query = (
            update(
                FlagURLValidated
            )
            .where(
                FlagURLValidated.url_id.in_(url_ids)
            )
            .values(
                type=URLType.META_URL
            )
        )
        await self.session.execute(query)

    async def add_validation_flags(self, url_ids: list[int]) -> None:
        inserts: list[FlagURLValidatedPydantic] = []
        for url_id in url_ids:
            flag = FlagURLValidatedPydantic(
                url_id=url_id,
                type=URLType.META_URL,
            )
            inserts.append(flag)

        await sh.bulk_insert(self.session, models=inserts)

    async def update_urls(self, url_ids: list[int]) -> None:
        """Update URLs and set record type to Contact Info and Agency Meta"""
        query = (
            update(
                URL
            )
            .values(
                record_type=RecordType.CONTACT_INFO_AND_AGENCY_META,
            )
            .where(
                URL.id.in_(url_ids)
            )
        )
        await self.session.execute(query)
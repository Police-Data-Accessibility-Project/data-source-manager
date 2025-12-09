from typing import Any

from sqlalchemy import update, case
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.url.operators.validate.queries.get.models.response import GetURLsForAutoValidationResponse
from src.db.helpers.session import session_helper as sh
from src.db.models.impl.flag.auto_validated.pydantic import FlagURLAutoValidatedPydantic
from src.db.models.impl.flag.url_validated.pydantic import FlagURLValidatedPydantic
from src.db.models.impl.link.url_agency.pydantic import LinkURLAgencyPydantic
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.record_type.pydantic import URLRecordTypePydantic
from src.db.queries.base.builder import QueryBuilderBase


class InsertURLAutoValidationsQueryBuilder(QueryBuilderBase):

    def __init__(self, responses: list[GetURLsForAutoValidationResponse]):
        super().__init__()
        self._responses = responses

    async def run(self, session: AsyncSession) -> Any:
        url_record_types: list[URLRecordTypePydantic] = []
        link_url_agencies: list[LinkURLAgencyPydantic] = []
        url_validated_flags: list[FlagURLValidatedPydantic] = []
        url_auto_validated_flags: list[FlagURLAutoValidatedPydantic] = []

        for response in self._responses:
            if response.agency_id is not None:
                link_url_agency: LinkURLAgencyPydantic = LinkURLAgencyPydantic(
                    url_id=response.url_id,
                    agency_id=response.agency_id
                )
                link_url_agencies.append(link_url_agency)

            if response.record_type is not None:
                url_record_type: URLRecordTypePydantic = URLRecordTypePydantic(
                    url_id=response.url_id,
                    record_type=response.record_type
                )
                url_record_types.append(url_record_type)

            url_validated_flag: FlagURLValidatedPydantic = FlagURLValidatedPydantic(
                url_id=response.url_id,
                type=response.url_type
            )
            url_validated_flags.append(url_validated_flag)

            url_auto_validated_flag: FlagURLAutoValidatedPydantic = FlagURLAutoValidatedPydantic(
                url_id=response.url_id,
            )
            url_auto_validated_flags.append(url_auto_validated_flag)

        for inserts in [
            link_url_agencies,
            url_record_types,
            url_validated_flags,
            url_auto_validated_flags,
        ]:
            await sh.bulk_insert(session, models=inserts)

        await self.update_urls(session)


    async def update_urls(self, session: AsyncSession) -> Any:
        id_to_name: dict[int, str] = {}
        for response in self._responses:
            if response.name is not None:
                id_to_name[response.url_id] = response.name

        if len(id_to_name) == 0:
            return

        stmt = (
            update(URL)
            .where(URL.id.in_(id_to_name.keys()))
            .values(
                name=case(
                    {id_: val for id_, val in id_to_name.items()},
                    value=URL.id
                )
            )
        )

        await session.execute(stmt)

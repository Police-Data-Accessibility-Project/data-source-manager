from sqlalchemy.ext.asyncio import AsyncSession

from src.core.enums import RecordType
from src.db.models.impl.flag.url_validated.enums import URLType
from src.db.templates.requester import RequesterBase


class URLSuggestRequester(RequesterBase):

    def __init__(
        self,
        session: AsyncSession,
        url_id: int
    ):
        super().__init__(session=session)
        self.url_id = url_id

    async def optionally_add_url_type_suggestion(
        self,
        url_type: URLType | None
    ) -> None:
        if url_type is None:
            return
        # TODO

    async def optionally_add_record_type_suggestion(self, record_type: RecordType | None):
        if record_type is None:
            return
        # TODO

    async def optionally_add_agency_id_suggestions(self, agency_ids: list[int]):
        if len(agency_ids) == 0:
            return
        # TODO

    async def optionally_add_name_suggestion(self, name: str | None):
        if name is None:
            return
        # TODO



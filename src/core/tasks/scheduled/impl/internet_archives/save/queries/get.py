from typing import Sequence

from sqlalchemy import RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.scheduled.impl.internet_archives.save.models.entry import InternetArchivesSaveTaskEntry
from src.core.tasks.scheduled.impl.internet_archives.save.queries.shared.get_valid_entries import \
    IA_SAVE_VALID_ENTRIES_QUERY
from src.db.helpers.session import session_helper as sh
from src.db.queries.base.builder import QueryBuilderBase


class GetURLsForInternetArchivesSaveTaskQueryBuilder(QueryBuilderBase):

    async def run(self, session: AsyncSession) -> list[InternetArchivesSaveTaskEntry]:
        query = (
            IA_SAVE_VALID_ENTRIES_QUERY
            # Limit to 15, which is the maximum number of URLs that can be saved at once.
            .limit(15)
        )

        db_mappings: Sequence[RowMapping] = await sh.mappings(session, query=query)
        return [
            InternetArchivesSaveTaskEntry(
                url_id=mapping["id"],
                url=mapping["url"],
                is_new=mapping["is_new"],
            ) for mapping in db_mappings
        ]
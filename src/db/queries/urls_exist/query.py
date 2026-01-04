from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.queries.urls_exist.model import URLExistsResult
from src.db.helpers.session import session_helper as sh
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.queries.base.builder import QueryBuilderBase
from src.util.models.full_url import FullURL


class URLsExistInDBQueryBuilder(QueryBuilderBase):
    """Checks if URLs exist in the database."""

    def __init__(self, full_urls: list[FullURL]):
        super().__init__()
        self.full_urls = full_urls
        self.id_form_urls = [
            url.id_form
            for url in full_urls
        ]

    async def run(self, session: AsyncSession) -> list[URLExistsResult]:
        norm_url = func.rtrim(URL.url, '/').label("norm_url")

        query = select(
            URL.id,
            norm_url
        ).where(
            norm_url.in_(self.id_form_urls)
        )
        db_mappings = await sh.mappings(session, query=query)

        url_to_id_map: dict[str, int] = {
            row["norm_url"]: row["id"]
            for row in db_mappings
        }
        id_to_db_url_map: dict[int, FullURL] = {
            row["id"]: FullURL(row["norm_url"])
            for row in db_mappings
        }
        results: list[URLExistsResult] = []
        for full_url in self.full_urls:
            url_id: int | None = url_to_id_map.get(full_url.id_form)
            db_url: FullURL | None = id_to_db_url_map.get(url_id)
            result = URLExistsResult(
                query_url=full_url,
                db_url=db_url,
                url_id=url_id
            )
            results.append(result)

        return results
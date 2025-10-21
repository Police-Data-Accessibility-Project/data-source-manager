from sqlalchemy.ext.asyncio import AsyncSession

from src.api.endpoints.suggest.url.models.request import URLSuggestionRequest
from src.api.endpoints.suggest.url.models.response.enums import URLSuggestResultEnum
from src.api.endpoints.suggest.url.models.response.model import URLSuggestResponse
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.queries.base.builder import QueryBuilderBase
from src.db.queries.urls_exist.model import URLExistsResult
from src.db.queries.urls_exist.query import URLsExistInDBQueryBuilder
from src.db.queries.urls_exist.requester import URLSuggestRequester
from src.util.models.full_url import FullURL


class URLSuggestQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        request: URLSuggestionRequest
    ):
        super().__init__()
        self.request = request

    async def run(self, session: AsyncSession) -> URLSuggestResponse:
        # Clean URL
        full_url = FullURL(self.request.url)

        # Check if already exists in database
        url_exists_result: URLExistsResult = (await URLsExistInDBQueryBuilder(
            [full_url]
        ).run(session))[0]
        if url_exists_result.url_id is not None:
            return URLSuggestResponse(
                url_id=url_exists_result.url_id,
                result=URLSuggestResultEnum.DUPLICATE,
                msg=f"URL Already Exists In Database with ID {url_exists_result.url_id}"
            )

        # Add URL
        url = URL(
            scheme=full_url.scheme,
            url=full_url.id_form,
            trailing_slash=full_url.has_trailing_slash,
        )
        session.add(url)
        await session.flush()
        url_id: int = url.id

        try:
            requester = URLSuggestRequester(session=session, url_id=url_id)

            # Optionally add other annotations
            await requester.optionally_add_url_type_suggestion(self.request.url_type)

            await requester.optionally_add_record_type_suggestion(self.request.record_type)

            await requester.optionally_add_agency_id_suggestions(self.request.agency_ids)

            await requester.optionally_add_name_suggestion(self.request.name)

            # If cleaned URL matches original URL, return as ACCEPTED
            return URLSuggestResponse(
                url_id=url_id,
                result=URLSuggestResultEnum.ACCEPTED,
                msg="URL was accepted"
            )

        except Exception as e:
            return URLSuggestResponse(
                url_id=url_id,
                result=URLSuggestResultEnum.ACCEPTED_WITH_ERRORS,
                msg=f"The URL was accepted, but there were errors in adding provided annotations: {e}"
            )


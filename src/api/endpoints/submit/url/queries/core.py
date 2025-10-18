
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.endpoints.submit.url.enums import URLSubmissionStatus
from src.api.endpoints.submit.url.models.request import URLSubmissionRequest
from src.api.endpoints.submit.url.models.response import URLSubmissionResponse
from src.api.endpoints.submit.url.queries.convert import convert_invalid_url_to_url_response, \
    convert_duplicate_urls_to_url_response
from src.api.endpoints.submit.url.queries.dedupe import DeduplicateURLQueryBuilder
from src.collectors.enums import URLStatus
from src.db.models.impl.link.user_name_suggestion.sqlalchemy import LinkUserNameSuggestion
from src.db.models.impl.link.user_suggestion_not_found.users_submitted_url.sqlalchemy import LinkUserSubmittedURL
from src.db.models.impl.url.core.enums import URLSource
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.suggestion.agency.user import UserUrlAgencySuggestion
from src.db.models.impl.url.suggestion.location.user.sqlalchemy import UserLocationSuggestion
from src.db.models.impl.url.suggestion.name.enums import NameSuggestionSource
from src.db.models.impl.url.suggestion.name.sqlalchemy import URLNameSuggestion
from src.db.models.impl.url.suggestion.record_type.user import UserRecordTypeSuggestion
from src.db.queries.base.builder import QueryBuilderBase
from src.db.utils.validate import is_valid_url
from src.util.models.url_and_scheme import URLAndScheme
from src.util.url import clean_url, get_url_and_scheme


class SubmitURLQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        request: URLSubmissionRequest,
        user_id: int
    ):
        super().__init__()
        self.request = request
        self.user_id = user_id

    async def run(self, session: AsyncSession) -> URLSubmissionResponse:
        url_original: str = self.request.url

        # Filter out invalid URLs
        valid: bool = is_valid_url(url_original)
        if not valid:
            return convert_invalid_url_to_url_response(url_original)

        # Clean URL
        url_clean: str = clean_url(url_original)

        url_and_scheme: URLAndScheme = get_url_and_scheme(url_clean)

        # Check if duplicate
        is_duplicate: bool = await DeduplicateURLQueryBuilder(url=url_and_scheme.url).run(session)
        if is_duplicate:
            return convert_duplicate_urls_to_url_response(
                clean_url=url_clean,
                original_url=url_original
            )

        # Submit URLs and get URL id

        # Add URL
        url_insert = URL(
            url=url_and_scheme.url,
            scheme=url_and_scheme.scheme,
            source=URLSource.MANUAL,
            status=URLStatus.OK,
            trailing_slash=url_and_scheme.url.endswith('/'),
        )
        session.add(url_insert)
        await session.flush()

        # Add Link
        link = LinkUserSubmittedURL(
            url_id=url_insert.id,
            user_id=self.user_id,
        )
        session.add(link)

        # Add record type as suggestion if exists
        if self.request.record_type is not None:
            rec_sugg = UserRecordTypeSuggestion(
                user_id=self.user_id,
                url_id=url_insert.id,
                record_type=self.request.record_type.value
            )
            session.add(rec_sugg)

        # Add name as suggestion if exists
        if self.request.name is not None:
            name_sugg = URLNameSuggestion(
                url_id=url_insert.id,
                suggestion=self.request.name,
                source=NameSuggestionSource.USER
            )
            session.add(name_sugg)
            await session.flush()

            link_name_sugg = LinkUserNameSuggestion(
                suggestion_id=name_sugg.id,
                user_id=self.user_id
            )
            session.add(link_name_sugg)



        # Add location ID as suggestion if exists
        if self.request.location_id is not None:
            loc_sugg = UserLocationSuggestion(
                user_id=self.user_id,
                url_id=url_insert.id,
                location_id=self.request.location_id
            )
            session.add(loc_sugg)

        # Add agency ID as suggestion if exists
        if self.request.agency_id is not None:
            agen_sugg = UserUrlAgencySuggestion(
                user_id=self.user_id,
                url_id=url_insert.id,
                agency_id=self.request.agency_id
            )
            session.add(agen_sugg)

        if url_clean == url_original:
            status = URLSubmissionStatus.ACCEPTED_AS_IS
        else:
            status = URLSubmissionStatus.ACCEPTED_WITH_CLEANING

        return URLSubmissionResponse(
            url_original=url_original,
            url_cleaned=url_clean,
            status=status,
            url_id=url_insert.id,
        )

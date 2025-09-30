from typing import Any, Counter

from sqlalchemy.ext.asyncio import AsyncSession

from src.api.endpoints.submit.urls.enums import URLSubmissionStatus
from src.api.endpoints.submit.urls.models.response import URLBatchSubmissionResponse, URLSubmissionResponse
from src.api.endpoints.submit.urls.queries.clean.core import clean_urls
from src.api.endpoints.submit.urls.queries.clean.response import CleanURLResponse
from src.api.endpoints.submit.urls.queries.convert import convert_invalid_urls_to_url_response
from src.api.endpoints.submit.urls.queries.deduplicate.core import DeduplicateURLsQueryBuilder
from src.api.endpoints.submit.urls.queries.deduplicate.response import DeduplicateURLResponse
from src.api.endpoints.submit.urls.queries.validate.core import validate_urls
from src.api.endpoints.submit.urls.queries.validate.response import ValidateURLResponse
from src.db.queries.base.builder import QueryBuilderBase


class SubmitURLsQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        urls: list[str],
    ):
        super().__init__()
        self.urls = urls

    async def run(self, session: AsyncSession) -> URLBatchSubmissionResponse:
        url_responses: list[URLSubmissionResponse] = []
        url_clean_original_mapping: dict[str, str] = {}

        # Filter out invalid URLs
        validate_response: ValidateURLResponse = validate_urls(self.urls)
        invalid_url_responses: list[URLSubmissionResponse] = convert_invalid_urls_to_url_response(
            validate_response.invalid_urls
        )
        url_responses.extend(invalid_url_responses)
        valid_urls: list[str] = validate_response.valid_urls

        # Clean URLs
        clean_url_responses: list[CleanURLResponse] = clean_urls(valid_urls)
        for clean_url_response in clean_url_responses:
            url_clean_original_mapping[clean_url_response.url_cleaned] = \
                clean_url_response.url_original

        # Filter out within-batch duplicates
        clean_url_set: set[str] = set()
        for clean_url_response in clean_url_responses:
            cur = clean_url_response
            if cur.url_cleaned in clean_url_set:
                url_responses.append(
                    URLSubmissionResponse(
                        url_original=cur.url_original,
                        url_cleaned=cur.url_cleaned,
                        status=URLSubmissionStatus.BATCH_DUPLICATE,
                        url_id=None,
                    )
                )
            else:
                clean_url_set.add(cur.url_cleaned)
        clean_url_list: list[str] = list(clean_url_set)

        # Filter out within-database duplicates
        deduplicate_response: DeduplicateURLResponse = \
            await DeduplicateURLsQueryBuilder(clean_url_list).run(session)


        # Submit URLs and get URL ids

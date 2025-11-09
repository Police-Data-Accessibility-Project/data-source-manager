import pytest

from src.api.endpoints.submit.url.enums import URLSubmissionStatus
from src.api.endpoints.submit.url.models.request import URLSubmissionRequest
from src.api.endpoints.submit.url.models.response import URLSubmissionResponse
from src.core.enums import RecordType
from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.link.user_name_suggestion.sqlalchemy import LinkUserNameSuggestion
from src.db.models.impl.link.user_suggestion_not_found.users_submitted_url.sqlalchemy import LinkUserSubmittedURL
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.suggestion.agency.user import UserURLAgencySuggestion
from src.db.models.impl.url.suggestion.location.user.sqlalchemy import UserLocationSuggestion
from src.db.models.impl.url.suggestion.name.enums import NameSuggestionSource
from src.db.models.impl.url.suggestion.name.sqlalchemy import URLNameSuggestion
from src.db.models.impl.url.suggestion.record_type.user import UserRecordTypeSuggestion
from tests.helpers.api_test_helper import APITestHelper
from tests.helpers.data_creator.core import DBDataCreator
from tests.helpers.data_creator.models.creation_info.locality import LocalityCreationInfo


@pytest.mark.asyncio
async def test_maximal(
    api_test_helper: APITestHelper,
    adb_client_test: AsyncDatabaseClient,
    db_data_creator: DBDataCreator,
    pittsburgh_locality: LocalityCreationInfo
):

    agency_id: int = await db_data_creator.agency()

    response: URLSubmissionResponse = await api_test_helper.request_validator.submit_url(
        request=URLSubmissionRequest(
            url="www.example.com",
            record_type=RecordType.INCARCERATION_RECORDS,
            name="Example URL",
            location_id=pittsburgh_locality.location_id,
            agency_id=agency_id,
        )
    )

    assert response.status == URLSubmissionStatus.ACCEPTED_AS_IS
    assert response.url_id is not None
    url_id: int = response.url_id

    adb_client: AsyncDatabaseClient = adb_client_test
    urls: list[URL] = await adb_client.get_all(URL)
    assert len(urls) == 1
    url: URL = urls[0]
    assert url.id == url_id
    assert url.url == "www.example.com"

    links: list[LinkUserSubmittedURL] = await adb_client.get_all(LinkUserSubmittedURL)
    assert len(links) == 1
    link: LinkUserSubmittedURL = links[0]
    assert link.url_id == url_id

    agen_suggs: list[UserURLAgencySuggestion] = await adb_client.get_all(UserURLAgencySuggestion)
    assert len(agen_suggs) == 1
    agen_sugg: UserURLAgencySuggestion = agen_suggs[0]
    assert agen_sugg.url_id == url_id
    assert agen_sugg.agency_id == agency_id

    loc_suggs: list[UserLocationSuggestion] = await adb_client.get_all(UserLocationSuggestion)
    assert len(loc_suggs) == 1
    loc_sugg: UserLocationSuggestion = loc_suggs[0]
    assert loc_sugg.url_id == url_id
    assert loc_sugg.location_id == pittsburgh_locality.location_id

    name_sugg: list[URLNameSuggestion] = await adb_client.get_all(URLNameSuggestion)
    assert len(name_sugg) == 1
    name_sugg: URLNameSuggestion = name_sugg[0]
    assert name_sugg.url_id == url_id
    assert name_sugg.suggestion == "Example URL"
    assert name_sugg.source == NameSuggestionSource.USER

    name_link_suggs: list[LinkUserNameSuggestion] = await adb_client.get_all(LinkUserNameSuggestion)
    assert len(name_link_suggs) == 1
    name_link_sugg: LinkUserNameSuggestion = name_link_suggs[0]
    assert name_link_sugg.suggestion_id == name_sugg.id

    rec_suggs: list[UserRecordTypeSuggestion] = await adb_client.get_all(UserRecordTypeSuggestion)
    assert len(rec_suggs) == 1
    rec_sugg: UserRecordTypeSuggestion = rec_suggs[0]
    assert rec_sugg.url_id == url_id
    assert rec_sugg.record_type == RecordType.INCARCERATION_RECORDS.value

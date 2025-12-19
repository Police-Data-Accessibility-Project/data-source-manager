from uuid import UUID

import pytest
from sqlalchemy import select

from src.core.enums import RecordType
from src.db.client.async_ import AsyncDatabaseClient
from src.db.dtos.url.mapping_.simple import SimpleURLMapping
from src.db.enums import ChangeLogOperationType
from src.db.models.impl.annotation.agency.anon.sqlalchemy import AnnotationAgencyAnon
from src.db.models.impl.annotation.agency.auto.subtask.enum import AutoAgencyIDSubtaskType, SubtaskDetailCode
from src.db.models.impl.annotation.agency.auto.subtask.sqlalchemy import AnnotationAgencyAutoSubtask
from src.db.models.impl.annotation.agency.auto.suggestion.sqlalchemy import AnnotationAgencyAutoSuggestion
from src.db.models.impl.annotation.agency.user.sqlalchemy import AnnotationAgencyUser
from src.db.models.impl.annotation.location.anon.sqlalchemy import AnnotationLocationAnon
from src.db.models.impl.annotation.location.auto.subtask.enums import LocationIDSubtaskType
from src.db.models.impl.annotation.location.auto.subtask.sqlalchemy import AnnotationLocationAutoSubtask
from src.db.models.impl.annotation.location.auto.suggestion.sqlalchemy import AnnotationLocationAutoSuggestion
from src.db.models.impl.annotation.location.user.sqlalchemy import AnnotationLocationUser
from src.db.models.impl.annotation.name.suggestion.enums import NameSuggestionSource
from src.db.models.impl.annotation.name.suggestion.sqlalchemy import AnnotationNameSuggestion
from src.db.models.impl.annotation.record_type.anon.sqlalchemy import AnnotationAnonRecordType
from src.db.models.impl.annotation.url_type.anon.sqlalchemy import AnnotationAnonURLType
from src.db.models.impl.change_log import ChangeLog
from src.db.models.impl.flag.checked_for_ia.sqlalchemy import FlagURLCheckedForInternetArchives
from src.db.models.impl.flag.root_url.sqlalchemy import FlagRootURL
from src.db.models.impl.flag.url_suspended.sqlalchemy import FlagURLSuspended
from src.db.models.impl.flag.url_validated.enums import URLType
from src.db.models.impl.link.batch_url.sqlalchemy import LinkBatchURL
from src.db.models.impl.link.url_redirect_url.sqlalchemy import LinkURLRedirectURL
from src.db.models.impl.link.urls_root_url.sqlalchemy import LinkURLRootURL
from src.db.models.impl.annotation.name.user.sqlalchemy import LinkUserNameSuggestion
from src.db.models.impl.link.user_suggestion_not_found.agency.sqlalchemy import LinkUserSuggestionAgencyNotFound
from src.db.models.impl.link.user_suggestion_not_found.location.sqlalchemy import LinkUserSuggestionLocationNotFound
from src.db.models.impl.link.user_suggestion_not_found.users_submitted_url.sqlalchemy import LinkUserSubmittedURL
from src.db.models.impl.url.checked_for_duplicate import URLCheckedForDuplicate
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.html.compressed.sqlalchemy import URLCompressedHTML
from src.db.models.impl.url.html.content.sqlalchemy import URLHTMLContent
from src.db.models.impl.url.internet_archives.probe.sqlalchemy import URLInternetArchivesProbeMetadata
from src.db.models.impl.url.internet_archives.save.sqlalchemy import URLInternetArchivesSaveMetadata
from src.db.models.impl.url.screenshot.sqlalchemy import URLScreenshot
from src.db.models.impl.annotation.record_type.auto.sqlalchemy import AnnotationAutoRecordType
from src.db.models.impl.annotation.record_type.user.user import AnnotationUserRecordType
from src.db.models.impl.annotation.url_type.auto.sqlalchemy import AnnotationAutoURLType
from src.db.models.impl.annotation.url_type.user.sqlalchemy import AnnotationUserURLType
from src.db.models.impl.url.task_error.sqlalchemy import URLTaskError
from src.db.models.impl.url.web_metadata.sqlalchemy import URLWebMetadata
from src.db.queries.implementations.anonymous_session import MakeAnonymousSessionQueryBuilder
from tests.helpers.api_test_helper import APITestHelper
from tests.helpers.data_creator.core import DBDataCreator
from tests.helpers.data_creator.models.creation_info.locality import LocalityCreationInfo


@pytest.mark.asyncio
async def test_any_url(
    pittsburgh_locality: LocalityCreationInfo,
    db_data_creator: DBDataCreator,
    test_agency_id: int,
    api_test_helper: APITestHelper
):
    """
    Test that deletion works properly for a URL that has all possible attributes
    that any URL could have
    """

    url_id: int = await _setup(
        ddc=db_data_creator,
        pittsburgh_id=pittsburgh_locality.location_id,
        agency_id=test_agency_id
    )
    api_test_helper.request_validator.delete_v3(
        f"url/{url_id}"
    )
    await _check_results(url_id, dbc=db_data_creator.adb_client)



async def _check_results(
    url_id: int,
    dbc: AsyncDatabaseClient
) -> None:
    # There should be only two urls present in the database, neither matching URL id
    urls: list[URL] = await dbc.get_all(URL)
    assert len(urls) == 2
    assert url_id not in (url.id for url in urls)

    # For the following models, there should no longer be any entries in the database.
    models = [
        # Batch Link
        LinkBatchURL,
        # MISCELLANEOUS
        ## Flag Root URL
        FlagRootURL,
        ## URL Task Error
        URLTaskError,
        ## URL Checked for Duplicate
        URLCheckedForDuplicate,
        ## Flag URL Suspended
        FlagURLSuspended,
        # LINKS
        ## Link URLs Redirect URL
        LinkURLRedirectURL,
        ## Link URLs Root URL
        LinkURLRootURL,
        ## Link User Submitted URLs
        LinkUserSubmittedURL,
        ## Link User Suggestion Agency Not Found
        LinkUserSuggestionAgencyNotFound,
        ## Link User Suggestion Location Not Found
        LinkUserSuggestionLocationNotFound,
        # WEB DATA
        ## URL Compressed HTML
        URLCompressedHTML,
        ## URL HTML Content
        URLHTMLContent,
        ## URL Screenshot
        URLScreenshot,
        ## URL Web Metadata
        URLWebMetadata,
        # INTERNET ARCHIVES
        ## Flag URL Checked for Internet Archives
        FlagURLCheckedForInternetArchives,
        ## URL Internet Archives Probe Metadata
        URLInternetArchivesProbeMetadata,
        ## URL Internet Archives Save Metadata
        URLInternetArchivesSaveMetadata,
        # ANNOTATIONS
        ## AUTO
        ### Agency
        AnnotationAgencyAutoSubtask,
        AnnotationAgencyAutoSuggestion,
        ### Record Type
        AnnotationAutoRecordType,
        ### URL Type
        AnnotationAutoURLType,
        ### Location
        AnnotationLocationAutoSubtask,
        AnnotationLocationAutoSuggestion,
        ## USER
        ### Agency
        AnnotationAgencyUser,
        ### Record Type
        AnnotationUserRecordType,
        ### URL Type
        AnnotationUserURLType,
        ### Location
        AnnotationLocationUser,
        AnnotationNameSuggestion,
        ## ANONYMOUS
        ### Agency
        AnnotationAgencyAnon,
        ### Location
        AnnotationLocationAnon,
        ### Record Type
        AnnotationAnonRecordType,
        ### URL Type
        AnnotationAnonURLType,
    ]
    for model in models:
        assert await dbc.get_all(model) == []

    # The Change Log should show, at minimum, the deletion of the URL
    query = (
        select(
            ChangeLog
        )
        .where(
            ChangeLog.table_name == "urls",
            ChangeLog.operation_type == ChangeLogOperationType.DELETE
        )
    )
    result = dbc.one_or_none(query)
    assert result is not None


async def _setup(
    ddc: DBDataCreator,
    pittsburgh_id: int,
    agency_id: int
) -> int:
    dbc: AsyncDatabaseClient = ddc.adb_client
    # URL & Batch Link
    url: SimpleURLMapping = (await ddc.create_urls(
        record_type=None
    ))[0]

    # MISCELLANEOUS
    ## Flag Root URL
    await ddc.flag_as_root(url_ids=[url.url_id])
    ## URL Task Error
    ### Task
    task_id: int = await ddc.task(url_ids=[url.url_id])
    ### Error
    await ddc.task_errors(url_ids=[url.url_id], task_id=task_id)
    ## URL Checked for Duplicate
    await dbc.add(
        URLCheckedForDuplicate(
            url_id=url.url_id
        )
    )
    ## Flag URL Suspended
    await dbc.add(
        FlagURLSuspended(
            url_id=url.url_id
        )
    )
    # LINKS
    ## Link URLs Redirect URL
    ### Additional url
    additional_url: SimpleURLMapping = (await ddc.create_urls(
        record_type=None
    ))[0]
    ### Redirect url
    await dbc.add(
        LinkURLRedirectURL(
            source_url_id=url.url_id,
            destination_url_id=additional_url.url_id
        )
    )
    ### (We will go in both directions even though this should technically not be legal)
    await dbc.add(
        LinkURLRedirectURL(
            source_url_id=additional_url.url_id,
            destination_url_id=url.url_id
        )
    )
    ## Link URLs Root URL
    ### (Again, will go in both directions despite this not being legal)
    root_url: SimpleURLMapping = (await ddc.create_urls(
        record_type=None
    ))[0]
    await dbc.add(
        LinkURLRootURL(
            url_id=url.url_id,
            root_url_id=root_url.url_id
        )
    )
    await dbc.add(
        LinkURLRootURL(
            url_id=root_url.url_id,
            root_url_id=url.url_id
        )
    )
    ## Link User Submitted URL
    await dbc.add(
        LinkUserSubmittedURL(
            url_id=url.url_id,
            user_id=1
        )
    )
    ## Link User Suggestion Agency Not Found
    await dbc.add(
        LinkUserSuggestionAgencyNotFound(
            url_id=url.url_id,
            user_id=1
        )
    )
    ## Link User Suggestion Location Not Found
    await dbc.add(
        LinkUserSuggestionLocationNotFound(
            url_id=url.url_id,
            user_id=1
        )
    )
    # WEB DATA
    ## URL Compressed HTML
    await ddc.add_compressed_html(
        url_ids=[url.url_id]
    )
    ## URL HTML Content
    await dbc.add(
        URLHTMLContent(
            url_id=url.url_id,
            content_type="Title",
            content="Test Title"
        )
    )
    ## URL Screenshot
    await dbc.add(
        URLScreenshot(
            url_id=url.url_id,
            content=b"Test Screenshot",
            file_size=1024
        )
    )
    ## URL Web Metadata
    await ddc.create_web_metadata(
        url_ids=[url.url_id]
    )
    # INTERNET ARCHIVES
    ## Flag URL Checked for Internet Archives
    await dbc.add(
        FlagURLCheckedForInternetArchives(
            url_id=url.url_id,
            success=True
        )
    )
    ## URL Internet Archives Probe Metadata
    await dbc.add(
        URLInternetArchivesProbeMetadata(
            url_id=url.url_id,
            archive_url="https://example.com",
            digest="test_digest",
            length=1024,
        )
    )
    ## URL Internet Archives Save Metadata
    await dbc.add(
        URLInternetArchivesSaveMetadata(
            url_id=url.url_id,
        )
    )
    # ANNOTATIONS
    ## AUTO
    ### Agency
    #### Subtask
    agency_subtask_id: int = await dbc.add(
        AnnotationAgencyAutoSubtask(
            url_id=url.url_id,
            task_id=task_id,
            agencies_found=True,
            type=AutoAgencyIDSubtaskType.NLP_LOCATION_MATCH,
            detail=SubtaskDetailCode.NO_DETAILS
        ),
        return_id=True
    )
    ### Suggestion
    await dbc.add(
        AnnotationAgencyAutoSuggestion(
            subtask_id=agency_subtask_id,
            agency_id=agency_id,
            confidence=60
        )
    )
    ### Record Type
    await dbc.add(
        AnnotationAutoRecordType(
            url_id=url.url_id,
            record_type=RecordType.BOOKING_REPORTS.value
        )
    )
    ### Relevant
    await dbc.add(
        AnnotationAutoURLType(
            url_id=url.url_id,
            relevant=True,
            confidence=0.5,
            model_name="Test Model"
        )
    )
    ### Location
    #### Subtask
    location_subtask_id: int = await dbc.add(
        AnnotationLocationAutoSubtask(
            url_id=url.url_id,
            task_id=task_id,
            locations_found=True,
            type=LocationIDSubtaskType.NLP_LOCATION_FREQUENCY,
        ),
        return_id=True
    )
    #### Suggestion
    await dbc.add(
        AnnotationLocationAutoSuggestion(
            subtask_id=location_subtask_id,
            location_id=pittsburgh_id,
            confidence=50
        )
    )
    ## USER
    ### Agency
    await dbc.add(
        AnnotationAgencyUser(
            url_id=url.url_id,
            user_id=1,
            agency_id=agency_id,
            is_new=False
        )
    )
    ### Record Type
    await dbc.add(
        AnnotationUserRecordType(
            url_id=url.url_id,
            user_id=1,
            record_type=RecordType.BOOKING_REPORTS.value,
        )
    )
    ### URL Type
    await dbc.add(
        AnnotationUserURLType(
            url_id=url.url_id,
            type=URLType.INDIVIDUAL_RECORD,
            user_id=1
        )
    )
    ### Location
    await dbc.add(
        AnnotationLocationUser(
            url_id=url.url_id,
            location_id=pittsburgh_id,
            user_id=1,
        )
    )
    ### Name
    name_suggestion_id: int = await dbc.add(
        AnnotationNameSuggestion(
            url_id=url.url_id,
            suggestion="Test Name",
            source=NameSuggestionSource.USER,
        ),
        return_id=True
    )
    await dbc.add(
        LinkUserNameSuggestion(
            suggestion_id=name_suggestion_id,
            user_id=1,
        )
    )
    session_id: UUID = await dbc.run_query_builder(
        MakeAnonymousSessionQueryBuilder()
    )
    ## ANONYMOUS
    for model in [
        ### Agency
        AnnotationAgencyAnon(
            url_id=url.url_id,
            agency_id=agency_id,
            session_id=session_id,
        ),
        ### Record Type
        AnnotationAnonRecordType(
            url_id=url.url_id,
            record_type=RecordType.BOOKING_REPORTS.value,
            session_id=session_id,
        ),
        ### URL Type
        AnnotationAnonURLType(
            url_id=url.url_id,
            url_type=URLType.INDIVIDUAL_RECORD,
            session_id=session_id,
        ),
        ### Location
        AnnotationLocationAnon(
            url_id=url.url_id,
            location_id=pittsburgh_id,
            session_id=session_id
        )
    ]:
        await dbc.add(model)

    return url.url_id







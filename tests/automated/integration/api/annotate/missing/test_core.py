import pytest
from sqlalchemy import select

from src.db.models.impl.annotation.agency.user.sqlalchemy import AnnotationAgencyUser
from src.db.models.impl.annotation.location.user.sqlalchemy import AnnotationLocationUser
from src.db.models.impl.flag.url_suspended.sqlalchemy import FlagURLSuspended
from src.db.models.impl.link.user_suggestion_not_found.agency.sqlalchemy import LinkUserSuggestionAgencyNotFound
from src.db.models.impl.link.user_suggestion_not_found.location.sqlalchemy import LinkUserSuggestionLocationNotFound
from src.db.models.materialized_views.url_status.enums import URLStatusViewEnum
from src.db.models.materialized_views.url_status.sqlalchemy import URLStatusMaterializedView
from tests.automated.integration.conftest import MOCK_USER_ID
from tests.helpers.data_creator.models.creation_info.locality import LocalityCreationInfo


@pytest.mark.asyncio
async def test_get_missing_annotations_queue(
    api_test_helper,
):
    ath = api_test_helper

    url_ids = [mapping.url_id for mapping in await ath.db_data_creator.create_urls(count=3)]
    qualifying_url_id = url_ids[0]
    unsuspended_url_id = url_ids[1]
    not_seconded_url_id = url_ids[2]

    await ath.db_data_creator.not_found_location_suggestion(url_id=qualifying_url_id)
    await ath.db_data_creator.not_found_location_suggestion(url_id=qualifying_url_id)
    await ath.db_data_creator.not_found_agency_suggestion(url_id=qualifying_url_id)
    await ath.db_data_creator.not_found_agency_suggestion(url_id=qualifying_url_id)
    await ath.adb_client().add(
        FlagURLSuspended(
            url_id=qualifying_url_id
        )
    )

    await ath.db_data_creator.not_found_location_suggestion(url_id=unsuspended_url_id)
    await ath.db_data_creator.not_found_location_suggestion(url_id=unsuspended_url_id)

    await ath.db_data_creator.not_found_agency_suggestion(url_id=not_seconded_url_id)
    await ath.adb_client().add(
        FlagURLSuspended(
            url_id=not_seconded_url_id
        )
    )

    response = ath.request_validator.get(
        url="/annotate/missing"
    )
    entries = response["entries"]

    assert len(entries) == 1
    assert entries[0]["url_id"] == qualifying_url_id
    assert entries[0]["missing_location_count"] == 2
    assert entries[0]["missing_agency_count"] == 2


@pytest.mark.asyncio
async def test_resolve_missing_annotations(
    api_test_helper,
    pittsburgh_locality: LocalityCreationInfo,
    test_agency_id: int,
):
    ath = api_test_helper
    url_id = (await ath.db_data_creator.create_urls(count=1))[0].url_id

    await ath.db_data_creator.not_found_location_suggestion(url_id=url_id)
    await ath.db_data_creator.not_found_location_suggestion(url_id=url_id)
    await ath.db_data_creator.not_found_agency_suggestion(url_id=url_id)
    await ath.db_data_creator.not_found_agency_suggestion(url_id=url_id)
    await ath.adb_client().add(
        FlagURLSuspended(
            url_id=url_id
        )
    )

    response = ath.request_validator.post(
        url=f"/annotate/missing/{url_id}",
        json={
            "location_id": pittsburgh_locality.location_id,
            "agency_id": test_agency_id,
        }
    )
    assert response["message"] == "Missing location/agency annotations resolved."

    queue_response = ath.request_validator.get(
        url="/annotate/missing"
    )
    assert queue_response["entries"] == []

    location_annotations: list[AnnotationLocationUser] = await ath.adb_client().get_all(AnnotationLocationUser)
    agency_annotations: list[AnnotationAgencyUser] = await ath.adb_client().get_all(AnnotationAgencyUser)
    assert len(location_annotations) == 1
    assert len(agency_annotations) == 1

    location_annotation = location_annotations[0]
    agency_annotation = agency_annotations[0]
    assert location_annotation.url_id == url_id
    assert location_annotation.user_id == MOCK_USER_ID
    assert location_annotation.location_id == pittsburgh_locality.location_id
    assert agency_annotation.url_id == url_id
    assert agency_annotation.user_id == MOCK_USER_ID
    assert agency_annotation.agency_id == test_agency_id

    not_found_agency_rows: list[LinkUserSuggestionAgencyNotFound] = await ath.adb_client().get_all(
        LinkUserSuggestionAgencyNotFound
    )
    not_found_location_rows: list[LinkUserSuggestionLocationNotFound] = await ath.adb_client().get_all(
        LinkUserSuggestionLocationNotFound
    )
    suspended_rows: list[FlagURLSuspended] = await ath.adb_client().get_all(FlagURLSuspended)

    assert not_found_agency_rows == []
    assert not_found_location_rows == []
    assert suspended_rows == []


@pytest.mark.asyncio
async def test_missing_annotations_status_code(
    api_test_helper,
):
    ath = api_test_helper
    url_id = (await ath.db_data_creator.create_urls(count=1))[0].url_id

    await ath.db_data_creator.not_found_location_suggestion(url_id=url_id)
    await ath.db_data_creator.not_found_location_suggestion(url_id=url_id)
    await ath.adb_client().add(
        FlagURLSuspended(
            url_id=url_id
        )
    )
    await ath.adb_client().refresh_materialized_views()

    result = await ath.adb_client().execute(
        select(URLStatusMaterializedView).where(
            URLStatusMaterializedView.url_id == url_id
        )
    )
    status_row = result.scalar_one()

    assert status_row.status == URLStatusViewEnum.MISSING_LOCATION_AGENCY.value
    assert status_row.code == 320

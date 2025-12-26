import pytest

from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.link.batch_url.sqlalchemy import LinkBatchURL
from src.db.models.impl.link.location__user_follow import LinkLocationUserFollow
from src.db.models.impl.link.location_batch.sqlalchemy import LinkLocationBatch
from src.db.models.impl.url.core.enums import URLSource
from tests.automated.integration.conftest import MOCK_USER_ID
from tests.helpers.api_test_helper import APITestHelper
from tests.helpers.data_creator.models.creation_info.county import CountyCreationInfo
from tests.helpers.data_creator.models.creation_info.locality import LocalityCreationInfo
from tests.helpers.setup.final_review.core import setup_for_get_next_url_for_final_review
from tests.helpers.setup.final_review.model import FinalReviewSetupInfo


@pytest.mark.asyncio
async def test_annotate_sorting(
    api_test_helper: APITestHelper,
    test_batch_id: int,
    pittsburgh_locality: LocalityCreationInfo,
    allegheny_county: CountyCreationInfo,
):
    """
    Test that annotations are prioritized in the following order:
    - Any manual submissions are prioritized first
    - Then prioritize by number of annotations descending
    - Then prioritize by URL ID ascending (e.g. least recently created)
    """
    ath = api_test_helper
    dbc: AsyncDatabaseClient = ath.adb_client()

    # First URL created should be prioritized in absence of any other factors
    setup_info_first_annotation: FinalReviewSetupInfo = await setup_for_get_next_url_for_final_review(
        db_data_creator=ath.db_data_creator,
        include_user_annotations=False
    )
    get_response_1 = await ath.request_validator.get_next_url_for_all_annotations()
    assert get_response_1.next_annotation is not None
    assert get_response_1.next_annotation.url_info.url_id == setup_info_first_annotation.url_mapping.url_id

    # ...But higher annotation count should take precedence over least recently created
    setup_info_high_annotations: FinalReviewSetupInfo = await setup_for_get_next_url_for_final_review(
        db_data_creator=ath.db_data_creator,
        include_user_annotations=True
    )
    get_response_2 = await ath.request_validator.get_next_url_for_all_annotations()
    assert get_response_2.next_annotation is not None
    assert get_response_2.next_annotation.url_info.url_id == setup_info_high_annotations.url_mapping.url_id

    # ...But manual submissions should take precedence over higher annotation count
    setup_info_manual_submission: FinalReviewSetupInfo = await setup_for_get_next_url_for_final_review(
        db_data_creator=ath.db_data_creator,
        source=URLSource.MANUAL,
        include_user_annotations=True
    )
    get_response_3 = await ath.request_validator.get_next_url_for_all_annotations()
    assert get_response_3.next_annotation is not None
    assert get_response_3.next_annotation.url_info.url_id == setup_info_manual_submission.url_mapping.url_id

    # URL with followed_by_any_user should take precedence over manual submissions

    ## Start by adding a new URL
    setup_info_followed_by_any_user: FinalReviewSetupInfo = await setup_for_get_next_url_for_final_review(
        db_data_creator=ath.db_data_creator,
        include_user_annotations=False
    )
    ## Add a link between that URL's batch and a location
    link_batch_location = LinkLocationBatch(
        batch_id=setup_info_followed_by_any_user.batch_id,
        location_id=pittsburgh_locality.location_id
    )
    await dbc.add(link_batch_location)
    ## Add a link between that location and a user
    link_location_user_follow = LinkLocationUserFollow(
        location_id=pittsburgh_locality.location_id,
        user_id=MOCK_USER_ID + 1 # To ensure it's not the same user we'll be using later on.
    )
    await dbc.add(link_location_user_follow)

    # Run get_next_url_for_all_annotations
    get_response_4 = await ath.request_validator.get_next_url_for_all_annotations()
    # Assert that the URL with followed_by_any_user is returned
    assert get_response_4.next_annotation is not None
    assert get_response_4.next_annotation.url_info.url_id == setup_info_followed_by_any_user.url_mapping.url_id

    # URL whose associated location is followed by this specific user
    # should take precedence over URL whose associated location
    # is followed by any user

    ## Start by adding a new URL
    setup_info_followed_by_annotating_user: FinalReviewSetupInfo = await setup_for_get_next_url_for_final_review(
        db_data_creator=ath.db_data_creator,
        include_user_annotations=False
    )

    ## Add a link between that URL's batch and a location
    link_batch_location = LinkLocationBatch(
        batch_id=setup_info_followed_by_annotating_user.batch_id,
        location_id=allegheny_county.location_id
    )
    await dbc.add(link_batch_location)
    ## Add a link between that location and the mock user
    link_location_user_follow = LinkLocationUserFollow(
        location_id=allegheny_county.location_id,
        user_id=MOCK_USER_ID
    )
    await dbc.add(link_location_user_follow)

    get_response_5 = await ath.request_validator.get_next_url_for_all_annotations()
    # Assert that the URL with followed_by_any_user is returned
    assert get_response_5.next_annotation is not None
    assert get_response_5.next_annotation.url_info.url_id == setup_info_followed_by_annotating_user.url_mapping.url_id


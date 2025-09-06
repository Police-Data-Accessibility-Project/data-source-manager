import pytest

from src.api.endpoints.annotate.agency.post.dto import URLAgencyAnnotationPostInfo
from tests.helpers.setup.annotate_agency.core import setup_for_annotate_agency
from tests.helpers.setup.annotate_agency.model import AnnotateAgencySetupInfo


@pytest.mark.asyncio
async def test_annotate_agency_submit_and_get_next(api_test_helper):
    """
    Test Scenario: Submit and Get Next (no other URL available)
    A URL has been annotated by our User, and no other valid URLs have not been annotated
    Our user should not receive another URL to annotate
    Until another relevant URL is added
    """
    ath = api_test_helper
    setup_info: AnnotateAgencySetupInfo = await setup_for_annotate_agency(
        db_data_creator=ath.db_data_creator,
        url_count=2
    )
    url_ids = setup_info.url_ids

    # User should submit an annotation and receive the next
    response = await ath.request_validator.post_agency_annotation_and_get_next(
        url_id=url_ids[0],
        agency_annotation_post_info=URLAgencyAnnotationPostInfo(
            suggested_agency=await ath.db_data_creator.agency(),
            is_new=False
        )

    )
    assert response.next_annotation is not None

    # User should submit this annotation and receive none for the next
    response = await ath.request_validator.post_agency_annotation_and_get_next(
        url_id=url_ids[1],
        agency_annotation_post_info=URLAgencyAnnotationPostInfo(
            suggested_agency=await ath.db_data_creator.agency(),
            is_new=False
        )
    )
    assert response.next_annotation is None

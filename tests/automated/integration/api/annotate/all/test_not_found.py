import pytest

from src.api.endpoints.annotate.all.post.models.agency import AnnotationPostAgencyInfo
from src.api.endpoints.annotate.all.post.models.location import AnnotationPostLocationInfo
from src.api.endpoints.annotate.all.post.models.name import AnnotationPostNameInfo
from src.api.endpoints.annotate.all.post.models.request import AllAnnotationPostInfo
from src.core.enums import RecordType
from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.flag.url_validated.enums import URLType
from src.db.models.impl.link.user_suggestion_not_found.agency.sqlalchemy import LinkUserSuggestionAgencyNotFound
from src.db.models.impl.link.user_suggestion_not_found.location.sqlalchemy import LinkUserSuggestionLocationNotFound
from tests.helpers.setup.final_review.core import setup_for_get_next_url_for_final_review


@pytest.mark.asyncio
async def test_not_found(
    api_test_helper,
):
    """
    Test that marking a URL as agency or location not found works.
    """
    ath = api_test_helper
    setup_info_1 = await setup_for_get_next_url_for_final_review(
        db_data_creator=ath.db_data_creator, include_user_annotations=True
    )

    post_response_1 = await ath.request_validator.post_all_annotations(
        url_id=setup_info_1.url_mapping.url_id,
        all_annotations_post_info=AllAnnotationPostInfo(
            suggested_status=URLType.DATA_SOURCE,
            record_type=RecordType.ACCIDENT_REPORTS,
            agency_info=AnnotationPostAgencyInfo(not_found=True),
            location_info=AnnotationPostLocationInfo(
                not_found=True,
            ),
            name_info=AnnotationPostNameInfo(
                new_name="New Name"
            )
        )
    )

    adb_client: AsyncDatabaseClient = ath.adb_client()

    not_found_agencies: list[LinkUserSuggestionAgencyNotFound] = await adb_client.get_all(LinkUserSuggestionAgencyNotFound)
    assert len(not_found_agencies) == 1

    not_found_locations: list[LinkUserSuggestionLocationNotFound] = await adb_client.get_all(LinkUserSuggestionLocationNotFound)
    assert len(not_found_locations) == 1
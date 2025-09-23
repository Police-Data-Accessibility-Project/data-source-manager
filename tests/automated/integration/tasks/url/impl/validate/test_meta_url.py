"""
Add a URL with two of the same suggestions for each of the following:
- Agency
- Location
- URL Type (META URL)
And confirm it is validated as META URL
"""
import pytest

from src.api.endpoints.annotate.agency.post.dto import URLAgencyAnnotationPostInfo
from src.core.tasks.url.operators.validate.core import AutoValidateURLTaskOperator
from src.db.models.impl.flag.url_validated.enums import URLType
from tests.helpers.data_creator.core import DBDataCreator
from tests.helpers.data_creator.models.creation_info.locality import LocalityCreationInfo


@pytest.mark.asyncio
async def test_meta_url(
    operator: AutoValidateURLTaskOperator,
    db_data_creator: DBDataCreator,
    pittsburgh_locality: LocalityCreationInfo
):
    # Add one URL
    url_id: int = (await db_data_creator.create_urls(count=1))[0].url_id

    # Create agency
    agency_id: int = await db_data_creator.agency()

    # Add two META URL suggestions
    for i in range(2):
        await db_data_creator.user_relevant_suggestion(
            suggested_status=URLType.META_URL,
            url_id=url_id,
            user_id=i,
        )

    # Assert operator does not yet meet task prerequisites
    assert not await operator.meets_task_prerequisites()

    # Add two Agency suggestions
    for i in range(2):
        await db_data_creator.agency_user_suggestions(
            url_id=url_id,
            user_id=i,
            agency_annotation_info=URLAgencyAnnotationPostInfo(
                suggested_agency=agency_id
            )
        )

    # Assert operator does not yet meet task prerequisites
    assert not await operator.meets_task_prerequisites()

    # Add two location suggestions
    for i in range(2):
        await db_data_creator.add_user_location_suggestion(
            url_id=url_id,
            user_id=i,
            location_id=pittsburgh_locality.location_id,
        )

    # Assert operator now meets task prerequisites
    assert await operator.meets_task_prerequisites()

    raise NotImplementedError('Finish test')



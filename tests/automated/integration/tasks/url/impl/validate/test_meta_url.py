"""
Add a URL with two of the same suggestions for each of the following:
- Agency
- Location
- URL Type (META URL)
And confirm it is validated as META URL
"""
import pytest

from src.core.tasks.url.operators.validate.core import AutoValidateURLTaskOperator
from src.db.models.impl.flag.url_validated.enums import URLType
from tests.automated.integration.tasks.url.impl.validate.helper import TestValidateTaskHelper
from tests.helpers.data_creator.models.creation_info.county import CountyCreationInfo
from tests.helpers.run import run_task_and_confirm_success


@pytest.mark.asyncio
async def test_meta_url(
    operator: AutoValidateURLTaskOperator,
    helper: TestValidateTaskHelper,
    allegheny_county: CountyCreationInfo
):
    # Add two META URL suggestions
    await helper.add_url_type_suggestions(URLType.META_URL, count=2)

    # Assert operator does not yet meet task prerequisites
    assert not await operator.meets_task_prerequisites()

    # Add two Agency suggestions
    await helper.add_agency_suggestions(count=2)

    # Assert operator does not yet meet task prerequisites
    assert not await operator.meets_task_prerequisites()

    # Add two location suggestions
    await helper.add_location_suggestions(count=2)

    # Assert operator now meets task prerequisites
    assert await operator.meets_task_prerequisites()

    # Add additional two location suggestions for different location
    await helper.add_location_suggestions(
        count=2,
        location_id=allegheny_county.location_id
    )

    # Assert operator no longer meets task prerequisites
    assert not await operator.meets_task_prerequisites()

    # Add additional location suggestion as tiebreaker
    await helper.add_location_suggestions()

    # Assert operator again meets task prerequisites
    assert await operator.meets_task_prerequisites()

    await run_task_and_confirm_success(operator)

    await helper.check_url_validated(URLType.META_URL)
    await helper.check_auto_validated()
    await helper.check_agency_linked()

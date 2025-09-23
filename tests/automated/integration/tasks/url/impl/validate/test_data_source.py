"""
Add a URL with two of the same suggestions for each of the following:
- Agency
- Location
- Record Type
- URL Type (DATA SOURCE)
And confirm it is validated as DATA SOURCE
"""
import pytest

from src.core.enums import RecordType
from src.core.tasks.url.operators.validate.core import AutoValidateURLTaskOperator
from src.db.models.impl.flag.url_validated.enums import URLType
from tests.automated.integration.tasks.url.impl.validate.helper import TestValidateTaskHelper
from tests.helpers.run import run_task_and_confirm_success


@pytest.mark.asyncio
async def test_data_source(
    operator: AutoValidateURLTaskOperator,
    helper: TestValidateTaskHelper
):
    await helper.add_url_type_suggestions(
        url_type=URLType.DATA_SOURCE,
        count=2
    )

    assert not await operator.meets_task_prerequisites()

    await helper.add_agency_suggestions(count=2)

    assert not await operator.meets_task_prerequisites()

    await helper.add_location_suggestions(count=2)

    assert not await operator.meets_task_prerequisites()

    await helper.add_record_type_suggestions(count=2)

    assert await operator.meets_task_prerequisites()

    # Add different record type suggestion
    await helper.add_record_type_suggestions(
        count=2,
        record_type=RecordType.STOPS
    )

    # Assert no longer meets task prerequisites
    assert not await operator.meets_task_prerequisites()

    # Add tiebreaker
    await helper.add_record_type_suggestions()

    assert await operator.meets_task_prerequisites()

    await run_task_and_confirm_success(operator)

    await helper.check_url_validated(URLType.DATA_SOURCE)
    await helper.check_auto_validated()
    await helper.check_agency_linked()
    await helper.check_record_type()


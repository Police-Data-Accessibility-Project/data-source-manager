# TODO: Add URL with 2 INDIVIDUAL RECORD suggestions. Check validated as INDIVIDUAL RECORD
import pytest

from src.core.tasks.url.operators.validate.core import AutoValidateURLTaskOperator
from src.db.models.impl.flag.url_validated.enums import URLType
from tests.automated.integration.tasks.url.impl.validate.helper import TestValidateTaskHelper
from tests.helpers.data_creator.core import DBDataCreator
from tests.helpers.run import run_task_and_confirm_success


@pytest.mark.asyncio
async def test_individual_record(
    operator: AutoValidateURLTaskOperator,
    helper: TestValidateTaskHelper
):
    # Add two INDIVIDUAL record suggestions
    await helper.add_url_type_suggestions(
        url_type=URLType.INDIVIDUAL_RECORD,
        count=2
    )

    assert not await operator.meets_task_prerequisites()

    await helper.add_agency_suggestions(count=2)

    assert not await operator.meets_task_prerequisites()

    await helper.add_location_suggestions(count=2)

    assert await operator.meets_task_prerequisites()

    # Add additional agency suggestions to create tie
    additional_agency_id: int = await helper.db_data_creator.agency()
    await helper.add_agency_suggestions(
        count=2,
        agency_id=additional_agency_id
    )

    # Confirm no longer meets task prerequisites
    assert not await operator.meets_task_prerequisites()

    # Add tiebreaker suggestion
    await helper.add_agency_suggestions()

    assert await operator.meets_task_prerequisites()

    await run_task_and_confirm_success(operator)

    await helper.check_url_validated(URLType.INDIVIDUAL_RECORD)
    await helper.check_auto_validated()
    await helper.check_agency_linked()


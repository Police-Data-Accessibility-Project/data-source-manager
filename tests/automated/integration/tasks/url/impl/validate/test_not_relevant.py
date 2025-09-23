import pytest

from src.core.tasks.url.operators.validate.core import AutoValidateURLTaskOperator
from src.db.models.impl.flag.url_validated.enums import URLType
from tests.automated.integration.tasks.url.impl.validate.helper import TestValidateTaskHelper
from tests.helpers.run import run_task_and_confirm_success


@pytest.mark.asyncio
async def test_not_relevant(
    operator: AutoValidateURLTaskOperator,
    helper: TestValidateTaskHelper
):
    """
    Add URL with 2 NOT RELEVANT suggestions. Check validated as NOT RELEVANT
    """

    # Assert operator does not yet meet task prerequisites
    assert not await operator.meets_task_prerequisites()

    # Add one NOT RELEVANT suggestion
    await helper.add_url_type_suggestions(
        url_type=URLType.NOT_RELEVANT,
    )

    # Assert operator does not yet meet task prerequisites
    assert not await operator.meets_task_prerequisites()

    # Add second NOT RELEVANT suggestion
    await helper.add_url_type_suggestions(
        url_type=URLType.NOT_RELEVANT,
    )

    # Assert operator now meets task prerequisites
    assert await operator.meets_task_prerequisites()

    # Add different suggestion to create tie
    await helper.add_url_type_suggestions(
        url_type=URLType.META_URL,
        count=2
    )
    assert not await operator.meets_task_prerequisites()

    # Add tiebreaker
    await helper.add_url_type_suggestions(
        url_type=URLType.NOT_RELEVANT
    )

    await run_task_and_confirm_success(operator)

    # Assert URL validated as NOT RELEVANT
    await helper.check_url_validated(
        url_type=URLType.NOT_RELEVANT,
    )

    await helper.check_auto_validated()

# TODO: Add URL with 2 NOT RELEVANT suggestions. Check validated as NOT RELEVANT
import pytest

from src.core.tasks.url.operators.validate.core import AutoValidateURLTaskOperator
from src.db.models.impl.flag.url_validated.enums import URLType
from tests.helpers.data_creator.core import DBDataCreator
from tests.helpers.run import run_task_and_confirm_success


@pytest.mark.asyncio
async def test_not_relevant(
    operator: AutoValidateURLTaskOperator,
    db_data_creator: DBDataCreator,
):
    # Assert operator does not yet meet task prerequisites
    assert not await operator.meets_task_prerequisites()

    # Add one URL
    url_id: int = (await db_data_creator.create_urls(count=1))[0].url_id

    # Assert operator does not yet meet task prerequisites
    assert not await operator.meets_task_prerequisites()

    # Add one NOT RELEVANT suggestion
    await db_data_creator.user_relevant_suggestion(
        suggested_status=URLType.NOT_RELEVANT,
        url_id=url_id,
        user_id=1,
    )

    # Assert operator does not yet meet task prerequisites
    assert not await operator.meets_task_prerequisites()

    # Add second NOT RELEVANT suggestion
    await db_data_creator.user_relevant_suggestion(
        suggested_status=URLType.NOT_RELEVANT,
        url_id=url_id,
        user_id=2,
    )

    # Assert operator now meets task prerequisites
    assert await operator.meets_task_prerequisites()

    await run_task_and_confirm_success(operator)
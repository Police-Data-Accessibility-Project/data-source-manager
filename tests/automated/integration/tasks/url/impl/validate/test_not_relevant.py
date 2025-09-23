import pytest

from src.core.tasks.url.operators.validate.core import AutoValidateURLTaskOperator
from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.flag.auto_validated.sqlalchemy import FlagURLAutoValidated
from src.db.models.impl.flag.url_validated.enums import URLType
from src.db.models.impl.flag.url_validated.sqlalchemy import FlagURLValidated
from tests.helpers.data_creator.core import DBDataCreator
from tests.helpers.run import run_task_and_confirm_success


@pytest.mark.asyncio
async def test_not_relevant(
    operator: AutoValidateURLTaskOperator,
    db_data_creator: DBDataCreator,
):
    """
    Add URL with 2 NOT RELEVANT suggestions. Check validated as NOT RELEVANT
    """
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

    # Assert URL validated as NOT RELEVANT
    adb_client: AsyncDatabaseClient = operator.adb_client
    validated_flags: list[FlagURLValidated] = await adb_client.get_all(FlagURLValidated)
    assert len(validated_flags) == 1
    validated_flag: FlagURLValidated = validated_flags[0]
    assert validated_flag.url_id == url_id
    assert validated_flag.type == URLType.NOT_RELEVANT

    # Assert flagged as auto validated
    auto_validated_flags: list[FlagURLAutoValidated] = await adb_client.get_all(FlagURLAutoValidated)
    assert len(auto_validated_flags) == 1
    auto_validated_flag: FlagURLAutoValidated = auto_validated_flags[0]
    assert auto_validated_flag.url_id == url_id
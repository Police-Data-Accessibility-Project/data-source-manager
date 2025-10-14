from collections import Counter

import pytest

from src.collectors.enums import URLStatus
from src.core.tasks.url.operators.auto_relevant.core import URLAutoRelevantTaskOperator
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.suggestion.relevant.auto.sqlalchemy import AutoRelevantSuggestion
from src.db.models.impl.url.task_error.sqlalchemy import URLTaskError
from tests.automated.integration.tasks.url.impl.asserts import assert_prereqs_not_met, assert_prereqs_met
from tests.automated.integration.tasks.url.impl.auto_relevant.setup import setup_operator, setup_urls
from tests.helpers.asserts import assert_task_run_success
from tests.helpers.data_creator.core import DBDataCreator


@pytest.mark.asyncio
async def test_url_auto_relevant_task(db_data_creator: DBDataCreator):

    operator: URLAutoRelevantTaskOperator = await setup_operator(adb_client=db_data_creator.adb_client)
    await assert_prereqs_not_met(operator)

    url_ids = await setup_urls(db_data_creator)
    await assert_prereqs_met(operator)

    run_info = await operator.run_task()

    assert_task_run_success(run_info)

    assert not await operator.meets_task_prerequisites()

    adb_client = db_data_creator.adb_client

    # Confirm two annotations were created
    suggestions: list[AutoRelevantSuggestion] = await adb_client.get_all(AutoRelevantSuggestion)
    assert len(suggestions) == 2
    for suggestion in suggestions:
        assert suggestion.url_id in url_ids
        assert suggestion.relevant is not None
        assert suggestion.confidence == 0.5
        assert suggestion.model_name == "test_model"

    # Confirm presence of url error
    errors = await adb_client.get_all(URLTaskError)
    assert len(errors) == 1



